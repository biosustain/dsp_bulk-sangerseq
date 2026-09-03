import csv
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = "modules/local/tracy/postprocess/resources/usr/bin/tracy_postprocessing.py"

VARIANT_COLUMNS = [
    "chr", "pos", "id", "ref", "alt", "qual", "filter",
    "type", "genotype", "basepos", "signalpos",
]


def write_decompose_json(path: Path, trace_filename: str, variant_rows: list) -> None:
    """Write a minimal tracy decompose JSON with the given variant rows."""
    payload = {
        "meta": {"arguments": {"input": trace_filename}},
        "variants": {
            "columns": VARIANT_COLUMNS,
            "rows": variant_rows,
            "xranges": [[0, 100] for _ in variant_rows],
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def snv_row(pos: int, signalpos: int) -> list:
    return ["ref_A", pos, ".", "A", "C", 45, "PASS", "SNV", "hom. ALT", 73, signalpos]


def unedited_row(pos: int, signalpos: int) -> list:
    """A variant call with no alternative allele, i.e. a successful edit."""
    return ["ref_A", pos, ".", "A", None, 45, "PASS", "SNV", "hom. REF", 73, signalpos]


def run_postprocess(json_paths: list, outdir: Path, indigo_link_base=None):
    command = [sys.executable, SCRIPT, "--json", *[str(p) for p in json_paths],
               "--outdir", str(outdir)]
    if indigo_link_base is not None:
        command += ["--indigo-link-base", indigo_link_base]

    return subprocess.run(command, text=True, capture_output=True, check=False)


def read_csv(path: Path) -> list:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


# ---------------------------------------------------------------------------
# indigo_visualisation link column
# ---------------------------------------------------------------------------

def test_each_mutation_links_to_its_own_position_in_the_viewer(tmp_path: Path) -> None:
    # Given a decompose result with two detected mutations
    decompose_json = tmp_path / "sample_1.json"
    write_decompose_json(
        decompose_json, "sample_1.abi", [snv_row(2274, 820), snv_row(2301, 946)]
    )
    outdir = tmp_path / "out"

    # When the tables are built with an Indigo viewer base URL
    result = run_postprocess(
        [decompose_json], outdir, indigo_link_base="file:///results/decompose"
    )

    # Then every row links to the same viewer, each at its own variant index
    assert result.returncode == 0, result.stderr
    rows = read_csv(outdir / "results_combined.csv")
    assert [row["indigo_visualisation"] for row in rows] == [
        "file:///results/decompose/sample_1.html?variants-table=0",
        "file:///results/decompose/sample_1.html?variants-table=1",
    ]


def test_sample_without_mutations_links_to_the_viewer_itself(tmp_path: Path) -> None:
    # Given a decompose result with no detected mutations
    decompose_json = tmp_path / "sample_2.json"
    write_decompose_json(decompose_json, "sample_2.abi", [])
    outdir = tmp_path / "out"

    # When the tables are built with an Indigo viewer base URL
    result = run_postprocess(
        [decompose_json], outdir, indigo_link_base="file:///results/decompose"
    )

    # Then the placeholder row links to the viewer without a variant fragment
    assert result.returncode == 0, result.stderr
    rows = read_csv(outdir / "results_combined.csv")
    assert len(rows) == 1
    assert rows[0]["indigo_visualisation"] == "file:///results/decompose/sample_2.html"


def test_link_uses_the_sample_id_the_viewer_is_published_under(tmp_path: Path) -> None:
    # Given a sample whose raw trace filename differs from its sample id
    decompose_json = tmp_path / "my_sample.json"
    write_decompose_json(decompose_json, "raw_A01.abi", [snv_row(2274, 820)])
    outdir = tmp_path / "out"

    # When the tables are built with an Indigo viewer base URL
    result = run_postprocess(
        [decompose_json], outdir, indigo_link_base="file:///results/decompose"
    )

    # Then the link points at the viewer's name, while sample_name keeps the
    # trace filename it has always reported
    assert result.returncode == 0, result.stderr
    rows = read_csv(outdir / "results_combined.csv")
    assert rows[0]["sample_name"] == "raw_A01"
    assert rows[0]["indigo_visualisation"].endswith("/my_sample.html?variants-table=0")


def test_trailing_slash_in_the_base_url_is_not_doubled(tmp_path: Path) -> None:
    # Given a base URL that ends in a slash
    decompose_json = tmp_path / "sample_1.json"
    write_decompose_json(decompose_json, "sample_1.abi", [snv_row(2274, 820)])
    outdir = tmp_path / "out"

    # When the tables are built
    result = run_postprocess(
        [decompose_json], outdir, indigo_link_base="file:///results/decompose/"
    )

    # Then the link has a single separator before the filename
    assert result.returncode == 0, result.stderr
    rows = read_csv(outdir / "results_combined.csv")
    assert rows[0]["indigo_visualisation"] == (
        "file:///results/decompose/sample_1.html?variants-table=0"
    )


def test_link_column_is_absent_without_a_base_url(tmp_path: Path) -> None:
    # Given a decompose result and no Indigo viewer base URL
    decompose_json = tmp_path / "sample_1.json"
    write_decompose_json(decompose_json, "sample_1.abi", [snv_row(2274, 820)])
    outdir = tmp_path / "out"

    # When the tables are built
    result = run_postprocess([decompose_json], outdir)

    # Then the tables keep their original columns
    assert result.returncode == 0, result.stderr
    combined = (outdir / "results_combined.csv").read_text(encoding="utf-8")
    header = combined.splitlines()[0]
    assert header == (
        "sample_name,chr,pos,id,ref,alt,qual,filter,type,genotype,basepos,"
        "signalpos,successfully_edited"
    )


def test_links_are_written_to_the_per_sample_tables_too(tmp_path: Path) -> None:
    # Given decompose results for two samples
    write_decompose_json(
        tmp_path / "sample_1.json", "sample_1.abi", [snv_row(2274, 820)]
    )
    write_decompose_json(
        tmp_path / "sample_2.json", "sample_2.abi", [unedited_row(2274, 820)]
    )
    outdir = tmp_path / "out"

    # When the tables are built with an Indigo viewer base URL
    result = run_postprocess(
        [tmp_path / "sample_1.json", tmp_path / "sample_2.json"],
        outdir,
        indigo_link_base="file:///results/decompose",
    )

    # Then each per-sample table carries the links of its own sample
    assert result.returncode == 0, result.stderr
    sample_1_rows = read_csv(outdir / "sample_1.csv")
    sample_2_rows = read_csv(outdir / "sample_2.csv")
    assert sample_1_rows[0]["indigo_visualisation"] == (
        "file:///results/decompose/sample_1.html?variants-table=0"
    )
    assert sample_2_rows[0]["indigo_visualisation"] == (
        "file:///results/decompose/sample_2.html?variants-table=0"
    )
    assert sample_2_rows[0]["successfully_edited"] == "True"
