process TRACY_RENDER_VISUALISATIONS {
    tag "${sample_id} (${section})"

    container "${params.visualisation_image}"
    // Azure Batch's TaskContainerSettings validation rejects the
    // per-process containerOptions override outright (same as the other
    // tracy processes below), so leave platform pinning to the global
    // docker.runOptions for local (e.g. Apple Silicon) runs instead.
    //containerOptions "--platform ${params.container_platform}"

    input:
    tuple val(sample_id), val(section), path(json_file)

    output:
    tuple val(section), path("${sample_id}.html"), emit: html_viewer

    script:
    """
    tracy-vis ${json_file} ${sample_id}.html
    """
}
