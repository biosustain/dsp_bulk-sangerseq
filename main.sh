#!/usr/bin/env bash

# Run Sanger sequencing analysis script
python3 -m bin.tracy_bulk_docker_samplesheet.py

# Run postprocessing script
python3 -m bin.tracy_postprocesssing.py

# Render visualisations
python3 -m tracy_render_visualisations.py

# Create vuegen report
python3 -m vuegen_report.py