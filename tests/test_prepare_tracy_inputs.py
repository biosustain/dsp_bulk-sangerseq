import csv
import subprocess
import sys
from pathlib import Path


def run_prepare(
    samplesheet: Path,
    reference_fasta: Path,
    data_dir: Path,
    samples_out: Path,
    assemblies_out: Path,
    references_dir: Path,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "scripts/prepare_tracy_inputs.py",
            "--samplesheet",
            str(samplesheet),
            "--reference-fasta",
            str(reference_fasta),
            "--data-dir",
            str(data_dir),
            "--samples-output",
            str(samples_out),
            "--assemblies-output",
            str(assemblies_out),
            "--reference-dir",
            str(references_dir),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_prepare_inputs_happy_path(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    write_file(data_dir / "sample_1.ab1", "dummy")
    write_file(data_dir / "sample_2.ab1", "dummy")

    samplesheet = tmp_path / "samples.csv"
    write_file(
        samplesheet,
        "sample_id,ab1_file,assembly_group,reference_id\n"
        "sample_1,sample_1.ab1,1,refA\n"
        "sample_2,sample_2.ab1,1,refA\n",
    )

    reference_fasta = tmp_path / "refs.fa"
    write_file(reference_fasta, ">refA\nACGT\n>refB\nTTTT\n")

    samples_out = tmp_path / "samples.tsv"
    assemblies_out = tmp_path / "assemblies.tsv"
    references_dir = tmp_path / "references"

    result = run_prepare(
        samplesheet,
        reference_fasta,
        data_dir,
        samples_out,
        assemblies_out,
        references_dir,
    )

    assert result.returncode == 0, result.stderr
    assert samples_out.exists()
    assert assemblies_out.exists()
    assert (references_dir / "refA.fa").exists()
    assert not (references_dir / "refB.fa").exists()

    with samples_out.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 2
    assert rows[0]["sample_id"] == "sample_1"

    with assemblies_out.open(encoding="utf-8", newline="") as handle:
        assembly_rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(assembly_rows) == 1
    assert assembly_rows[0]["sample_id_joined"] == "sample_1_sample_2"


def test_prepare_inputs_missing_column_fails(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    write_file(data_dir / "sample_1.ab1", "dummy")

    bad_samplesheet = tmp_path / "bad.csv"
    write_file(
        bad_samplesheet,
        "sample_id,ab1_file,reference_id\n"
        "sample_1,sample_1.ab1,refA\n",
    )

    reference_fasta = tmp_path / "refs.fa"
    write_file(reference_fasta, ">refA\nACGT\n")

    result = run_prepare(
        bad_samplesheet,
        reference_fasta,
        data_dir,
        tmp_path / "samples.tsv",
        tmp_path / "assemblies.tsv",
        tmp_path / "references",
    )

    assert result.returncode != 0
    assert "missing required columns" in result.stderr.lower()
