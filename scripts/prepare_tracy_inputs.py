import argparse
import csv
from collections import defaultdict
from pathlib import Path


REQUIRED_COLUMNS = {'sample_id', 'ab1_file', 'assembly_group', 'reference_id'}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--samplesheet', required=True)
    parser.add_argument('--reference-fasta', required=True)
    parser.add_argument('--data-dir', required=True)
    parser.add_argument('--samples-output', required=True)
    parser.add_argument('--assemblies-output', required=True)
    parser.add_argument('--reference-dir', required=True)
    return parser.parse_args()


def parse_fasta(fasta_path: Path):
    header = None
    chunks = []

    with fasta_path.open(encoding='utf-8') as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith('>'):
                if header is not None:
                    yield header, ''.join(chunks)
                header = line[1:].split()[0]
                chunks = []
                continue

            chunks.append(line)

    if header is not None:
        yield header, ''.join(chunks)


def resolve_ab1_path(data_dir: Path, ab1_value: str) -> Path:
    candidate = Path(ab1_value)
    if not candidate.is_absolute():
        candidate = data_dir / candidate
    return candidate.resolve()


def main() -> None:
    args = parse_args()

    samplesheet_path = Path(args.samplesheet).resolve()
    reference_fasta_path = Path(args.reference_fasta).resolve()
    data_dir = Path(args.data_dir).resolve()
    samples_output = Path(args.samples_output)
    assemblies_output = Path(args.assemblies_output)
    reference_dir = Path(args.reference_dir)

    if not samplesheet_path.exists():
        raise FileNotFoundError(f'Samplesheet not found: {samplesheet_path}')

    if not reference_fasta_path.exists():
        raise FileNotFoundError(f'Reference FASTA not found: {reference_fasta_path}')

    if not data_dir.exists():
        raise FileNotFoundError(f'Data directory not found: {data_dir}')

    with samplesheet_path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        missing_columns = REQUIRED_COLUMNS.difference(reader.fieldnames or [])
        if missing_columns:
            raise ValueError(
                'Samplesheet is missing required columns: '
                + ', '.join(sorted(missing_columns))
            )

        sample_rows = []
        assembly_groups = defaultdict(list)

        for row in reader:
            sample_id = (row['sample_id'] or '').strip()
            ab1_file = (row['ab1_file'] or '').strip()
            assembly_group = (row['assembly_group'] or '').strip()
            reference_id = (row['reference_id'] or '').strip()

            if not sample_id or not ab1_file or not reference_id:
                raise ValueError(f'Invalid samplesheet row: {row}')

            ab1_path = resolve_ab1_path(data_dir, ab1_file)
            if not ab1_path.exists():
                raise FileNotFoundError(f'Sequencing file not found: {ab1_path}')

            normalized_row = {
                'sample_id': sample_id,
                'ab1_path': str(ab1_path),
                'assembly_group': assembly_group,
                'reference_id': reference_id,
            }
            sample_rows.append(normalized_row)

            if assembly_group:
                assembly_groups[assembly_group].append(normalized_row)

    requested_reference_ids = sorted({row['reference_id'] for row in sample_rows})
    requested_reference_set = set(requested_reference_ids)

    reference_dir.mkdir(parents=True, exist_ok=True)
    extracted_reference_ids = set()
    for reference_id, sequence in parse_fasta(reference_fasta_path):
        if reference_id not in requested_reference_set:
            continue

        extracted_reference_ids.add(reference_id)
        reference_path = reference_dir / f'{reference_id}.fa'
        reference_path.write_text(f'>{reference_id}\n{sequence}\n', encoding='utf-8')

    missing_reference_ids = requested_reference_set.difference(extracted_reference_ids)
    if missing_reference_ids:
        raise ValueError(
            'Missing reference sequences in FASTA: '
            + ', '.join(sorted(missing_reference_ids))
        )

    with samples_output.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=['sample_id', 'ab1_path', 'assembly_group', 'reference_id'],
            delimiter='\t',
        )
        writer.writeheader()
        writer.writerows(sample_rows)

    with assemblies_output.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=['assembly_group', 'reference_id', 'sample_id_joined', 'ab1_paths'],
            delimiter='\t',
        )
        writer.writeheader()

        for assembly_group in sorted(assembly_groups):
            grouped_rows = assembly_groups[assembly_group]
            reference_ids = {row['reference_id'] for row in grouped_rows}
            if len(reference_ids) != 1:
                raise ValueError(
                    f'Assembly group {assembly_group} uses multiple reference IDs: '
                    + ', '.join(sorted(reference_ids))
                )

            writer.writerow(
                {
                    'assembly_group': assembly_group,
                    'reference_id': grouped_rows[0]['reference_id'],
                    'sample_id_joined': '_'.join(row['sample_id'] for row in grouped_rows),
                    'ab1_paths': ';'.join(row['ab1_path'] for row in grouped_rows),
                }
            )


if __name__ == '__main__':
    main()
