"""Sphinx configuration for the SIMBA ecosystem documentation."""

project = "SIMBA ecosystem"
copyright = "2026, Collins Patrick Ohagwu"
author = "Collins Patrick Ohagwu"
release = "0.1.0.dev0"  # py-simba-pop-tools
version = "0.1"

extensions = ["sphinx.ext.duration"]
templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
