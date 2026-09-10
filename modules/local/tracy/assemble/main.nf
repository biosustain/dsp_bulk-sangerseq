process TRACY_ASSEMBLE {
    tag "${sample_id_joined}"

    container params.tracy_image
    //containerOptions "--platform ${params.container_platform}"

    input:
    tuple val(assembly_group), val(sample_id_joined), path(reference_file), path(ab1_files)

    output:
    tuple val(assembly_group), path("${sample_id_joined}*"), emit: assemble_results
    // Keyed by `sample_id_joined` rather than `assembly_group`, because it
    // names the rendered viewer. `optional: true` keeps a group that produced
    // no alignment (everything trimmed away) from failing the task, which
    // `errorStrategy = 'terminate'` would turn into a failed pipeline.
    tuple val(sample_id_joined), path("${sample_id_joined}.align.fa", optional: true), emit: align_fa
    // The same run's JSON, which carries `gappedTraces` and so feeds pearl's
    // editable assembly viewer. Optional for the same reason as `align_fa`.
    tuple val(sample_id_joined), path("${sample_id_joined}.json", optional: true), emit: assembly_json

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
