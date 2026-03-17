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
