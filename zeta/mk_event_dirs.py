#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def make_dirs(dirs_path_root: str, dirs_name_root: str, size: int) -> None:
    os.chdir(dirs_path_root)
    for i in range(size):
        dir_name = dirs_name_root + str(i+1)
        if not os.path.exists(dir_name):
                os.mkdir(dir_name)

make_dirs('/mnt/storage/','2tau8c_', 5)