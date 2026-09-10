process TRACY_RENDER_VISUALISATIONS {
    tag "${viewer_id} (${section})"

    container "${params.visualisation_image}"
    // Azure Batch's TaskContainerSettings validation rejects the
    // per-process containerOptions override outright (same as the other
    // tracy processes below), so leave platform pinning to the global
    // docker.runOptions for local (e.g. Apple Silicon) runs instead.
    //containerOptions "--platform ${params.container_platform}"

    // `viewer_id` is the output basename, not necessarily a sample id: a
    // section rendering more than one viewer per input distinguishes them
    // here, because every viewer of a section is published to one directory.
    input:
    tuple val(viewer_id), val(section), path(data_file)

    output:
    tuple val(section), path("${viewer_id}.html"), emit: html_viewer

    script:
    """
    tracy-vis ${data_file} ${viewer_id}.html
    """
}
