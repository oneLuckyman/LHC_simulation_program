#!/usr/bin/env/ python3

from logging import WARNING
import os,sys,re
from turtle import bgcolor 
import pandas as pd 
import shutil 
import numpy as np 
import copy 

'''
@作者:  贾兴隆
@文档:  本程序的目标功能是实现蒙特卡洛模拟LHC对撞实验的自动化，本文件为继Alpha,Beta,Gamma之后的Delta开发版本。从本版本开始，文件会拥有尽可能完整的注释和文档。
@编写日志：
        2022年4月1日，本程序开始编写。构造了字体和颜色库，构造了进程父类以及其中的（进程的初始化，获得主进程目录，获得数据目录，获得generate_number）
        2022年4月2日，构造了进程准备类。
'''

class bcolors(object):
    '''
    打印所需的字体和颜色库
    '''
    WARNING = '\033[31;1m'  #红色高亮
    ENDC = '\033[0m'        #段位转义

    def print_WARNING(error_field):
        '''
        输出警告
        '''
        error = bcolors.WARNING + error_field + bcolors.ENDC
        return error


class Monte_Carlo_simulation(object):
    '''
    这是单个蒙特卡洛模拟进程所有子类的父类，所有必要的属性和方法都存在这里
    每当一个Monte_Carlo_simulation类被实例化时，即可视为一次蒙特卡洛模拟进程开始了
    '''
    def __init__(self, data_path_: str, generate_number_: str, main_path_: str = sys.path[0]) -> None:
        '''
        进程的初始化，获得主进程目录，数据目录，generate_number
        '''
        main_path(main_path_)
        data_path(data_path_)

        @property
        def main_path(self) -> str:
            '''
            获取主进程目录
            '''
            return self._main_path 

        @main_path.setter
        def main_path(self, main_path_: str) -> None:
            '''
            设置主进程目录
            '''
            if not isinstance(main_path_, str):
                raise ValueError(bcolors.print_WARNING('Main path must be a string!!!'))
            self._main_path = main_path_

        @property
        def data_path(self) -> str:
            '''
            获取数据目录
            '''
            return self._data_path

        @data_path.setter
        def data_path(self, data_path_: str) -> None:
            '''
            设置数据目录
            '''
            if not isinstance(data_path_, str):
                raise ValueError(bcolors.print_WARNING('Data path must be a string!!!'))
            self._data_path = data_path_

        @property
        def generate_number(self) -> str:
            '''
            获取generate_number
            generate_number指的是ck_input.csv表格的行数
            ck_input.csv包含了除MadGraph产生的events外所有Checkmate所需要的数据，也包含了所有可能需要输出的数据
            每当一个蒙特卡洛模拟进程开始的时候，generate_number都是必须的，以指认进行哪一个参数点进行LHC模拟。
            '''
            return self._generate_numbe

        @generate_number.setter
        def generate_number(self, generate_number_: str) -> None:
            '''
            设置generate_number
            会有一个generate_number.dat文件被送进来，因此输入参数中的generate_number_是一个包含generate_number.dat的路径
            原始的generate_number.dat的内容是一段用于替换的字段，该字段在每次模拟进程开始时应当被替换为ck_input.csv中对应行数，并且获得这个数值，这就是本函数的功能
            '''
        

class Prepare_process(Monte_Carlo_simulation):
    
    pass


    