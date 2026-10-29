#!/usr/bin/env python3
"""Post-process tracy decompose JSON results into consolidated report tables.

Relevant variant results are extracted from each tracy ``decompose`` JSON output
and consolidated into per-sample CSV tables plus a single combined table. The
script takes explicit input/output paths (the files Nextflow has staged into the
task work directory) and does not perform electropherogram plotting.

When an Indigo viewer base URL is supplied, each row also carries a link to the
sample's published Indigo visualisation, pointing at the variant of that row.
"""

import argparse
import csv
import json
from pathlib import Path
from urllib.parse import urlencode

# Variant columns as emitted by tracy decompose, framed by the derived sample
# name and the computed editing-success flag. This ordering matches the reference
# output produced by the original pandas-based script.
VARIANT_COLUMNS = [
    'chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter',
    'type', 'genotype', 'basepos', 'signalpos',
]
OUTPUT_COLUMNS = ['sample_name'] + VARIANT_COLUMNS + ['successfully_edited']

# Appended to OUTPUT_COLUMNS only when an Indigo viewer base URL is configured,
# so a run without one keeps producing the tables in their original shape.
INDIGO_LINK_COLUMN = 'indigo_visualisation'

# Query parameter the Indigo viewer takes the variant to show from. It is named
# after the id of the viewer's variants-table element, so this has to match the
# indigo template in biosustain/tracy-visualisations.
INDIGO_VARIANT_PARAM = 'variants-table'


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--json', required=True, nargs='+', dest='json_paths',
        help='One or more tracy decompose JSON result files.',
    )
    parser.add_argument(
        '--outdir', default='.', dest='outdir',
        help='Directory to write the per-sample and combined CSV tables into.',
    )
    parser.add_argument(
        '--combined-name', default='results_combined.csv', dest='combined_name',
        help='Filename for the combined results table.',
    )
    parser.add_argument(
        '--indigo-link-base', default=None, dest='indigo_link_base',
        help=(
            'Base URL of the directory holding the published Indigo viewers '
            '(e.g. file:///data/results/decompose). When given, a '
            f'{INDIGO_LINK_COLUMN!r} column linking each mutation to its '
            'position in the electropherogram is added to the tables.'
        ),
    )
    return parser.parse_args()


def output_columns(indigo_link_base):
    """Return the CSV columns to write for the given link configuration."""
    if not indigo_link_base:
        return OUTPUT_COLUMNS
    return OUTPUT_COLUMNS + [INDIGO_LINK_COLUMN]


def indigo_viewer_url(indigo_link_base, viewer_name, variant_index):
    """Return the link to a sample's Indigo viewer, focused on one variant.

    ``variant_index`` is the 0-based row index of the variant within the tracy
    decompose JSON; the viewer reads it back from the URL query and scrolls to
    that position in the electropherogram. ``None`` (a sample with no detected
    mutations) links to the viewer as a whole.
    """
    url = f'{indigo_link_base.rstrip("/")}/{viewer_name}.html'
    if variant_index is None:
        return url
    return f'{url}?{urlencode({INDIGO_VARIANT_PARAM: variant_index})}'


def extract_sample_rows(json_path: Path, indigo_link_base=None):
    """Return (sample_name, list-of-row-dicts) for a single decompose JSON file."""
    with json_path.open(encoding='utf-8') as handle:
        data = json.load(handle)

    # Derive the sample name from the original input filename, e.g. 'sample_1.abi'
    # -> 'sample_1', matching the legacy script's naming.
    sample_name = data['meta']['arguments']['input'].split('.')[0]

    # The published Indigo viewer is named after the pipeline's sample id, and so
    # is this JSON file. That is not always the same as `sample_name`, which
    # mirrors the raw trace filename from the samplesheet.
    viewer_name = json_path.stem

    columns = data['variants']['columns']
    variant_rows = [dict(zip(columns, values)) for values in data['variants']['rows']]
    variant_indices = list(range(len(variant_rows)))

    # No detected mutations: emit a single empty row so the sample still appears in
    # the combined table (mirrors the NaN placeholder row of the pandas version).
    # There is no variant for it to link to, only the viewer as a whole.
    if not variant_rows:
        variant_rows = [{column: None for column in VARIANT_COLUMNS}]
        variant_indices = [None]

    rows = []
    for variant_index, variant in zip(variant_indices, variant_rows):
        row = {'sample_name': sample_name}
        for column in VARIANT_COLUMNS:
            row[column] = variant.get(column)
        # A missing alternative allele indicates a successful edit. Note this logic
        # only holds when aligning against the edited reference sequence.
        row['successfully_edited'] = row['alt'] is None
        if indigo_link_base:
            row[INDIGO_LINK_COLUMN] = indigo_viewer_url(
                indigo_link_base, viewer_name, variant_index
            )
        rows.append(row)

    return sample_name, rows


def write_csv(path: Path, rows, columns) -> None:
    with path.open('w', newline='', encoding='utf-8') as handle:
        # lineterminator='\n' reproduces the pandas to_csv output byte-for-byte.
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format(row[column]) for column in columns})


def _format(value):
    # None -> empty field (as pandas writes NaN); everything else stringified as-is.
    return '' if value is None else value


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Sort by sample name for deterministic combined-table ordering, independent of
    # the (unordered) order in which Nextflow stages the input files.
    samples = sorted(
        (
            extract_sample_rows(Path(json_path), args.indigo_link_base)
            for json_path in args.json_paths
        ),
        key=lambda item: item[0],
    )

    columns = output_columns(args.indigo_link_base)

    combined_rows = []
    for sample_name, rows in samples:
        write_csv(outdir / f'{sample_name}.csv', rows, columns)
        combined_rows.extend(rows)

    write_csv(outdir / args.combined_name, combined_rows, columns)


if __name__ == '__main__':
    main()
