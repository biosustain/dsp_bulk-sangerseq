import subprocess
import sys
from pathlib import Path

SCRIPT = "modules/local/vuegen/prepare_tree/resources/usr/bin/build_vuegen_tree.py"
MUTATION_SECTION = "01_Mutation_tables_decompose"
NOTE_NAME = "About_the_indigo_visualisation_links.md"

BASE_HEADER = (
    "sample_name,chr,pos,id,ref,alt,qual,filter,type,genotype,basepos,"
    "signalpos,successfully_edited"
)


def run_build_tree(combined: Path, indir: Path, report_dir: Path):
    return subprocess.run(
        [
            sys.executable, SCRIPT,
            "--combined", str(combined),
            "--indir", str(indir),
            "--report-dir", str(report_dir),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


# ---------------------------------------------------------------------------
# reader note for the Indigo link column
# ---------------------------------------------------------------------------

def test_note_explains_how_to_open_the_links(tmp_path: Path) -> None:
    # Given a mutation table that carries the Indigo link column
    combined = tmp_path / "results_combined.csv"
    combined.write_text(
        f"{BASE_HEADER},indigo_visualisation\n"
        "sample_1,ref_A,2274,.,A,C,45,PASS,SNV,hom. ALT,73,820,False,"
        "file:///results/decompose/sample_1.html?variants-table=0\n",
        encoding="utf-8",
    )
    report_dir = tmp_path / "vuegen_report"

    # When the report tree is built
    result = run_build_tree(combined, tmp_path, report_dir)

    # Then the mutation section gains a note pointing at the bulk URL opener
    assert result.returncode == 0, result.stderr
    note = report_dir / MUTATION_SECTION / NOTE_NAME
    assert note.exists()
    assert "indigo_visualisation" in note.read_text(encoding="utf-8")
    assert "Bulk URL Opener" in note.read_text(encoding="utf-8")


def test_no_note_without_the_link_column(tmp_path: Path) -> None:
    # Given a mutation table without the Indigo link column
    combined = tmp_path / "results_combined.csv"
    combined.write_text(
        f"{BASE_HEADER}\n"
        "sample_1,ref_A,2274,.,A,C,45,PASS,SNV,hom. ALT,73,820,False\n",
        encoding="utf-8",
    )
    report_dir = tmp_path / "vuegen_report"

    # When the report tree is built
    result = run_build_tree(combined, tmp_path, report_dir)

    # Then no note is written, so the report never explains a missing column
    assert result.returncode == 0, result.stderr
    assert (report_dir / MUTATION_SECTION / "results_combined.csv").exists()
    assert not (report_dir / MUTATION_SECTION / NOTE_NAME).exists()


def test_note_sorts_before_the_mutation_table(tmp_path: Path) -> None:
    # Given a mutation table that carries the Indigo link column
    combined = tmp_path / "results_combined.csv"
    combined.write_text(
        f"{BASE_HEADER},indigo_visualisation\n"
        "sample_1,ref_A,2274,.,A,C,45,PASS,SNV,hom. ALT,73,820,False,"
        "file:///results/decompose/sample_1.html?variants-table=0\n",
        encoding="utf-8",
    )
    report_dir = tmp_path / "vuegen_report"

    # When the report tree is built
    result = run_build_tree(combined, tmp_path, report_dir)

    # Then VueGen, which orders a section's components by filename, renders the
    # note above the table it describes
    assert result.returncode == 0, result.stderr
    section_files = sorted(p.name for p in (report_dir / MUTATION_SECTION).iterdir())
    assert section_files == [NOTE_NAME, "results_combined.csv"]
