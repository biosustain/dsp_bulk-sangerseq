"""Post-process tracy decompose JSON results into consolidated report tables.

Relevant variant results are extracted from each tracy ``decompose`` JSON output
and consolidated into per-sample CSV tables plus a single combined table. This is
the Nextflow-adapted port of the standalone ``tracy_postprocesssing.py`` script;
it takes explicit input/output paths instead of reading ``config.yaml`` and does
not perform the electropherogram plotting done by the legacy script.
"""

import argparse
import csv
import json
from pathlib import Path

# Variant columns as emitted by tracy decompose, framed by the derived sample
# name and the computed editing-success flag. This ordering matches the reference
# output produced by the original pandas-based script.
VARIANT_COLUMNS = [
    'chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter',
    'type', 'genotype', 'basepos', 'signalpos',
]
OUTPUT_COLUMNS = ['sample_name'] + VARIANT_COLUMNS + ['successfully_edited']


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
    return parser.parse_args()


def extract_sample_rows(json_path: Path):
    """Return (sample_name, list-of-row-dicts) for a single decompose JSON file."""
    with json_path.open(encoding='utf-8') as handle:
        data = json.load(handle)

    # Derive the sample name from the original input filename, e.g. 'sample_1.abi'
    # -> 'sample_1', matching the legacy script's naming.
    sample_name = data['meta']['arguments']['input'].split('.')[0]

    columns = data['variants']['columns']
    variant_rows = [dict(zip(columns, values)) for values in data['variants']['rows']]

    # No detected mutations: emit a single empty row so the sample still appears in
    # the combined table (mirrors the NaN placeholder row of the pandas version).
    if not variant_rows:
        variant_rows = [{column: None for column in VARIANT_COLUMNS}]

    rows = []
    for variant in variant_rows:
        row = {'sample_name': sample_name}
        for column in VARIANT_COLUMNS:
            row[column] = variant.get(column)
        # A missing alternative allele indicates a successful edit. Note this logic
        # only holds when aligning against the edited reference sequence.
        row['successfully_edited'] = row['alt'] is None
        rows.append(row)

    return sample_name, rows


def write_csv(path: Path, rows) -> None:
    with path.open('w', newline='', encoding='utf-8') as handle:
        # lineterminator='\n' reproduces the pandas to_csv output byte-for-byte.
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS, lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format(row[column]) for column in OUTPUT_COLUMNS})


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
        (extract_sample_rows(Path(json_path)) for json_path in args.json_paths),
        key=lambda item: item[0],
    )

    combined_rows = []
    for sample_name, rows in samples:
        write_csv(outdir / f'{sample_name}.csv', rows)
        combined_rows.extend(rows)

    write_csv(outdir / args.combined_name, combined_rows)


if __name__ == '__main__':
    main()
