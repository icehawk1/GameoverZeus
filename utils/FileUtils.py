#!/usr/bin/env python2.7
# coding=UTF-8
import os, errno


def mkdir_p(path):
    """Creates all directories in this path that do not exist yet. Silently skips existing directories.
    Behaves like mkdir -p in Linux."""
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
