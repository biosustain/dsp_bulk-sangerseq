#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { DSP_BULK_SANGERSEQ } from './workflows/dsp_bulk_sangerseq'

// Validate `outdir` here, before the session starts, so a run that is missing
// `--outdir` fails immediately and never lets the trace/report/timeline/dag
// observers create a stray `null/pipeline_info` directory on completion.
if (!params.outdir) {
    error 'Required parameter --outdir was not provided'
}

workflow {
    DSP_BULK_SANGERSEQ()
}
