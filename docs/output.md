# Output

All results are published to the directory given by `--outdir`:

```
outdir
├── align
├── assemble
├── decompose
├── pipeline_info
├── results_combined.csv
├── sample_1.csv
├── sample_2.csv
└── vuegen_report
```

- `align/` — results from the `tracy align` process (alignment of each Sanger
  read against its reference), including the generated HTML trace viewers.
- `assemble/` — results from the `tracy assemble` process (reference-guided
  assembly of overlapping reads).
- `decompose/` — results from the `tracy decompose` process (mutation detection
  and decomposition of double peaks).
- `<sample>.csv` — per-sample mutation-detection results from `tracy decompose`.
- `results_combined.csv` — consolidated mutation-detection results across all
  samples.
- `pipeline_info/` — Nextflow execution reports (timeline, report, trace, DAG).
- `vuegen_report/` — the [VueGen](https://github.com/Multiomics-Analytics-Group/vuegen)
  report and its section tree.

## Mutation tables

One row per detected mutation, so a sample can occupy several rows. Each row
carries an `indigo_visualisation` column linking to that sample's Indigo viewer
in [`decompose/`](#decompose), opened on that row's mutation:

```
file:///path/to/outdir/decompose/sample_1.html?variants-table=0
```

The `?variants-table=<n>` parameter is the mutation's position in the sample's
variant list; the viewer reads it from the URL and shows that mutation in the
trace. Without it the viewer opens at an arbitrary region of the trace and the
mutation has to be found by clicking the row's chart icon — which writes the
same parameter back into the URL, so the address bar is always a link to what is
on screen and back/forward step through the mutations looked at. Point the links
somewhere else than the local filesystem with `--indigo_link_base` (see
[usage.md](usage.md#report)).

Browsers refuse to follow `file://` links out of a rendered page, so the links
cannot be clicked inside the VueGen report. Filter the table down to the
mutations of interest, copy their `indigo_visualisation` values and paste them
into a bulk URL opener such as the
[Bulk URL Opener](https://chromewebstore.google.com/detail/bulk-url-opener-tab-manag/nipkhjpemhflobkeegjpflbfmplpndje)
Chrome extension (which needs *Allow access to file URLs* enabled).

## `align/`

```
outdir/align
├── <sample>.abif
├── <sample>.align.fa
├── <sample>.html
├── <sample>.json
└── <sample>.txt
```

- `.align.fa` / `.txt` — pairwise alignment of the Sanger read against the
  reference sequence.
- `.html` — visualisation of the sequencing result (Sage).
- `.json` — full output of `tracy align`.

## `decompose/`

```
outdir/decompose
├── <sample>.abif
├── <sample>.align1
├── <sample>.align2
├── <sample>.align3
├── <sample>.bcf
├── <sample>.bcf.csi
├── <sample>.decomp
├── <sample>.html
└── <sample>.json
```

- `.align1` — alignment of the main signal against the reference.
- `.align2` — alignment of the minor signal against the reference.
- `.align3` — alignment of the major against the minor signal.
- `.html` — visualisation of the sequencing result (Indigo); accepts a
  `?variants-table=<n>` URL parameter to open on a specific mutation.
- `.bcf` — binary variant-call file (convertible to VCF with
  [bcftools](https://github.com/samtools/bcftools)).
- `.json` — full output of `tracy decompose`.

## `assemble/`

```
outdir/assemble
├── <group>.align.fa
├── <group>.cons.fa
├── <group>.html
├── <group>.json
└── <group>.vertical
```

- `.align.fa` — multiple-sequence alignment of the reads against the reference
  (viewable with [Sabre](https://www.gear-genomics.com/sabre/)).
- `.cons.fa` — consensus sequence from `tracy assemble`.
- `.html` — assembly visualisation (Pearl; **not implemented yet**).
- `.json` — full output of `tracy assemble`.

## `vuegen_report/`

```
outdir/vuegen_report
├── 01_Mutation_tables_decompose
│   ├── About_the_indigo_visualisation_links.md
│   └── results_combined.csv
├── 02_alignments_decompose
│   ├── align1/
│   ├── align2/
│   └── align3/
├── 03_alignments_align
│   └── <sample>.txt.md
└── 04_sequence_assembly_assemble
    ├── alignments/
    └── consensus_sequences/
```

The rendered report (e.g. `html`) is produced according to
`--vuegen_report_type`.
