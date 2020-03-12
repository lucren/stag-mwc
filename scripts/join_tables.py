#!/usr/bin/env python3
"""Join per sample feature tables into a large combined table."""
__author__ = "Fredrik Boulund"
__date__ = "2020"
__version__ = "1.0"

from sys import argv, exit
from functools import reduce, partial
from pathlib import Path
import argparse

import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("TABLE", nargs="+",
            help="TSV table with columns headers.")
    parser.add_argument("-f", "--feature-column", dest="feature_column",
            default="name",
            help="Column header of feature column to use, "
                 "typically containing taxa names. "
                 "Select several columns by separating with comma (e.g. name,taxid) "
                 "[%(default)s].")
    parser.add_argument("-c", "--value-column", dest="value_column",
            default="fraction_total_reads",
            help="Column header of value column to use, "
                 "typically containing counts or abundances [%(default)s].")
    parser.add_argument("-o", "--outfile", dest="outfile",
            default="joined_table.tsv",
            help="Outfile name [%(default)s].")
    parser.add_argument("-n", "--fillna", dest="fillna", metavar="FLOAT",
            default=0.0,
            type=float,
            help="Fill NA values in merged table with FLOAT [%(default)s].")

    return parser.parse_args()


def main(table_files, feature_column, value_column, outfile, fillna):
    feature_columns = feature_column.split(",")

    tables = []
    for table_file in table_files:
        sample_name = Path(table_file).name.split(".")[0]
        tables\
            .append(pd.read_csv(table_file, sep="\t")\
            .set_index(feature_columns)\
            .rename(columns={value_column: sample_name})\
            .loc[:, [sample_name]])  # Ugly hack to get a single-column DataFrame

    df = tables[0]
    if len(tables) > 1:
        for table in tables[1:]:
            df = df.join(table, how="outer")
    df.fillna(fillna, inplace=True)

    df.to_csv(outfile, sep="\t")


if __name__ == "__main__":
    args = parse_args()
    main(args.TABLE, args.feature_column, args.value_column, args.outfile, args.fillna)
