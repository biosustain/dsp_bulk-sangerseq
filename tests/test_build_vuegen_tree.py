import subprocess
import sys
from pathlib import Path

SCRIPT = "modules/local/vuegen/prepare_tree/resources/usr/bin/build_vuegen_tree.py"
MUTATION_SECTION = "01_Mutation_tables_decompose"
DECOMPOSE_VIEWER_SECTION = "02_alignments_decompose"
ALIGN_VIEWER_SECTION = "03_alignments_align"
ASSEMBLE_VIEWER_SECTION = "04_sequence_assembly_assemble"

BASE_HEADER = (
    "sample_name,chr,pos,id,ref,alt,qual,filter,type,genotype,basepos,"
    "signalpos,successfully_edited"
)


def run_build_tree(
    combined: Path,
    report_dir: Path,
    decompose_viewers: Path | None = None,
    align_viewers: Path | None = None,
    assemble_viewers: Path | None = None,
):
    command = [
        sys.executable, SCRIPT,
        "--combined", str(combined),
        "--report-dir", str(report_dir),
    ]

    if decompose_viewers is not None:
        command += ["--decompose-viewers", str(decompose_viewers)]
    if align_viewers is not None:
        command += ["--align-viewers", str(align_viewers)]
    if assemble_viewers is not None:
        command += ["--assemble-viewers", str(assemble_viewers)]

    return subprocess.run(command, text=True, capture_output=True, check=False)


# ---------------------------------------------------------------------------
# rendered trace viewers
# ---------------------------------------------------------------------------

def write_minimal_combined_table(combined: Path) -> None:
    combined.write_text(
        f"{BASE_HEADER}\n"
        "sample_1,ref_A,2274,.,A,C,45,PASS,SNV,hom. ALT,73,820,False\n",
        encoding="utf-8",
    )


def test_rendered_viewers_land_in_their_own_sections(tmp_path: Path) -> None:
    # Given rendered Indigo, Sage and Pearl viewers, staged in separate
    # directories so the identically named per-sample files never clash
    combined = tmp_path / "results_combined.csv"
    write_minimal_combined_table(combined)

    decompose_viewers = tmp_path / "decompose_viewers"
    decompose_viewers.mkdir()
    (decompose_viewers / "sample_1.html").write_text("<html>indigo</html>")
    (decompose_viewers / "sample_2.html").write_text("<html>indigo</html>")

    align_viewers = tmp_path / "align_viewers"
    align_viewers.mkdir()
    (align_viewers / "sample_1.html").write_text("<html>sage</html>")

    assemble_viewers = tmp_path / "assemble_viewers"
    assemble_viewers.mkdir()
    (assemble_viewers / "sample_1_sample_2.html").write_text("<html>pearl</html>")

    report_dir = tmp_path / "vuegen_report"

    # When the report tree is built
    result = run_build_tree(
        combined,
        report_dir,
        decompose_viewers=decompose_viewers,
        align_viewers=align_viewers,
        assemble_viewers=assemble_viewers,
    )

    # Then VueGen finds one HTML component per sample in each viewer section
    assert result.returncode == 0, result.stderr
    assert (report_dir / DECOMPOSE_VIEWER_SECTION / "sample_1.html").exists()
    assert (report_dir / DECOMPOSE_VIEWER_SECTION / "sample_2.html").exists()
    assert (report_dir / ALIGN_VIEWER_SECTION / "sample_1.html").exists()
    assert (report_dir / ASSEMBLE_VIEWER_SECTION / "sample_1_sample_2.html").exists()

    # And the two sections keep the viewers apart despite the shared filename
    decompose_html = (report_dir / DECOMPOSE_VIEWER_SECTION / "sample_1.html").read_text()
    align_html = (report_dir / ALIGN_VIEWER_SECTION / "sample_1.html").read_text()
    assert decompose_html == "<html>indigo</html>"
    assert align_html == "<html>sage</html>"


