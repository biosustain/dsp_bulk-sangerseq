#!/usr/bin/env nextflow

nextflow.enable.dsl = 2

workflow {
    def samplesheet_file = file(params.samplesheet)
    def reference_fasta_file = file(params.reference_fasta)
    def data_dir = file(params.data_dir)

    if (!samplesheet_file.exists()) {
        error "Samplesheet not found: ${params.samplesheet}"
    }

    if (!reference_fasta_file.exists()) {
        error "Reference FASTA not found: ${params.reference_fasta}"
    }

    if (!data_dir.exists()) {
        error "Data directory not found: ${params.data_dir}"
    }

    Channel.fromPath(params.samplesheet, checkIfExists: true).set { samplesheet_ch }
    Channel.fromPath(params.reference_fasta, checkIfExists: true).set { reference_fasta_ch }
    Channel.fromPath("${projectDir}/static/traceView.js", checkIfExists: true).set { trace_js_ch }

    PREPARE_INPUTS(samplesheet_ch, reference_fasta_ch)

    def reference_ch = PREPARE_INPUTS.out.reference_files.map { reference_file ->
        tuple(reference_file.baseName, reference_file)
    }

    def sample_tasks_ch = PREPARE_INPUTS.out.samples_tsv
        .splitCsv(header: true, sep: '\t')
        .map { row ->
            tuple(
                row.reference_id,
                row.sample_id,
                file(row.ab1_path, checkIfExists: true)
            )
        }
        .join(reference_ch)
        .map { reference_id, sample_id, ab1_file, reference_file ->
            tuple(sample_id, ab1_file, reference_file)
        }

    sample_tasks_ch.into { decompose_tasks_ch; align_tasks_ch }

    TRACY_DECOMPOSE(decompose_tasks_ch)
    TRACY_ALIGN(align_tasks_ch)

    def assembly_tasks_ch = PREPARE_INPUTS.out.assemblies_tsv
        .splitCsv(header: true, sep: '\t')
        .filter { row -> row.sample_id_joined?.trim() }
        .map { row ->
            def ab1_files = row.ab1_paths
                .split(';')
                .findAll { it }
                .collect { file(it, checkIfExists: true) }

            tuple(
                row.reference_id,
                row.assembly_group,
                row.sample_id_joined,
                ab1_files
            )
        }
        .join(reference_ch)
        .map { reference_id, assembly_group, sample_id_joined, ab1_files, reference_file ->
            tuple(assembly_group, sample_id_joined, reference_file, ab1_files)
        }

    TRACY_ASSEMBLE(assembly_tasks_ch)
    COPY_TRACE_JS(trace_js_ch)

    TRACY_ALIGN.out.json_results
        .combine(trace_js_ch)
        .map { sample_id, json_file, trace_js_file ->
            tuple(sample_id, json_file, trace_js_file)
        }
        .set { viewer_tasks_ch }

    RENDER_ALIGN_VIEWER(viewer_tasks_ch)
}

process PREPARE_INPUTS {
    container 'python:3.12-slim'

    input:
    path samplesheet_file
    path reference_fasta

    output:
    path 'samples.tsv', emit: samples_tsv
    path 'assemblies.tsv', emit: assemblies_tsv
    path 'references/*.fa', emit: reference_files

    script:
    """
    python ${projectDir}/scripts/prepare_tracy_inputs.py \
        --samplesheet ${samplesheet_file} \
        --reference-fasta ${reference_fasta} \
        --data-dir ${params.data_dir} \
        --samples-output samples.tsv \
        --assemblies-output assemblies.tsv \
        --reference-dir references
    """
}

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
    """
    tracy decompose -v \\
        -r ${reference_file} \\
        -o ${sample_id} \\
        --trimLeft ${params.trim_left} \\
        --trimRight ${params.trim_right} \\
        -t ${params.trim_stringency_decompose} \\
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
        -t ${params.trim_stringency_align} \\
        ${ab1_file}
    """
}

process TRACY_ASSEMBLE {
    tag "${sample_id_joined}"

    container params.tracy_image
    containerOptions "--platform ${params.container_platform}"

    publishDir "${params.outdir}/assemble", mode: 'copy', pattern: "${sample_id_joined}*"

    input:
    tuple val(assembly_group), val(sample_id_joined), path(reference_file), path(ab1_files)

    output:
    tuple val(assembly_group), path("${sample_id_joined}*"), emit: assemble_results

    script:
    def assembly_inputs = ab1_files.collect { "\"${it}\"" }.join(' ')
    """
    tracy assemble \\
        -r ${reference_file} \\
        -o ${sample_id_joined} \\
        -t ${params.trim_stringency_assemble} \\
        ${assembly_inputs}
    """
}

process COPY_TRACE_JS {
    container 'python:3.12-slim'

    publishDir "${params.outdir}/align", mode: 'copy'

    input:
    path trace_js_file

    output:
    path 'traceView.js'

    script:
    """
    cp ${trace_js_file} traceView.js
    """
}

process RENDER_ALIGN_VIEWER {
    tag "${sample_id}"

    container 'python:3.12-slim'

    publishDir "${params.outdir}/align", mode: 'copy', pattern: '*.html'

    input:
    tuple val(sample_id), path(json_file), path(trace_js_file)

    output:
    path "${sample_id}.html", emit: html_viewer

    script:
    """
    python ${projectDir}/scripts/tracy_render_align.py \\
        --json ${json_file} \\
        --output ${sample_id}.html \\
        --trace-js ${trace_js_file}
    """
}
