#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

include { DSP_BULK_SANGERSEQ } from './workflows/dsp_bulk_sangerseq'

workflow {
    DSP_BULK_SANGERSEQ()
}
