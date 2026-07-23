process RENDER_ALIGN_VIEWER {
    tag "${sample_id}"

    container 'python:3.12'

    input:
    tuple val(sample_id), path(json_file), path(trace_js_file)

    output:
    path "${sample_id}.html", emit: html_viewer
    path 'traceView.js',      emit: trace_js

    script:
    """
    tracy_render_align.py \\
        --json ${json_file} \\
        --output ${sample_id}.html \\
        --trace-js ${trace_js_file}
    """
}
