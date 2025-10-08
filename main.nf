#!/usr/bin/env nextflow

/*
================================================================================
    Nextflow Pipeline for Tracy Sanger Sequencing Analysis
================================================================================
*/

nextflow.enable.dsl = 2


// Input/output parameters
params.samplesheet = null
params.input_dir = null
params.outdir = './results'
params.config_file = './config.yaml'

// Tracy analysis parameters
params.trim_left = 50
params.trim_right = 200
params.tracy_image = 'geargenomics/tracy:latest'
params.container_platform = 'linux/amd64'

// Processing mode: 'samplesheet' or 'directory'
params.mode = 'auto'

// Reference file for directory mode (when not using samplesheet)
params.reference = null


workflow {
    
    // Validate input parameters
    if (!params.samplesheet && !params.input_dir) {
        error "Either --samplesheet or --input_dir must be provided"
    }
    
    // Determine processing mode
    def mode = params.mode
    if (mode == 'auto') {
        mode = params.samplesheet ? 'samplesheet' : 'directory'
    }
    
    // Create input channel based on mode
    if (mode == 'samplesheet') {
        // Samplesheet mode - similar to tracy_bulk_docker_samplesheet.py
        if (!file(params.samplesheet).exists()) {
            error "Samplesheet file not found: ${params.samplesheet}"
        }
        
        samples_ch = Channel
            .fromPath(params.samplesheet)
            .splitCsv(header: true, sep: ',')
            .map { row ->
                [
                    row.sample_id,
                    file(row.ab1_1),
                    file(row.reference)
                ]
            }
    } else {
        // Directory mode - similar to tracy_bulk_docker.py
        if (!params.input_dir) {
            error "Input directory must be provided when not using samplesheet mode"
        }
        
        def reference_file = params.reference ? file(params.reference) : null
        
        samples_ch = Channel
            .fromPath("${params.input_dir}/*.ab1")
            .map { ab1_file ->
                def sample_id = ab1_file.baseName
                [
                    sample_id,
                    ab1_file,
                    reference_file
                ]
            }
    }
    
    // Run Tracy decompose process
    TRACY_DECOMPOSE(samples_ch)
    
    // Run Tracy align process (only when reference is provided)
    samples_with_ref = samples_ch.filter { _sample_id, _ab1_file, ref_file -> ref_file != null }
    TRACY_ALIGN(samples_with_ref)
    
    // Run alignment viewer - collect all JSON files (including empty collection)
    align_json_ch = TRACY_ALIGN.out.json_results
        .map { _sample_id, json_file -> json_file }
        .collect()
        .ifEmpty(Channel.value([]))  // Ensure we always have a value to pass
    
    trace_js_ch = Channel.fromPath("${projectDir}/static/traceView.js")
    
    // Always run viewer (it will handle the case of no results)
    RENDER_ALIGN_VIEWER(align_json_ch, trace_js_ch)
}

/*
================================================================================
    PROCESSES
================================================================================
*/

process TRACY_DECOMPOSE {
    tag "${sample_id}"
    
    container params.tracy_image
    containerOptions "--platform ${params.container_platform}"
    
    publishDir "${params.outdir}/decompose", mode: 'copy', pattern: "${sample_id}*"
    
    input:
    tuple val(sample_id), path(ab1_file), path(reference_file)
    
    output:
    tuple val(sample_id), path("${sample_id}*"), emit: decompose_results
    tuple val(sample_id), path("${sample_id}.json"), emit: json_results, optional: true
    
    script:
    def reference_arg = reference_file ? "-r ${reference_file}" : ""
    """
    tracy decompose -v \\
        ${reference_arg} \\
        -o ${sample_id} \\
        --trimLeft ${params.trim_left} \\
        --trimRight ${params.trim_right} \\
        ${ab1_file}
    """
}

process TRACY_ALIGN {
    tag "${sample_id}"
    
    container params.tracy_image
    containerOptions "--platform ${params.container_platform}"
    
    publishDir "${params.outdir}/align", mode: 'copy', pattern: "${sample_id}*"
    
    input:
    tuple val(sample_id), path(ab1_file), path(reference_file)
    
    output:
    tuple val(sample_id), path("${sample_id}*"), emit: align_results
    tuple val(sample_id), path("${sample_id}.json"), emit: json_results, optional: true
    
    script:
    """
    tracy align \\
        -r ${reference_file} \\
        -o ${sample_id} \\
        --trimLeft ${params.trim_left} \\
        --trimRight ${params.trim_right} \\
        ${ab1_file}
    """
}

process RENDER_ALIGN_VIEWER {
    tag "render_alignment_viewer"
    
    container 'python:3.9-slim'
    
    publishDir "${params.outdir}/viewer", mode: 'copy'
    
    input:
    path json_file
    path trace_js_file
    
    output:
    path "${params.outdir}/*.html", emit: html_viewer
    
    script:
    """
    ls
    python /Users/dommas/Projects/dsp_bulk-sangerseq/scripts/tracy_render_align.py ${json_file} ${params.outdir} ${trace_js_file}
    ls
    """
}
