import os
from pathlib import Path
import sys


path_str = sys.argv[1]
output_dir = sys.argv[2]
trace_js_file = sys.argv[3]

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def viewer_html_factory(json_str):
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Trace Viewer</title>
</head>
<body>
    <div id="traceView"></div>
    <script src="./traceView.js"></script>
    <script>

        document.addEventListener("DOMContentLoaded", () => displayData({json_str}));
    </script>
</body>
</html>
    """


path = Path(path_str)
with open(path, "r") as f:
    json_str = f.read()
html_content = viewer_html_factory(json_str)
with open(os.path.join(output_dir, f"{path.stem}.html"), "w") as f:
    f.write(html_content)
