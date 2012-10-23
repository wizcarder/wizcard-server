#!/usr/bin/python
# The Wiz utils. For now there is only logging in here. In future other util functions
# e.g profiling, debugging etc. will find home here.

# Logging
# TODO: build a log file, for now log messages are dumped on console.

# logging flag: For now there is only one level of logging, in future there could be 
# multiple.
verbose = True

# pretty basic: dump on console.
def log(*args):
    if verbose:
        print args

# End of wizutils.py
