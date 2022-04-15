#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def make_dirs(dirs_path_root: str, dirs_name_root: str, size: int) -> None:
    os.chdir(dirs_path_root)
    for i in range(size):
        dir_name = dirs_name_root + str(i+1)
        if not os.path.exists(dir_name):
                os.mkdir(dir_name)
        if not os.path.exists(os.path.join(dir_name, 'bin')):
                os.mkdir(os.path.join(dir_name, 'bin'))
        if not os.path.exists(os.path.join(dir_name, 'bin', 'ck_1')):
                os.mkdir(os.path.join(dir_name, 'bin', 'ck_1'))
        if not os.path.exists(os.path.join(dir_name, 'Externals')):
                os.mkdir(os.path.join(dir_name, 'Externals'))
        if not os.path.exists(os.path.join(dir_name, 'Externals','ck')):
                os.mkdir(os.path.join(dir_name, 'Externals','ck'))
        if not os.path.exists(os.path.join(dir_name, 'Externals','ck','after_ck')):
                os.mkdir(os.path.join(dir_name, 'Externals','ck','after_ck'))
        if not os.path.exists(os.path.join(dir_name, 'Externals','Madgraph')):
                os.mkdir(os.path.join(dir_name, 'Externals','Madgraph'))
        if not os.path.exists(os.path.join(dir_name, 'Externals','CheckMATE')):
                os.mkdir(os.path.join(dir_name, 'Externals','CheckMATE'))

make_dirs('/home/jxl/Desktop','2tau8c_', 5)