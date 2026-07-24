# Usage

`dsp_bulk-sangerseq` is a [Nextflow](https://www.nextflow.io) DSL2 pipeline for
bulk analysis of Sanger sequencing data with [Tracy](https://github.com/gear-genomics/tracy).
All analysis software runs inside Docker containers that Nextflow pulls
automatically, so only **Java (17+)**, **Nextflow (>=23.10.0)** and **Docker** are
required on the host. See the [README](../README.md) for host-installation
instructions and [installation_prerequisites.md](installation_prerequisites.md)
for WSL/Windows notes.

## Quick start

Run against the bundled test dataset:

```bash
nextflow run . -profile docker,test
```

Run on your own data (`--outdir` is required):

```bash
nextflow run . -profile docker \
  --data_dir /path/to/ab1 \
  --samplesheet /path/to/samplesheet.csv \
  --reference_fasta /path/to/references.fa \
  --outdir results
```

On the first run Nextflow pulls the container images used by the pipeline
(`geargenomics/tracy` and `python:3.12`); no manual Python or dependency setup is
required.

## Samplesheet

The pipeline is driven by a CSV samplesheet with the following columns:

| Column | Description |
|--------|-------------|
| `sample_id` | Unique sample name. |
| `ab1_file` | Name of the `.ab1` sequencing file (located in `--data_dir`). |
| `assembly_group` | Group id (e.g. `1`, `2`) for reference-guided assembly; leave blank to skip assembly for the sample. |
| `reference_id` | Reference name, which **must** match a FASTA header in `--reference_fasta`. |

Samples that share an `assembly_group` are assembled together (a minimum of two
sequences is required). Forward/reverse orientation is detected automatically by
Tracy — input sequences do not need to be reverse-complemented beforehand.

Templates are provided under [`data/test_data_1`](../data/test_data_1).

## Parameters

Parameters can be passed on the command line as `--<parameter> <value>` or
collected in a `-params-file params.yaml`. Defaults, types and validation rules
are defined in [`nextflow_schema.json`](../nextflow_schema.json).

### Input/output

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--data_dir` | Directory containing the `.ab1` files. | `data/test_data_1` |
| `--samplesheet` | Path to the samplesheet `.csv`. | see schema |
| `--reference_fasta` | Path to the multi-fasta reference file. | see schema |
| `--outdir` | Output directory for published results. **Required.** | *(none)* |

### Tracy trimming

`trim_left`/`trim_right` set the number of bases trimmed at the 5'/3' ends. Trim
stringency (`1`–`9`, `0` disables) can be combined with them to determine the
trimming length automatically from sequencing quality, and is set separately per
Tracy command. For standard workflows the `decompose` and `align` stringencies
should be identical.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--trim_left` | Bases to trim at the 5'-end. | `50` |
| `--trim_right` | Bases to trim at the 3'-end. | `50` |
| `--trim_stringency_decompose` | Trim stringency for `decompose` (0-9). | `0` |
| `--trim_stringency_align` | Trim stringency for `align` (0-9). | `0` |
| `--trim_stringency_assemble` | Trim stringency for `assemble` (0-9). | `4` |

### Report

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--vuegen_report_type` | VueGen report type: `html`, `streamlit`, `pdf`, `docx`, `revealjs`, `pptx`, `jupyter`. | `html` |
| `--vuegen_version` | VueGen version pip-installed at runtime. | `0.6.0` |

For the `pdf` report type, `tinytex` is required (`quarto install tinytex`). See
the [VueGen documentation](https://github.com/Multiomics-Analytics-Group/vuegen)
for details.

## Testing

The pipeline is covered by [nf-test](https://www.nf-test.com); see the
[README](../README.md#testing-the-nextflow-pipeline) for how to run the suite.
