process TRACY_DECOMPOSE {
    tag "${sample_id}"

    container params.tracy_image
    containerOptions "--platform ${params.container_platform}"

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
