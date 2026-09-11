process TRACY_RENDER_VISUALISATIONS {
    tag "${viewer_name} (${section})"

    container "${params.visualisation_image}"
    // Azure Batch's TaskContainerSettings validation rejects the
    // per-process containerOptions override outright (same as the other
    // tracy processes below), so leave platform pinning to the global
    // docker.runOptions for local (e.g. Apple Silicon) runs instead.
    //containerOptions "--platform ${params.container_platform}"

    input:
    // `tracy_output` is either a tracy JSON or a gapped multi-FASTA
    // alignment; `tracy-vis` picks the viewer from the file's content
    // (Sage / Indigo / Pearl for JSON, Sabre for FASTA).
    tuple val(viewer_name), val(section), path(tracy_output)

    output:
    tuple val(section), path("${viewer_name}.html"), emit: html_viewer

    script:
    """
    tracy-vis ${tracy_output} ${viewer_name}.html
    """
}
