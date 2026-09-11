#!/usr/bin/env python3
"""Assemble the VueGen report directory tree.

It takes explicit input paths (the files Nextflow has staged into the task
work directory) and builds the numbered ``vuegen_report/`` section tree
expected by VueGen, copying in the combined mutation table and the rendered
trace viewers.

Every tracy section holds its rendered viewer rather than tracy's text reports:
the Indigo viewer already shows the ``.align1`` / ``.align2`` / ``.align3``
alignments it would otherwise take three markdown sub-sections to print, the
Sage viewer shows the ``.txt`` alignment of the align step, and the assembly's
two viewers cover its outputs between them: Pearl the aligned traces behind the
consensus, Sabre the ``.align.fa`` multiple-sequence alignment read by read.
All of those text outputs stay published under ``outdir/`` for anyone who wants
them.

Rendering the tree into a report is done separately by the nf-core VUEGEN
module (see workflows/dsp_bulk_sangerseq.nf), which already ships a
maintained container with vuegen and its report-type dependencies baked in.
"""

import argparse
import shutil
import sys
from pathlib import Path

# Numbered top-level sections of the VueGen report tree.
SECTION_MUTATIONS = "01_Mutation_tables_decompose"
SECTION_VIEWERS_DECOMPOSE = "02_alignments_decompose"
SECTION_VIEWERS_ALIGN = "03_alignments_align"
SECTION_VIEWERS_ASSEMBLE = "04_sequence_assembly_assemble"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--combined",
        required=True,
        help="Combined mutation table (results_combined.csv) from postprocess.",
    )
    parser.add_argument(
        "--decompose-viewers",
        dest="decompose_viewers",
        help="Directory holding the rendered decompose (Indigo) viewers.",
    )
    parser.add_argument(
        "--align-viewers",
        dest="align_viewers",
        help="Directory holding the rendered align (Sage) viewers.",
    )
    parser.add_argument(
        "--assemble-viewers",
        dest="assemble_viewers",
        help="Directory holding the rendered assemble (Pearl / Sabre) viewers.",
    )
    parser.add_argument(
        "--report-dir",
        default="vuegen_report",
        dest="report_dir",
        help="Directory to build the VueGen section tree into.",
    )
    return parser.parse_args()


def copy_viewers(viewer_dir: Path | None, dest_dir: Path) -> None:
    """Copy the rendered ``.html`` viewers of one section into the report tree.

    VueGen reads a ``.html`` file as an HTML component and the renderer inlines
    it, so the viewer is readable inside the report and replaces the fenced-code
    text report this section used to print.

    A viewer directory that was never staged (no viewers rendered for that
    section) leaves no section behind, rather than an empty one VueGen would
    warn about.
    """
    if viewer_dir is None or not viewer_dir.is_dir():
        return

    viewers = sorted(viewer_dir.glob("*.html"))
    if not viewers:
        return

    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in viewers:
        shutil.copy2(src, dest_dir / src.name)


def build_tree(
    combined: Path,
    report_dir: Path,
    decompose_viewers: Path | None = None,
    align_viewers: Path | None = None,
    assemble_viewers: Path | None = None,
) -> None:
    """Populate the numbered VueGen section tree from the staged tracy outputs."""

    # 01 - combined mutation table (copied as-is).
    mut_dir = report_dir / SECTION_MUTATIONS
    mut_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(combined, mut_dir / "results_combined.csv")

    # 02 / 03 / 04 - the rendered trace viewers, in place of the decompose,
    # align and assemble text reports. They arrive from separate staging
    # directories because the sections name their files after the sample, so
    # staged flat the viewers of a sample would collide.
    copy_viewers(decompose_viewers, report_dir / SECTION_VIEWERS_DECOMPOSE)
    copy_viewers(align_viewers, report_dir / SECTION_VIEWERS_ALIGN)
    copy_viewers(assemble_viewers, report_dir / SECTION_VIEWERS_ASSEMBLE)


def main() -> int:
    args = parse_args()
    build_tree(
        Path(args.combined),
        Path(args.report_dir),
        Path(args.decompose_viewers) if args.decompose_viewers else None,
        Path(args.align_viewers) if args.align_viewers else None,
        Path(args.assemble_viewers) if args.assemble_viewers else None,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
