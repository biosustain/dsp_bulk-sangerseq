#!/usr/bin/env python3
"""Assemble the VueGen report directory tree.

It takes explicit input paths (the files Nextflow has staged into the task
work directory) and builds the numbered ``vuegen_report/`` section tree
expected by VueGen, copying the combined mutation table and converting the
tracy alignment / assembly text outputs to fenced-code markdown.

Rendering the tree into a report is done separately by the nf-core VUEGEN
module (see workflows/dsp_bulk_sangerseq.nf), which already ships a
maintained container with vuegen and its report-type dependencies baked in.

The section layout and markdown wrapping match the reference output produced by
the original script byte-for-byte (```` ```\\n<content>\\n``` ````, no trailing
newline).
"""

import argparse
import csv
import shutil
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

# Link column added to the mutation tables by the postprocess step. Its presence
# is what decides whether the reader note below is worth including.
INDIGO_LINK_COLUMN = "indigo_visualisation"

# Sorts ahead of ``results_combined.csv``, so VueGen renders the note above the
# table it describes.
INDIGO_LINK_NOTE_NAME = "About_the_indigo_visualisation_links.md"

INDIGO_LINK_NOTE = f"""## Opening the Indigo visualisation links

The `{INDIGO_LINK_COLUMN}` column of the mutation table links every detected
mutation to the Sanger trace it was called from: the sample's Indigo
electropherogram, opened on that mutation instead of the arbitrary region the
visualisation otherwise opens at.

Browsers refuse to follow `file://` links out of a rendered page, so the links
cannot be clicked here — they have to be copied. To inspect a set of traces:

1. Sort or filter the table (for example on `successfully_edited`) down to the
   mutations of interest.
2. Copy the `{INDIGO_LINK_COLUMN}` values of those rows.
3. Paste a single link into the browser's address bar, or a whole set into a
   bulk URL opener such as the
   [Bulk URL Opener](https://chromewebstore.google.com/detail/bulk-url-opener-tab-manag/nipkhjpemhflobkeegjpflbfmplpndje)
   Chrome extension, to open them all at once.

For `file://` links the extension needs *Allow access to file URLs* enabled in
its Chrome settings.
"""


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


def has_indigo_links(combined: Path) -> bool:
    """Return whether the mutation table carries the Indigo viewer link column."""
    with combined.open(encoding="utf-8", newline="") as handle:
        header = next(csv.reader(handle), [])
    return INDIGO_LINK_COLUMN in header


def build_tree(combined: Path, indir: Path, report_dir: Path) -> None:
    """Populate the numbered VueGen section tree from the staged tracy outputs."""

    # 01 - combined mutation table (copied as-is), preceded by a note on how to
    # use its Indigo links when the postprocess step added them.
    mut_dir = report_dir / SECTION_MUTATIONS
    mut_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(combined, mut_dir / "results_combined.csv")
    if has_indigo_links(combined):
        (mut_dir / INDIGO_LINK_NOTE_NAME).write_text(INDIGO_LINK_NOTE, encoding="utf-8")

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


def main() -> int:
    args = parse_args()
    build_tree(Path(args.combined), Path(args.indir), Path(args.report_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
