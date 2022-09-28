# xmi2conll CLI

![Python Version](https://img.shields.io/badge/Python-%3E%3D%203.8-%2313aab7) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![PyPI version](https://badge.fury.io/py/xmi2conll.svg)](https://badge.fury.io/py/xmi2conll)

![logo](./docs/x2c_logo.png)

Simple CLI to convert any annotated document in UIMA CAS XMI to CONLL format (IOB schema support).

### Installation:

Start by create and activate a new environnement with virtualenv : 

```bash
virtualenv --python=/usr/bin/python3.8 venv
source venv/bin/activate
```

then choose:

- Easy way (use pip):

```bash
pip install xmi2conll
```

- Dev install:

```bash
git clone https://github.com/Lucaterre/xmi2conll
pip install -r requirements.txt
```


### Usage:

with pip install run:
```bash
x2c --help
```

or with dev install run:
```bash
python x2c.py --help
```

```
Usage: x2c.py [OPTIONS] INPUT_XMI TYPESYSTEM

  XMI to CONLL Converter CLI © 2022 - @Lucaterre

  INPUT_XMI (str): XMI file path or directory path that contains XMI for batch
  processing.

  TYPESYSTEM (str): Typesystem.xml path.

Options:
  -o, --output TEXT               output path that contains new conll, 
                                  if it not specify ./output/ is auto created.
                                  [default: ./output/]
  -tn, --type_name_annotations TEXT
                                  type name of the annotations  [default: de.t
                                  udarmstadt.ukp.dkpro.core.api.ner.type.Named
                                  Entity]
  -s, --conll_separator TEXT      Defines a separator in CONLL between mention
                                  and label; only 'space' or 'tab' are accepted [default:
                                  space]
  -h, --header BOOLEAN            show or hide title of CLI  [default: True]
  --help                          Show this message and exit.

```

### Citation:

```
@misc{xmi2conll-cli,
    author = "Lucas Terriel",
    title = {xmi2conll, a cli to convert any annotated document in UIMA CAS XMI to CONLL format (IOB schema support)},
    howpublished = {\url{https://github.com/Lucaterre/xmi2conll}},
    year = {2022}
}
```

### License:

This tool is distributed under MIT license.
