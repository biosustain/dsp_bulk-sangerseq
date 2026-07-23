#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def viewer_html_factory(json_content: str, trace_js: str) -> str:
    # The trace-viewer script is inlined so each HTML is self-contained.
    payload = json.dumps(json.loads(json_content))
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Trace Viewer</title>
</head>
<body>
    <div id="traceView"></div>
    <script>
{trace_js}
    </script>
    <script>
        document.addEventListener("DOMContentLoaded", () => displayData({payload}));
    </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True, dest="json_path")
    parser.add_argument("--output", required=True, dest="output_path")
    parser.add_argument("--trace-js", required=True, dest="trace_js_path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    json_path = Path(args.json_path)
    output_path = Path(args.output_path)
    trace_js_path = Path(args.trace_js_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    trace_js = trace_js_path.read_text(encoding="utf-8")
    with json_path.open(encoding="utf-8") as handle:
        html_content = viewer_html_factory(handle.read(), trace_js)

    output_path.write_text(html_content, encoding="utf-8")


if __name__ == "__main__":
    main()
