process COPY_TRACE_JS {
    container 'python:3.12'

    input:
    path trace_js_file

    output:
    path 'traceView.js'

    script:
    """
    if [ "${trace_js_file}" != "traceView.js" ]; then
        cp "${trace_js_file}" traceView.js
    fi
    """
}
