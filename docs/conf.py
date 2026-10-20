"""Sphinx configuration for the py-simba-pop-tools documentation."""

project = "py-simba-pop-tools"
copyright = "2026, Collins Patrick Ohagwu"
author = "Collins Patrick Ohagwu"
release = "0.1.0"  # py-simba-pop-tools; must equal its __version__ (checked by simba-ecosystem CI)
version = "0.1"

extensions = ["sphinx.ext.duration"]
templates_path = []
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
