import logging
import subprocess
import sys
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# %% Read yaml configuration file
with open('./config.yaml', 'r', encoding='utf-8') as file:
    cfg = yaml.safe_load(file)

outdir_host = Path(cfg['paths']['outdir_host']).resolve()
if not outdir_host.exists():
    raise FileNotFoundError(f'Output directory does not exist: {outdir_host}')

visualisation_cfg = cfg.get('visualisation', {})
visualisation_image = visualisation_cfg.get(
    'image',
    'ghcr.io/biosustain/tracy-visualisations',
)
visualisation_tag = str(visualisation_cfg.get('tag', 'latest'))
docker_platform = visualisation_cfg.get(
    'platform',
    cfg.get('docker', {}).get('platform', 'linux/amd64'),
)
visualisation_image_ref = f'{visualisation_image}:{visualisation_tag}'


def render_with_docker(json_file: Path, html_file: Path) -> None:
    """Render HTML using the published GHCR image."""
    output_dir = json_file.parent.resolve()
    docker_cmd = [
        'docker',
        'run',
        '--rm',
        '--platform',
        docker_platform,
        '-v',
        f'{output_dir}:/work',
        visualisation_image_ref,
        json_file.name,
        html_file.name,
    ]
    subprocess.run(docker_cmd, check=True)


def render_with_local_package(json_file: Path, html_file: Path) -> None:
    """Fallback renderer using the local tracy-visualisations checkout."""
    local_package_src = (
        Path(__file__).resolve().parent.parent / 'tracy-visualisations' / 'src'
    )
    if local_package_src.exists() and str(local_package_src) not in sys.path:
        sys.path.insert(0, str(local_package_src))

    from tracy_visualisations.bundler import bundle

    bundle(json_file, html_file)


# %% Pull tracy-visualisations Docker image
use_docker_visualisation = True
try:
    subprocess.run(
        [
            'docker',
            'pull',
            '--platform',
            docker_platform,
            visualisation_image_ref,
        ],
        check=True,
    )
except subprocess.CalledProcessError as e:
    use_docker_visualisation = False
    logging.warning(
        'Could not access Docker image %s (%s). Falling back to the local '
        'tracy-visualisations checkout.',
        visualisation_image_ref,
        e,
    )


# %% Render self-contained HTML visualisations for all Tracy JSON outputs
json_files = sorted(outdir_host.rglob('*.json'))
if not json_files:
    logging.warning('No Tracy JSON files found under %s', outdir_host)

for json_file in json_files:
    html_file = json_file.with_suffix('.html')
    logging.info('Rendering HTML visualisation for %s', json_file)

    try:
        if use_docker_visualisation:
            render_with_docker(json_file, html_file)
        else:
            render_with_local_package(json_file, html_file)
    except (subprocess.CalledProcessError, ImportError, FileNotFoundError) as e:
        logging.error(
            'Error rendering visualisation for %s: %s',
            json_file,
            e,
        )
