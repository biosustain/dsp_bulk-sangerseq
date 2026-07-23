#!/usr/bin/env python3
"""Assemble the VueGen report directory tree and render the report.

It takes explicit input
paths (the files Nextflow has staged into the task work directory) and:

1. builds the numbered ``vuegen_report/`` section tree expected by VueGen,
   copying the combined mutation table and converting the tracy alignment /
   assembly text outputs to fenced-code markdown, and
2. runs ``vuegen`` on that tree to render the report (html by default).

The section layout and markdown wrapping match the reference output produced by
the original script byte-for-byte (```` ```\\n<content>\\n``` ````, no trailing
newline).
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

# Numbered top-level sections of the VueGen report tree.
SECTION_MUTATIONS = "01_Mutation_tables_decompose"
SECTION_ALIGN_DECOMPOSE = "02_alignments_decompose"
SECTION_ALIGN_ALIGN = "03_alignments_align"
SECTION_ASSEMBLE = "04_sequence_assembly_assemble"

# tracy ``decompose`` produces one alignment file per reported allele; each goes
# into its own sub-section.
DECOMPOSE_ALIGN_EXTS = ("align1", "align2", "align3")

# tracy ``assemble`` sub-sections: alignment vs. consensus sequence outputs.
ASSEMBLE_ALIGNMENTS = "alignments"
ASSEMBLE_CONSENSUS = "consensus_sequences"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--combined",
        required=True,
        help="Combined mutation table (results_combined.csv) from postprocess.",
    )
    parser.add_argument(
        "--indir",
        default=".",
        help="Directory holding the staged tracy outputs to route by extension.",
    )
    parser.add_argument(
        "--report-dir",
        default="vuegen_report",
        dest="report_dir",
        help="Directory to build the VueGen section tree into.",
    )
    parser.add_argument(
        "--report-type",
        default="html",
        dest="report_type",
        help="VueGen report type (html, streamlit, pdf, ...).",
    )
    return parser.parse_args()


def to_markdown(src: Path, dest_dir: Path) -> None:
    """Wrap a text file's content in a markdown code fence and write it out.

    The destination filename is the source name with ``.md`` appended (e.g.
    ``sample_1.align1`` -> ``sample_1.align1.md``); the body is exactly
    ```` ```\\n<content>\\n``` ```` with no trailing newline, matching the
    reference report output.
    """
    content = src.read_text(encoding="utf-8")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / (src.name + ".md")
    dest.write_text("```\n" + content + "\n```", encoding="utf-8")


def build_tree(combined: Path, indir: Path, report_dir: Path) -> None:
    """Populate the numbered VueGen section tree from the staged tracy outputs."""

    # 01 - combined mutation table (copied as-is).
    mut_dir = report_dir / SECTION_MUTATIONS
    mut_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(combined, mut_dir / "results_combined.csv")

    # 02 - per-allele decompose alignments, one sub-section per allele.
    for ext in DECOMPOSE_ALIGN_EXTS:
        dest_dir = report_dir / SECTION_ALIGN_DECOMPOSE / ext
        for src in sorted(indir.glob(f"*.{ext}")):
            to_markdown(src, dest_dir)

    # 03 - align text reports.
    align_dir = report_dir / SECTION_ALIGN_ALIGN
    for src in sorted(indir.glob("*.txt")):
        to_markdown(src, align_dir)

    # 04 - assembly alignments and consensus sequences.
    for src in sorted(indir.glob("*.align.fa")):
        to_markdown(src, report_dir / SECTION_ASSEMBLE / ASSEMBLE_ALIGNMENTS)
    for src in sorted(indir.glob("*.cons.fa")):
        to_markdown(src, report_dir / SECTION_ASSEMBLE / ASSEMBLE_CONSENSUS)


def render(report_dir: Path, report_type: str) -> None:
    """Render the assembled tree with VueGen, nested inside the report dir.

    VueGen derives the report title from the ``--directory`` name, so the tree
    must live in a named directory (``vuegen_report``, not ``.``) or quarto
    rejects the empty title. The rendered output is written to a
    ``rendered_report/`` sub-directory so the whole report - section structure
    plus rendered artifacts - is captured under the single ``report_dir`` the
    Nextflow module publishes.
    """
    subprocess.run(
        [
            "vuegen",
            "--directory",
            str(report_dir),
            "--report_type",
            report_type,
            "--output_directory",
            str(report_dir / "rendered_report"),
        ],
        check=True,
    )


def main() -> int:
    args = parse_args()
    report_dir = Path(args.report_dir)
    build_tree(Path(args.combined), Path(args.indir), report_dir)
    render(report_dir, args.report_type)
    return 0


if __name__ == "__main__":
    sys.exit(main())
