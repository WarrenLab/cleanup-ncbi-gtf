"""
Clean up an NCBI-style GTF file so that it is compatible with
CellRanger.
"""
import argparse
from functools import partial
import sys

import gffutils


def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "input_gtf",
        type=partial(
            gffutils.create_db,
            dbfn=":memory:",
            id_spec={"gene": "gene_id", "transcript": "transcript_id"},
            transform=transform_record,
            disable_infer_genes=True,
            disable_infer_transcripts=True,
        ),
    )
    return parser.parse_args()


def transform_record(
    record: gffutils.Feature,
    allowed_attributes: list[str] = [
        "gene_id",
        "transcript_id",
        "transcript_biotype",
        "gene",
        "exon_number",
    ],
) -> gffutils.Feature:
    """Change a record to be parseable by CellRanger

    Change a record to be parseable by CellRanger by making the
    following changes:
    * Remove attributes whose keys are not in the list of allowed keys
    * Add a "gene_name" attribute that mirrors the "gene" attribute, as
      "gene_name" is where CellRanger looks for the gene symbol

    Arguments:
        record: a Feature object to transform
        allowed_attributes: a list of attribute to allow in the output

    Returns:
        an edited version of the input record
    """
    keys_to_delete = set(record.attributes.keys()) - set(allowed_attributes)
    for key in keys_to_delete:
        del record.attributes[key]
    if "gene" in record.attributes:
        record.attributes["gene_name"] = record.attributes["gene"]

    return record


def main():
    """Main method of program"""
    args = parse_args()
    for record in args.input_gtf.all_features():
        print(record)


if __name__ == "__main__":
    main()
