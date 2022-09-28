# -*- encoding: utf-8 -*-
"""
e"e"e
"""
import os
import sys
from typing import Union
from collections.abc import Generator

from cassis import (load_cas_from_xmi,
                    load_typesystem,
                    typesystem,
                    cas)
import tqdm

from src.cli_utils import report_log


def to_text_file(method):
    """A simple decorator that write an output of method
    in text file.
    """
    def out(*args):
        with open(file=f'{args[0].output}{args[0].actual_file}.conll',
                  mode='w',
                  encoding='UTF-8') as file:
            for line in method(args[0]):
                file.write(line)
    return out


class Xmi2Conll:
    """
    ded
    """
    def __init__(self,
                 xmi: str = None,
                 typesystem_input: str = None,
                 type_name_annotations: str = None,
                 output: str = "./output/",
                 sep: str = " ") -> None:

        self.conll_sep = sep

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
                    self.conversion_process()
                    report_log(f"{self.actual_file}.conll => OK", type_log="S")
                except Exception as exception:
                    report_log(f"{self.actual_file}.conll => NOK : {exception}", type_log="E")

        report_log(f'All finish, Please check, new file(s) in {output} dir', type_log='I')

    @staticmethod
    def get_filename(path: str) -> str:
        """

        :param path:
        :return:
        """
        return os.path.basename(os.path.splitext(path)[0])

    @staticmethod
    def open_typesystem(file: str) -> Union[typesystem.TypeSystem, None]:
        """

        :param file:
        :return:
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
        """gr
        """
        try:
            with open(file=file, mode='rb') as xmi_file:
                xmi = load_cas_from_xmi(xmi_file, typesystem=typesystem_in, lenient=False, trusted=True)
            report_log(f"{file} is valid.", type_log="S")
            print(type(xmi))
            return xmi
        except Exception as exception:
            report_log(f"{file} is invalid, please check : {exception}, It will "
                       f"not be taken into account during conversion process", type_log="E")
            return None

    @staticmethod
    def is_between(start: int,
                   end: int,
                   interval: tuple) -> bool:
        """

        :param start:
        :param end:
        :param interval:
        :return:
        """
        return start >= interval[0] and end <= interval[1]

    def label_categorizer(self,
                          interval_token: tuple,
                          interval_label: dict) -> list:
        """

        :param interval_token:
        :param interval_label:
        :return:
        """
        return [
            value for k, value in interval_label.items()
            if self.is_between(interval_token[0],
                               interval_token[1],
                               k)
        ]

    def build_coords(self) -> dict:
        """

        :return:
        """
        return {
            (
                ne.get('begin'),
                ne.get('end')): ne.value for ne in self._xmi.select(self._type_name_annotations)
        }

    @to_text_file
    def conversion_process(self) -> Generator:
        """

        :return:
        """
        is_first = True
        for sentence in tqdm.tqdm(
                self._xmi.select('de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Sentence'),
                desc=f"processing sentences..."
        ):
            for token in self._xmi.select_covered(
                    'de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.Token',
                    sentence):
                result_cat = self.label_categorizer(
                    (token.get('begin'), token.get('end')
                     ), self.coords_ne)
                mention = token.get_covered_text()
                if len(result_cat) > 0:
                    if is_first:
                        yield f"{mention}{self.conll_sep}{self.chunk_prefix[is_first]}{result_cat[0]}\n"
                        is_first = False
                    else:
                        yield f"{mention}{self.conll_sep}{self.chunk_prefix[is_first]}{result_cat[0]}\n"
                else:
                    yield f"{mention}{self.conll_sep}{self.chunk_prefix['default']}\n"
                    is_first = True

            yield "\n"
