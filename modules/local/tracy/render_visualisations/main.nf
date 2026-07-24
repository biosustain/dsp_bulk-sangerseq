process TRACY_RENDER_VISUALISATIONS {
    tag "${sample_id} (${section})"

    container "${params.visualisation_image}"
    // The image sets ENTRYPOINT ["tracy-vis"]; clear it so Nextflow can run
    // its own launcher (/bin/bash -c ...) inside the container. Pin the platform
    // to match the other tracy processes so local (e.g. Apple Silicon) runs work.
    containerOptions "--platform ${params.container_platform} --entrypoint \"\""

    input:
    tuple val(sample_id), val(section), path(json_file)

    output:
    tuple val(section), path("${sample_id}.html"), emit: html_viewer

    script:
    """
    tracy-vis ${json_file} ${sample_id}.html
    """
}
