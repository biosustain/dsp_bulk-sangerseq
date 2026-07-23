import json
import subprocess
import sys
from pathlib import Path


def test_render_align_generates_html_and_copies_js(tmp_path: Path) -> None:
    input_json = tmp_path / "sample.json"
    trace_js = tmp_path / "traceView.js"
    output_html = tmp_path / "viewer" / "sample.html"

    input_json.write_text(json.dumps({"k": "v"}), encoding="utf-8")
    trace_js.write_text("console.log('trace');", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            "bin/tracy_render_align.py",
            "--json",
            str(input_json),
            "--output",
            str(output_html),
            "--trace-js",
            str(trace_js),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output_html.exists()
    assert (output_html.parent / "traceView.js").exists()

    html_content = output_html.read_text(encoding="utf-8")
    assert "displayData" in html_content
    assert "\"k\": \"v\"" in html_content
