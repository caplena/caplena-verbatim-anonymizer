"""
Script for configurable anonymization flow on tabular data
"""
import argparse
import pandas as pd
from typing import List, Callable

from verbatim_anonymizer.anonmization_steps import (
    AnonymizerSteps,
    DEFAULT_ANONYMIZATION_PIPELINE,
    Languages,
    EntityAnonymizerStep,
)


def anonymize_verbatim(
    verbatim: str, anonymizationsteps: List[Callable]
) -> str:
    for step in anonymizationsteps:
        verbatim = step(verbatim)
    return verbatim


parser = argparse.ArgumentParser(
    "Tool to anonymize verbatims from tabular files (CSV or XLS/XLSX)"
)
parser.add_argument("in_path", type=str, help="Path to a CSV or XLS/XLSX file")
parser.add_argument(
    "out_path", type=str, help="Path to write anonymized file to"
)
parser.add_argument(
    "text_columns",
    nargs="*",
    help="Columns with verbatims to anonymize, separated by space, i.e. 'Text_1 Text_2' ",
)
parser.add_argument(
    "--steps",
    nargs="*",
    choices=[el.name for el in AnonymizerSteps],
    help="Anonymization steps to carry out in sequence",
    default=[el.name for el in DEFAULT_ANONYMIZATION_PIPELINE],
)
parser.add_argument(
    "--delimiter",
    type=str,
    default=",",
    help="Delimiter used in the tabular file. Only applies to CSV",
)
parser.add_argument(
    "--language",
    choices=[lang for lang in Languages],
    default=Languages.en,
    help="Language of the verbatims (only relevant for anonymizing named entities like names, organizations etc.)",
)

if __name__ == "__main__":
    args = parser.parse_args()
    anonymization_steps = []
    for step in args.steps:
        an_step = AnonymizerSteps[step]
        if isinstance(an_step.value, EntityAnonymizerStep):
            an_step.value.language = args.language
        anonymization_steps.append(an_step)
    if args.in_path.endswith(".csv"):
        try:
            df = pd.read_csv(args.in_path, sep=args.delimiter)
            is_csv = True
        except Exception as e:
            raise ValueError(
                "Unable to read CSV file, verify the contents and make sure you set "
                "--delimiter correctly. Original Exception: {}".format(str(e))
            )
    elif args.in_path.endswith(".xls") or args.in_path.endswith(".xlsx"):
        try:
            df = pd.read_excel(args.in_path)
        except Exception:
            raise ValueError(
                "Unable to read Excel file, verify contents, save again in Excel and try again"
            )
    else:
        raise ValueError(
            "Invalid file extension, supply either .csv or .xls/.xlsx"
        )
    for col in args.text_columns:
        if col not in df.columns:
            raise ValueError(
                "Supplied text column {} couldn't be found in supplied file".format(
                    col
                )
            )
        df[col] = df[col].apply(anonymize_verbatim, args=[anonymization_steps])
    if args.out_path.endswith(".csv"):
        df.to_csv(args.out_path, sep=args.delimiter, index=None)
    else:
        df.to_excel(args.out_path, index=None)
    print(
        "Successfully anonymized file, wrote output to {}".format(
            args.out_path
        )
    )
