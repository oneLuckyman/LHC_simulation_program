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
            本文件包含第二种和第三种类型。
@开发日志：
        2022年4月6日：开始编写MC_sim_class.py
'''

