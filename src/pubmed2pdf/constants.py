# -*- coding: utf-8 -*-

"""This module contains all the constants used in pubmed2pdf repo."""

import os

MODULE_NAME = 'pubmed2pdf'
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser('~'), 'pubmed2pdf')
DEFAULT_ERROR_FILE = "failed_pubmeds.tsv"

def get_data_dir() -> str:
    """Ensure the appropriate pubmed2pdf data directory exists for the given module, then returns the file path."""
    os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
    return DEFAULT_OUTPUT_DIR

DATA_DIR = get_data_dir()