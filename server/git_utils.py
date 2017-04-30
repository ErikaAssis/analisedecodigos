# coding: utf-8

import subprocess


def git_clone(repository_url, path_to_save):
    ''' Clone a Git repository using `git` binary '''
    return subprocess.call(['git', 'clone', repository_url, path_to_save])
