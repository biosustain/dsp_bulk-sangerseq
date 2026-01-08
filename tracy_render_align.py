import glob
import os
from pathlib import Path
import shutil

import yaml

# %% Read yaml configuration file
with open("./config.yaml", "r") as file:
    cfg = yaml.safe_load(file)

align_output_dir = os.path.join(cfg["paths"]["outdir_host"], "align")
if not os.path.exists(align_output_dir):
    raise Exception(f"Alignment output directory does not exist: {align_output_dir}")

shutil.copy("/static/traceView.js", "/outdir/align/traceView.js")


def viewer_html_factory(json_file):
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


for path_str in glob.glob(os.path.join(cfg["paths"]["outdir_host"], "align", "*.json")):
    path = Path(path_str)
    with open(path, "r") as f:
        json_str = f.read()
    html_content = viewer_html_factory(json_str)
    with open(os.path.join(align_output_dir, f"{path.stem}.html"), "w") as f:
        f.write(html_content)

# %%
