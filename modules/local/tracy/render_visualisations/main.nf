process TRACY_RENDER_VISUALISATIONS {
    tag "${sample_id} (${section})"

    container "${params.visualisation_image}"
    // Pin the platform to match the other tracy processes so local (e.g.
    // Apple Silicon) runs work. The image no longer sets an ENTRYPOINT, so
    // no override is needed here -- Azure Batch's TaskContainerSettings
    // validation rejects an empty --entrypoint value outright.
    containerOptions "--platform ${params.container_platform}"

    input:
    tuple val(sample_id), val(section), path(json_file)

    output:
    tuple val(section), path("${sample_id}.html"), emit: html_viewer

    script:
    """
    tracy-vis ${json_file} ${sample_id}.html
    """
}
