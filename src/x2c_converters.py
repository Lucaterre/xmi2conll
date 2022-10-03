# -*- encoding: utf-8 -*-
"""xmi2conll class to convert XMI to CONLL format
"""
import os
import sys
from typing import Union

import pandas as pd
import numpy as np
from cassis import (load_cas_from_xmi,
                    load_typesystem,
                    typesystem,
                    cas)
import tqdm

from src.cli_utils import report_log


"""
def to_text_file(method):
    ""A decorator that write an output of method
    in text file.
    ""
    def out(*args):
        with open(file=f'{args[0].output}{args[0].actual_file}.conll',
                  mode='w',
                  encoding='UTF-8') as file:
            for line in method(args[0]):
                file.write(line)
    return out
"""


class Xmi2Conll:
    """
    Xmi2Conll ensure XMI conversion to Conll
    """
    def __init__(self,
                 xmi: str = None,
                 typesystem_input: str = None,
                 type_name_annotations: str = None,
                 output: str = "./output/",
                 sep: str = "space") -> None:

        if sep == "space":
            self.conll_sep = " "
        elif sep == "tab":
            self.conll_sep = "\t"
        else:
            self.conll_sep = " "
            report_log(f"separator: {sep} is not a valid value (only 'space' or 'tab' is accept). Your sep is replace with 'space'.", type_log='W')

        # 1. read & check typesystem
        if typesystem_input is not None:
            self._typesystem = self.open_typesystem(typesystem_input)
            if self._typesystem is None:
                sys.exit()

        # 2. check if xmi input is directory or file and create a batch
        # to convert documents
        self._xmi = xmi
        self._batch_xmis = []
        if xmi is not None:
            if os.path.isfile(self._xmi):
                self._xmi = self.open_xmi(xmi, self._typesystem)
                self._batch_xmis.append((self.get_filename(xmi), self._xmi))
            elif os.path.isdir(self._xmi):
                if not self._xmi.endswith('/'):
                    self._xmi = f"{self._xmi}/"
                else:
                    self._xmi = self._xmi
                self._batch_xmis = [
                    (self.get_filename(xmi),
                     self.open_xmi(self._xmi+xmi, self._typesystem))
                    for xmi in os.listdir(self._xmi)
                ]
            else:
                report_log("Data input is not a path to a file or a directory", type_log="E")
                sys.exit()

        # 3. check if output exists else create a new output dir
        # or default "output/" in root work directory
        if not output.endswith('/'):
            self.output = f"{output}/"
        else:
            self.output = output
        if not os.path.exists(output):
            report_log(f'create a new {self.output} dir', type_log='I')
            os.makedirs(self.output)
        else:
            report_log(f'{self.output} dir already exists', type_log='I')

        self._type_name_annotations = type_name_annotations
        # coords_ne store all the offsets of known entities for a document
        # eg. {(start, end): "PERSON", (start, end): "LOCATION", (start, end): "PERSON" ...}
        self.coords_ne = {}
        self.chunk_prefix = {
            True: "B-",
            False: "I-",
            "default": "O"
        }
        self.actual_file = ""

        # 4. run batch process to convert XMI => CONLL
        for name, xmi in self._batch_xmis:
            self.actual_file = name
            self._xmi = xmi
            if self._xmi is not None:
                report_log(f"Convert {self.actual_file}.xmi "
                           f"to {self.actual_file}.conll in progress...", type_log='I')
                try:
                    self.coords_ne = self.build_coords()
                    self.mentions, self.labels = self.conversion_process()
                    self.fast_chunk_iob()
                    #self.conversion_process()
                    report_log(f"{self.actual_file}.conll => OK", type_log="S")
                except Exception as exception:
                    report_log(f"{self.actual_file}.conll => NOK : {exception}", type_log="E")

        report_log(f'All finish, Please check, new file(s) in {output} dir', type_log='I')

    @staticmethod
    def get_filename(path: str) -> str:
        """extract a filename from path without extension
        """
        return os.path.basename(os.path.splitext(path)[0])

    @staticmethod
    def open_typesystem(file: str) -> Union[typesystem.TypeSystem, None]:
        """check and load typesystem.xml
        """
        try:
            with open(file, 'rb') as type_sys_in:
                type_sys = load_typesystem(type_sys_in)
            report_log("Typesystem.xml is valid.", type_log="S")
            return type_sys
        except Exception as exception:
            report_log(f"Typesystem.xml is invalid, please check before rerun : {exception}", type_log="E")
            return None

    @staticmethod
    def open_xmi(file: str, typesystem_in: typesystem.TypeSystem) -> Union[cas.Cas, None]:
        """check and open xmi files to process
        """
        try:
            with open(file=file, mode='rb') as xmi_file:
                xmi = load_cas_from_xmi(xmi_file, typesystem=typesystem_in, lenient=False, trusted=True)
            report_log(f"{file} is valid.", type_log="S")
            return xmi
        except Exception as exception:
            report_log(f"{file} is invalid, please check : {exception}, It will "
                       f"not be taken into account during conversion process", type_log="E")
            return None

    @staticmethod
    def is_between(start: int,
                   end: int,
                   interval: tuple) -> bool:
        """A help method to check if token offset is in between known
        entities interval and return true if token is
        a part of entity
        """
        return start >= interval[0] and end <= interval[1]

    def label_categorizer(self,
                          interval_token: tuple,
                          interval_label: dict) -> list:
        """Search if token is a part of entity and returns
        correct label
        """
        return [
            value for k, value in interval_label.items()
            if self.is_between(interval_token[0],
                               interval_token[1],
                               k)
        ]

    def build_coords(self) -> dict:
        """Maps all offsets of know entities in
        document
        """
        return {
            (
                ne.get('begin'),
                ne.get('end')): ne.value for ne in self._xmi.select(self._type_name_annotations)
        }

    #@to_text_file
    def conversion_process(self) -> tuple:
        """Main process to retireve mentions and
        labels from XMI as sequences
        """
        # is_first = True
        mentions, labels = [], []
        # idx = 1
        # iterate over all sentences
        for sentence in tqdm.tqdm(
                self._xmi.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'),
                desc=f"processing sentences..."
        ):
            # iterate over all tokens
            for token in self._xmi.select_covered(
                    'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token',
                    sentence):
                # is token a part of named entity ?
                result_cat = self.label_categorizer(
                    (token.get('begin'), token.get('end')
                     ), self.coords_ne)
                # get textual value of token
                mention = token.get_covered_text()
                mentions.append(mention)
                if len(result_cat) > 0:
                    # if token is labeled entity
                    labels.append(result_cat[0])
                    """
                    if is_first:
                        # B- + label
                        yield f"{mention}{self.conll_sep}{self.chunk_prefix[is_first]}{result_cat[0]}\n"
                        is_first = False
                    else:
                        # I- + label
                        yield f"{mention}{self.conll_sep}{self.chunk_prefix[is_first]}{result_cat[0]}\n"
                    """
                else:
                    # if token is not an entity
                    labels.append("O")
                    # O + label
                    """
                    yield f"{mention}{self.conll_sep}{self.chunk_prefix['default']}\n"
                    is_first = True
                    """
            # new sentence
            #yield "\n"
            mentions.append("BREAK")
            labels.append("BREAK")
        return mentions, labels

    def fast_chunk_iob(self):
        """Chunk sequences of tokens with IOB schema
        """
        # initialize dataframe
        df = pd.DataFrame(list(zip(self.mentions, self.labels)), columns=[
            "mention", "label"
        ])

        # create mask to chunk with IOB:
        # label is not equal to 'BREAK'
        m_break = df['label'].ne('BREAK')
        # label is not equal to 'O'
        m1 = m_break & df['label'].ne('O')
        # label is not equal to 'O' and previous label equals to 'O'
        m2 = m1 & df['label'].shift().eq('O')
        # label is not equal to 'O' and next label is not equal to actual label
        m3 = m1 & (df['label'].shift(1) != df['label'])

        # apply masks
        df['label'] = np.select([m3, m2, m1], ['B-', 'B-', 'I-'], '') + df['label']

        # replace BREAK by empty values
        df = df.replace('BREAK', '')

        # generate an conll output
        df.to_csv(path_or_buf=f'{self.output}{self.actual_file}.conll',
                  encoding='utf-8',
                  sep=self.conll_sep,
                  index=False,
                  header=False)

        # clean empty values
        data_to_write = []
        with open(f'{self.output}{self.actual_file}.conll', mode="r", encoding='utf-8') as f_in:
            conll = f_in.read()
            for row in conll.splitlines():
                rs = row.split()
                if len(rs) == 0:
                    data_to_write.append('\n')
                else:
                    # case with breaking space
                    if len(rs) == 1:
                        data_to_write.append(f' {self.conll_sep}{rs[0]}\n')
                    else:
                        data_to_write.append(f'{rs[0]}{self.conll_sep}{rs[1]}\n')

        # write finalk output
        with open(f'{self.output}{self.actual_file}.conll', mode="w", encoding='utf-8') as f_out:
            for data in data_to_write:
                f_out.write(data)