def test_both_assembly_viewers_land_in_the_assemble_section(tmp_path: Path) -> None:
    # Given the two viewers tracy assemble's outputs are rendered into: Pearl
    # from the JSON, and Sabre from the `.align.fa` multiple-sequence alignment
    combined = tmp_path / "results_combined.csv"
    write_minimal_combined_table(combined)

    assemble_viewers = tmp_path / "assemble_viewers"
    assemble_viewers.mkdir()
    (assemble_viewers / "sample_1_sample_2.html").write_text("<html>pearl</html>")
    (assemble_viewers / "sample_1_sample_2_alignment.html").write_text("<html>sabre</html>")

    report_dir = tmp_path / "vuegen_report"

    # When the report tree is built
    result = run_build_tree(combined, report_dir, assemble_viewers=assemble_viewers)

    # Then the group is shown twice in the assemble section, the consensus
    # assembly and the read-by-read alignment, under names that do not collide
    assert result.returncode == 0, result.stderr
    assemble_section = sorted(p.name for p in (report_dir / ASSEMBLE_VIEWER_SECTION).iterdir())
    assert assemble_section == [
        "sample_1_sample_2.html",
        "sample_1_sample_2_alignment.html",
    ]


def test_viewers_replace_the_tracy_text_reports(tmp_path: Path) -> None:
    # Given tracy's decompose, align and assemble text reports staged alongside
    # the viewers rendered from the same samples
    combined = tmp_path / "results_combined.csv"
    write_minimal_combined_table(combined)

    (tmp_path / "sample_1.align1").write_text("alt1 alignment")
    (tmp_path / "sample_1.align2").write_text("alt2 alignment")
    (tmp_path / "sample_1.align3").write_text("alt1 vs alt2 alignment")
    (tmp_path / "sample_1.txt").write_text("align report")
    (tmp_path / "sample_1_sample_2.align.fa").write_text(">aln")
    (tmp_path / "sample_1_sample_2.cons.fa").write_text(">cons")

    decompose_viewers = tmp_path / "decompose_viewers"
    decompose_viewers.mkdir()
    (decompose_viewers / "sample_1.html").write_text("<html>indigo</html>")

    align_viewers = tmp_path / "align_viewers"
    align_viewers.mkdir()
    (align_viewers / "sample_1.html").write_text("<html>sage</html>")

    assemble_viewers = tmp_path / "assemble_viewers"
    assemble_viewers.mkdir()
    (assemble_viewers / "sample_1_sample_2.html").write_text("<html>pearl</html>")

    report_dir = tmp_path / "vuegen_report"

    # When the report tree is built
    result = run_build_tree(
        combined,
        report_dir,
        decompose_viewers=decompose_viewers,
        align_viewers=align_viewers,
        assemble_viewers=assemble_viewers,
    )

    # Then each section holds only its viewer -- the text the viewer already
    # displays is not printed a second time as fenced-code markdown
    assert result.returncode == 0, result.stderr
    decompose_section = sorted(p.name for p in (report_dir / DECOMPOSE_VIEWER_SECTION).iterdir())
    align_section = sorted(p.name for p in (report_dir / ALIGN_VIEWER_SECTION).iterdir())
    assemble_section = sorted(p.name for p in (report_dir / ASSEMBLE_VIEWER_SECTION).iterdir())
    assert decompose_section == ["sample_1.html"]
    assert align_section == ["sample_1.html"]
    assert assemble_section == ["sample_1_sample_2.html"]


def test_viewer_sections_are_skipped_when_nothing_was_rendered(tmp_path: Path) -> None:
    # Given a run whose viewer directories were never staged
    combined = tmp_path / "results_combined.csv"
    write_minimal_combined_table(combined)
    report_dir = tmp_path / "vuegen_report"

    # When the report tree is built
    result = run_build_tree(combined, report_dir)

    # Then the tree is still built, without empty sections VueGen would warn on
    assert result.returncode == 0, result.stderr
    assert (report_dir / MUTATION_SECTION / "results_combined.csv").exists()
    assert not (report_dir / DECOMPOSE_VIEWER_SECTION).exists()
    assert not (report_dir / ALIGN_VIEWER_SECTION).exists()
    assert not (report_dir / ASSEMBLE_VIEWER_SECTION).exists()
