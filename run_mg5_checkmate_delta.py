#!/usr/bin/env/ python3

from ast import keyword
from lib2to3.pgen2.pgen import generate_grammar
from logging import WARNING
import os,sys,re
from turtle import bgcolor
from isort import file 
import pandas as pd 
import shutil 
import numpy as np 
import copy 

'''
@作者:  贾兴隆
@说明:  本程序的目标功能是实现蒙特卡洛模拟LHC对撞实验的自动化，本系列文件为继Alpha,Beta,Gamma之后的Delta开发版本。从本版本开始，程序会拥有尽可能完整的注释和文档。
@开发日志：
        2022年4月1日：本程序开始编写。构造了字体和颜色库，构造了Monte_Carlo_simulation类以及其中的（进程的初始化，获得主进程目录，获得数据目录）
        2022年4月2日：构造了Monte_Carlo_simulation类中，generate_number的内容。将项目上传至GitHub。
        2022年4月3日：构造进程准备类，补完generate_number函数。
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

class Prepare_program(object):
    '''
    单个模拟进程开始前的准备工作
    将来会用于替换prepare.py
    '''
    def __init__(self) -> None:
        pass

    def get_generate_numbers_from_ck_ini(self, ck_ini: str) -> list:
        '''
        输入一个ck.ini文件，并获取本次进程所需的所有generate_numbers
        '''
        search_keyword = 'Input parameters:'
        with open('{}/ck.ini'.format(self._main_path)) as ck_ini:       #本文件同目录下存在一个ck.ini文件，这是一个easyscan配置文件，其中包含了要执行的单个进程所需的所有信息。旧的程序正是依赖easyscan运行的。
            for line in ck_ini:
                if search_keyword in line:
                    ck_ini_message = re.split(r'[\s\,]+', line)         #本程序所需的ck.ini中的信息是，要计算的目标参数点所对应的ck_input.csv的行数
                    generate_number_range = [int(ck_ini_message[-3]),int(ck_ini_message[-2])]
                    generate_numbers = list(range(generate_number_range[1] - generate_number_range[0] - 1, 1))
        return generate_numbers


class Monte_Carlo_simulation(object):
    '''
    这是单个蒙特卡洛模拟进程所有子类的父类，所有必要的属性和方法都存在这里
    每当一个Monte_Carlo_simulation类被实例化时，即可视为一次蒙特卡洛模拟进程开始了
    '''
    def __init__(self, data_path_: str, generate_number_: int, main_path_: str = sys.path[0]) -> None:
        '''
        进程的初始化，获得主进程目录，数据目录，generate_number
        '''
        main_path(main_path_)
        data_path(data_path_)
        generate_number(generate_number_)

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
            return self._generate_number

        @generate_number.setter
        def generate_number(self, generate_number_: int) -> None:
            '''
            设置generate_number
            会有一个generate_number.dat文件被送进来，因此输入参数中的generate_number_是一个包含generate_number.dat的路径
            旧有的模式是，原始的generate_number.dat的内容是一段用于替换的字段，该字段在每次模拟进程开始时被替换为一个ck_input.csv中的行标，并且获得这个数值
            为了保持与旧程序的连贯性，不改变原有的文件结构，本函数的功能暂时维持旧有的模式，但可以避免对generate_number.dat的依赖
            后续可能的优化是使用生成器和迭代器改进多核进程
            '''
            if not isinstance(generate_number_, int):
                raise ValueError(bcolors.print_WARNING('Generate number must be a integer!!!'))
            self._generate_number = generate_number_


class Prepare_MCsim(Monte_Carlo_simulation):##需要改！！
    '''
    
    '''
    def __init__(self, data_path_: str, generate_number_: int, main_path_: str = sys.path[0]) -> None:
        super().__init__(data_path_, generate_number_, main_path_)


    