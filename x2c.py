#! /usr/bin/python3
# -*- encoding: utf-8 -*-
"""XMI2CONLL CLI entry point
"""
import sys

import click
import pyfiglet

from src.cli_utils import timing
from src.x2c_converters import Xmi2Conll


@click.command()
@click.argument('input_xmi',
                nargs=1)
@click.argument('typesystem',
                nargs=1)
@click.option('-o',
              '--output',
              default='./output/',
              show_default=True,
              help="output path that contains new conll.",
              required=False,
              type=str)
@click.option('-tn',
              '--type_name_annotations',
              default='de.tudarmstadt.ukp.dkpro.core.api.ner.type.NamedEntity',
              show_default=True,
              help="type name of the annotations",
              required=False,
              type=str)
@click.option('-s',
              '--conll_separator',
              default="space",
              show_default=True,
              help="Defines a separator in CONLL between mention and label; only 'space' or 'tab' are accepted",
              required=False,
              type=str)
@click.option('-h',
              '--header',
              default=True,
              show_default=True,
              help="show or hide title of CLI",
              required=False,
              type=bool)
@timing
def main(input_xmi: str,
         typesystem: str,
         output: str,
         type_name_annotations: str,
         conll_separator: str,
         header: bool) -> None:
    """XMI to CONLL Converter CLI © 2022 - @Lucaterre

    INPUT_XMI (str): XMI file path or directory path that contains XMI for batch processing.\n
    TYPESYSTEM (str): Typesystem.xml path.
    """
    # Create a CLI header
    if header:
        ascii_logo = pyfiglet.figlet_format("|* XMI2CONLL *|")
        print(ascii_logo)
        print("© 2022 - @Lucaterre")
    # Run conversion process
    Xmi2Conll(
        xmi=input_xmi,
        typesystem_input=typesystem,
        type_name_annotations=type_name_annotations,
        output=output,
        sep=conll_separator
    )


if __name__ == '__main__':
    main()
