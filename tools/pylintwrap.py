#!/usr/bin/env python

import subprocess
import sys

from git_pylint_commit_hook import commit_hook


# overwrite _get_list_of_committed_files to get diff from origin/master
def _get_list_of_committed_files():
    files = []
    args = ["git", "diff", "--name-only", "origin/master", "--diff-filter=ACM"]

    output = subprocess.check_output(args)
    output = output.decode('utf-8')
    for file_name in output.split('\n'):
        if file_name != '':
            files.append(file_name.strip())

    return files


# pylint: disable=protected-access
commit_hook._get_list_of_committed_files = _get_list_of_committed_files
# pylint: enable=protected-access


if __name__ == '__main__':
    result = commit_hook.check_repo(10)
    if not result:
        sys.exit(1)

    sys.exit(0)

sys.exit(1)
