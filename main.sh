#!/usr/bin/env bash

# Run Sanger sequencing analysis script
python3 -m bin.tracy_bulk_docker_samplesheet

# Run postprocessing script
python3 -m bin.tracy_postprocesssing

# Render visualisations
python3 -m bin.tracy_render_visualisations

# Create vuegen report
python3 -m bin.vuegen_report