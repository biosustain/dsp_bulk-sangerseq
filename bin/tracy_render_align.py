#!/usr/bin/env python3
import argparse
import json
import shutil
from pathlib import Path


def viewer_html_factory(json_content: str) -> str:
    payload = json.dumps(json.loads(json_content))
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Trace Viewer</title>
</head>
<body>
    <div id="traceView"></div>
    <script src="./traceView.js"></script>
    <script>
        document.addEventListener("DOMContentLoaded", () => displayData({payload}));
    </script>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--json', required=True, dest='json_path')
    parser.add_argument('--output', required=True, dest='output_path')
    parser.add_argument('--trace-js', required=True, dest='trace_js_path')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    json_path = Path(args.json_path)
    output_path = Path(args.output_path)
    trace_js_path = Path(args.trace_js_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    trace_js_dest = output_path.parent / 'traceView.js'
    if trace_js_path.resolve() != trace_js_dest.resolve():
        shutil.copy2(trace_js_path, trace_js_dest)

    with json_path.open(encoding='utf-8') as handle:
        html_content = viewer_html_factory(handle.read())

    output_path.write_text(html_content, encoding='utf-8')


if __name__ == '__main__':
    main()
