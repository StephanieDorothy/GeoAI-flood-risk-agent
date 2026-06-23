# Troubleshooting Log

This document records all issues encountered during development.

---

## Issue 001

Date: 23/06/2026

Problem:

ImportError: cannot import name 'PROJECT_ROOT' from config

Cause:

The configuration file was not being read correctly during the initial execution. After saving files and rerunning, the module loaded successfully.

Solution:

Verified contents of config.py and test_paths.py.
Reran the script after ensuring files were saved.

Lessons Learned:

Before changing code, verify that files are saved and that Python is loading the expected module.


