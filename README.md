# verbatim-anonymization

Utility to automatically anonymize survey responses
using [SpaCy](https://spacy.io/) and Regex

## Setup

### Prerequisites (local)

* Python version >=3.6
* Python pip (usually comes with your Python installation)

### Prerequisites (docker)

* Docker (https://docs.docker.com/get-docker/)

### Installation (local)

`pip3 install -r requirements.txt`

### Installation (docker)

## Usage

To anonymize a file stored at path `${IN_PATH}` with text column(s) `${TEXT_COLS}` using the default settings, execute

```python3 -m verbatim_anonymizer.anonymize_verbatim_file ${IN_PATH} ${OUT_PATH} ${TEXT_COLUMNS}```

(set `${OUT_PATH}` to the path where the anonymized file should be written to).
If your file has multiple text columns to analyze, set `${TEXT_COLUMNS}` to be a list of text columns separated by
spaces and surrounded by apostrophes, for example:

```python3 -m verbatim_anonymizer.anonymize_verbatim_file ${IN_PATH} ${OUT_PATH} "Text_1 Text_2""```

(Column names are expected to not contain any spaces).

For optimal performance of the entity recognition (names, organizations etc.) we recommend setting the
_language_ py also passing the argument `--language` with the appropriate language. For more languages or different models
please consult the spacy documentation: https://spacy.io/models/en

To see the full list of options available, execute
```python3 -m verbatim_anonymizer.anonymize_verbatim_file -h```


## Tests
To execute the tests, install pytest using
```
pip install pytest
```
and then run
```
python -m pytest tests/
```
