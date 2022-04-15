#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ast import keyword
from lib2to3.pgen2.pgen import generate_grammar
from logging import WARNING
import os,sys,re
import pandas as pd 
import shutil 
import numpy as np 
import copy 

'''
@作者:  贾兴隆
@说明:  本程序的目标功能是实现蒙特卡洛模拟LHC对撞实验的自动化，本系列文件为继Alpha,Beta,Gamma,Delta之后的Epsilon开发版本。
        根据前四个版本的经验，整个自动化过程会有三种类别的数据（类的属性）和要执行的动作（类的方法）
        因此Epilson版本会把所有类分为三种类型：
            第一种类型：一旦进程启动轻易不会更改的属性和方法，例如主进程的目录，数据存放的目录，各个子程序的目录等等
            第二种类型：在单核的进程开始后，也就是当generate_numbers确定以后，不会再改变的数据和操作
            第三种类型：在单个参数点的计算开始后，也就是当generater_number确定以后，不会再改变的数据和操作
                这一种类型下还包括一种子类型，MadGraph类和CheckMATE类，这种子进程类可能会在第三种类型中多次调用，但每次实例化的过程相同。
            本文件包含第一种类型。
@开发日志：
        2022年4月6日：开始编写MC_sim_class.py
        2022年4月7日：MC_sim_class.py编写完毕
        2022年4月14日：添加了输入模型名，model_name
'''

#   !!!!    注意，本文件用于储存最基本的属性和方法，除非文件结构发生改变，否则本文件不要轻易改动    !!!!


class bcolors(object):
    '''
    打印所需的字体和颜色库。
    '''
    WARNING = '\033[31;1m'  #红色高亮
    ENDC = '\033[0m'        #段尾转义

    def print_WARNING(error_field):
        '''
        输出警告。
        '''
        error = bcolors.WARNING + error_field + bcolors.ENDC
        return error

class Monte_Carlo_simulation(object):
    '''
    这是单个蒙特卡洛模拟进程的主类，所有必要的属性和方法都存在这里。
    每当一个Monte_Carlo_simulation类被实例化时，即可视为一次蒙特卡洛模拟进程开始了。
    '''
    def __init__(self, data_path_: str, model_name_: str, info_name_list_: list, main_path_: str = sys.path[0]) -> None:
        '''
        进程的初始化，获得: 主进程目录，数据目录，generate_number， MadGraph目录
        数据目录包含了Spectrums文件夹，以及ck_input.csv文件。ck_input.csv文件中包含了所有要计算的参数点信息。
        '''
        self._main_path = main_path_                                                                       #获得主进程目录
        self._data_path = data_path_                                                                       #获得数据目录
        self._MadGraph_path = os.path.join(self._main_path, '../Externals/Madgraph/')                      #获得MadGraph的目录
        self._CheckMate_path = os.path.join(self._main_path, '../Externals/CheckMATE/CM_v2_26/')           #获得CheckMate的目录
        self._Support_path = os.path.join(self._main_path, '../Externals/ck/')                             #获得ck的目录
        self._result_path = os.path.join(self._main_path, 'ck_1/')                                         #获得结果目录
        self._info_name_list = info_name_list_                                                             #获得信息名称列表
        self._model_name = model_name_.upper()                                                             #获得模型名称

        if not os.path.exists(self._result_path):
            os.mkdir(self._result_path)

    @property
    def main_path(self) -> str:
        '''
        获取主进程目录
        '''
        return self._main_path  # 返回主进程目录

    @main_path.setter       
    def main_path(self, main_path_: str) -> None:
        '''
        设置主进程目录
        '''
        if not isinstance(main_path_, str):
            raise ValueError(bcolors.print_WARNING('Main path must be a string!!!'))            # 主进程目录必须是一个字符串
        self._main_path = main_path_ 

    @property
    def data_path(self) -> str:
        '''
        获取数据目录
        '''
        return self._data_path  # 返回数据目录

    @data_path.setter
    def data_path(self, data_path_: str) -> None:
        '''
        设置数据目录
        '''
        if not isinstance(data_path_, str):
            raise ValueError(bcolors.print_WARNING('Data path must be a string!!!'))                    # 数据目录必须是一个字符串
        self._data_path = data_path_

    @property
    def MadGraph_path(self) -> str:
        '''
        获取MadGraph目录
        '''
        return self._MadGraph_path

    @MadGraph_path.setter
    def MadGraph_path(self, MadGraph_path_: str) -> None:
        '''
        设置MadGraph目录
        '''
        if not isinstance(MadGraph_path_, str):
            raise ValueError(bcolors.print_WARNING('MadGraph path must be a string!!!'))                # MadGraph目录必须是一个字符串
        self._MadGraph_path = MadGraph_path_
    
    @property
    def CheckMate_path(self) -> str:
        '''
        获取CheckMate目录
        '''
        return self._CheckMate_path

    @CheckMate_path.setter
    def CheckMate_path(self, CheckMate_path_: str) -> None:
        '''
        设置CheckMate目录
        '''
        if not isinstance(CheckMate_path_, str):
            raise ValueError(bcolors.print_WARNING('CheckMate path must be a string!!!'))                # CheckMate目录必须是一个字符串
        self._CheckMate_path = CheckMate_path_

    @property
    def Support_path(self) -> str:
        '''
        获取Support目录
        '''
        return self._Support_path

    @Support_path.setter
    def Support_path(self, Support_path_: str) -> None:
        '''
        设置Support目录
        '''
        if not isinstance(Support_path_, str):
            raise ValueError(bcolors.print_WARNING('Support path must be a string!!!'))                # Support目录必须是一个字符串
        self._Support_path = Support_path_

    @property
    def model_name(self) -> str:
        '''
        获取模型名称
        '''
        return self._model_name
    
    @model_name.setter
    def model_name(self, model_name_: str) -> None:
        '''
        设置模型名称
        '''
        if not isinstance(model_name_, str):
            raise ValueError(bcolors.print_WARNING('Model name must be a string!!!'))                    # 模型名称必须是一个字符串
        self._model_name = model_name_.upper()






if __name__ != '__main__':
    info_name_list = ['Index']
    MC_sim = Monte_Carlo_simulation('/home/jxl/Desktop/program_test/collider_sim/Test/gnmssm', 'nmssm', info_name_list)

if __name__ == '__main__':
    print('Do not run this file directly!!')