# -*- coding: utf-8 -*-
import os


def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)

    if not os.path.exists(directory):
        os.makedirs(directory)
