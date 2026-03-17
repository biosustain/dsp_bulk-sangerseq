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
