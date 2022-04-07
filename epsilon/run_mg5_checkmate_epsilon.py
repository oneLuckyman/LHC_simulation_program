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
from MC_sim_class import MC_sim

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
        2022年4月7日：MC_sim_class.py编写完毕，开始编写Prepare_program类，Prepare_subprocess类，MadGraph类
'''

class Prepare_program(object):
    '''
    单个模拟进程开始前的准备工作。
    这个类中的方法只会在单个模拟进程开始前调用一次，一旦generate_numbers固定后这个类不会再发生改变。
    '''
    def __init__(self) -> None:
        self._main_path = sys.path[0]
        

    def get_generate_numbers_from_ck_ini(self) -> list:
        '''
        输入一个ck.ini文件，并获取本次进程所需的所有generate_numbers。
        '''
        search_keyword = 'Input parameters:'
        with open('{}/ck.ini'.format(self._main_path)) as ck_ini:       #本文件同目录下存在一个ck.ini文件，这是一个easyscan配置文件，其中包含了要执行的单个进程所需的所有信息。旧的程序正是依赖easyscan运行的。
            for line in ck_ini:
                if search_keyword in line:
                    ck_ini_message = re.split(r'[\s\,]+', line)         #本程序所需的ck.ini中的信息是，要计算的目标参数点所对应的ck_input.csv的行数
                    generate_number_range = [int(round(float(ck_ini_message[-4]))),int(round(float(ck_ini_message[-3])))]   #获得要计算的目标参数点的范围
                    generate_numbers = list(range(generate_number_range[0] - 1, generate_number_range[1], 1))              #获得要计算的目标参数点的序列
        return generate_numbers

class Prepare_subprocess(object):
    '''
    用于准备和收尾各个子进程的类，通常generate_number确定后，这个类中的方法在指定位置只会调用一次
    '''
    def __init__(self, generate_number_) -> None:
        self._main_path = MC_sim._main_path                                                                     #获得主目录
        self._data_path = MC_sim._data_path_                                                                    #获得数据目录
        self._MadGraph_path = os.path.join(self._main_path, '../Externals/MadGraph/')                           #获得MadGraph的目录
        self._CheckMate_path = os.path.join(self._main_path, '../Externals/CheckMATE/CM_v2_26/')                #获得CheckMate的目录
        self._Support_path = os.path.join(self._main_path, '../Externals/ck/')                                  #获得ck的目录
        self._generate_number = generate_number_                                                                #获得要计算的目标参数点

    def prepare_MadGraph(self) -> None:
        '''
        准备MadGraph的param_card.dat输入文件以及proc_chi输入文件
        '''
        def pre_generate(self) -> None:
            '''
            修改自@张迪的代码，用于准备MadGraph的param_card.dat输入文件以及proc_chi输入文件。proc_chi是generate EW过程文件的输入文件 
            param_card.dat文件来自于一个Spectrum文件的修改。
            proc_chi来源于MadGraph_path/proc/proc_n*文件，其中n*是neutralino*。
            至于为什么判断条件如此设置，请咨询@张迪，后续@贾兴隆会尽可能添加解释。
            '''
            data = pd.read_csv("{}/ck_input.csv".format(self._data_path))                                           # 读取ck_input.csv文件
            Index = data['Index'].iloc[self._generate_number-1]                                                     # 获取Spectrum的Index
            with open("{}/muonSPhenoSPC_1/SPhenoSPC_{}.txt".format(self._data_path, str(Index)), 'r') as f1:        # 读取Spectrum文件
                with open("{}/../Madgraph/param_card.dat".format(self._Support_path), 'w') as f2:                    # 写入param_card.dat文件
                    f2.write(f1.read())


            ## 注意 !!!!  以下代码用于获得proc_chi文件，在未来的工作中判断条件有可能会被更改。  !!!!
            if max(pow(data['N11'].iloc[self._generate_number-1], 2), pow(data['N12'].iloc[self._generate_number-1], 2), (pow(data['N13'].iloc[self._generate_number-1], 2) + pow(data['N14'].iloc[self._generate_number-1], 2)), pow(data['N15'].iloc[self._generate_number-1], 2)) == pow(data['N15'].iloc[self._generate_number-1], 2):  
                os.system("cp {}/../Madgraph/proc/proc_n1 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))
            if max(pow(data['N21'].iloc[self._generate_number-1], 2), pow(data['N22'].iloc[self._generate_number-1], 2), (pow(data['N23'].iloc[self._generate_number-1], 2) + pow(data['N24'].iloc[self._generate_number-1], 2)), pow(data['N25'].iloc[self._generate_number-1], 2)) == pow(data['N25'].iloc[self._generate_number-1], 2):
                os.system("cp {}/../Madgraph/proc/proc_n2 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))
            if max(pow(data['N31'].iloc[self._generate_number-1], 2), pow(data['N32'].iloc[self._generate_number-1], 2), (pow(data['N33'].iloc[self._generate_number-1], 2) + pow(data['N34'].iloc[self._generate_number-1], 2)), pow(data['N35'].iloc[self._generate_number-1], 2)) == pow(data['N35'].iloc[self._generate_number-1], 2):
                os.system("cp {}/../Madgraph/proc/proc_n3 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))
            if max(pow(data['N41'].iloc[self._generate_number-1], 2), pow(data['N42'].iloc[self._generate_number-1], 2), (pow(data['N43'].iloc[self._generate_number-1], 2) + pow(data['N44'].iloc[self._generate_number-1], 2)), pow(data['N45'].iloc[self._generate_number-1], 2)) == pow(data['N45'].iloc[self._generate_number-1], 2):
                os.system("cp {}/../Madgraph/proc/proc_n4 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))
            if max(pow(data['N51'].iloc[self._generate_number-1], 2), pow(data['N52'].iloc[self._generate_number-1], 2), (pow(data['N53'].iloc[self._generate_number-1], 2) + pow(data['N54'].iloc[self._generate_number-1], 2)), pow(data['N55'].iloc[self._generate_number-1], 2)) == pow(data['N55'].iloc[self._generate_number-1], 2):
                os.system("cp {}/../Madgraph/proc/proc_n5 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))

        os.chdir(self._Support_path)
        os.system('rm -rf ../Madgraph/param_card.dat')                              # 删除原有的param_card.dat文件
        os.system('rm -rf ../Madgraph/proc_chi')                                    # 删除原有的proc_chi文件
        pre_generate(self)
        os.chdir(self._main_path)                                                   # 回到主目录

    def prepare_CheckMATE(self) -> None:
        '''
        修改自@张迪的代码，用于获得checkmate的输入数据，写进ck_input.dat里
        其中一个重要的输入是截面数据，cs13chi_pb需要进行一系列判断再决定具体的数值
        最终所有输入数据都被写入ck_input.dat文件中，供下一步使用
        '''
        def ck_input(self) -> float:
            data = pd.read_csv("{}/ck_input.csv".format(self._data_path))                                           # 读取ck_input.csv文件

            ## 注意 !!!!  以下代码用于获得checkmate的输入参数，在未来的工作中有可能会被更改，届时可能会作为该函数的输入进一步强化程序的灵活性  !!!!

            Index = data['Index'].iloc[self._generate_number-1]                                                     # 获取Spectrum的Index
            r_smodels = data['r_smodels'].iloc[self._generate_number-1]                                             # 获取Spectrum的r_smodels
            cs13chi_pb = data['cs13chi_pb'].iloc[self._generate_number-1]                                           # 获取Spectrum的cs13chi_pb，该数字是EW的产生截面数据。在作为checkmate输入数值之前，该截面还需要进一步计算。
            cs13smu_in = data['cs13smu_pb'].iloc[self._generate_number-1]                                           # 获取Spectrum的cs13smu_pb，该数字是SM的产生截面数据，是checkmate的重要输入数值。
            if max(pow(data['N11'].iloc[self._generate_number-1], 2), pow(data['N12'].iloc[self._generate_number-1], 2), (pow(data['N13'].iloc[self._generate_number-1], 2) + pow(data['N14'].iloc[self._generate_number-1], 2)), pow(data['N15'].iloc[self._generate_number-1], 2)) == pow(data['N15'].iloc[self._generate_number-1], 2):
                cs13chi_in = cs13chi_pb
            if max(pow(data['N21'].iloc[self._generate_number-1], 2), pow(data['N22'].iloc[self._generate_number-1], 2), (pow(data['N23'].iloc[self._generate_number-1], 2) + pow(data['N24'].iloc[self._generate_number-1], 2)), pow(data['N25'].iloc[self._generate_number-1], 2)) == pow(data['N25'].iloc[self._generate_number-1], 2):
                cs13chi_in = cs13chi_pb - (data['c1barn2_pb'].iloc[self._generate_number-1] + data['c1n2_pb'].iloc[self._generate_number-1] + data['c2barn2_pb'].iloc[self._generate_number-1] + data['c2n2_pb'].iloc[self._generate_number-1] + data['n2n2_pb'].iloc[self._generate_number-1] + data['n2n3_pb'].iloc[self._generate_number-1] + data['n2n4_pb'].iloc[self._generate_number-1] + data['n2n5_pb'].iloc[self._generate_number-1])
            if max(pow(data['N31'].iloc[self._generate_number-1], 2), pow(data['N32'].iloc[self._generate_number-1], 2), (pow(data['N33'].iloc[self._generate_number-1], 2)+ pow(data['N34'].iloc[self._generate_number-1], 2)), pow(data['N35'].iloc[self._generate_number-1], 2)) == pow(data['N35'].iloc[self._generate_number-1], 2):
                cs13chi_in = cs13chi_pb - (data['c1barn3_pb'].iloc[self._generate_number-1] + data['c1n3_pb'].iloc[self._generate_number-1] + data['c2barn3_pb'].iloc[self._generate_number-1] + data['c2n3_pb'].iloc[self._generate_number-1] + data['n3n3_pb'].iloc[self._generate_number-1] + data['n2n3_pb'].iloc[self._generate_number-1] + data['n3n4_pb'].iloc[self._generate_number-1] + data['n3n5_pb'].iloc[self._generate_number-1])
            if max(pow(data['N41'].iloc[self._generate_number-1], 2), pow(data['N42'].iloc[self._generate_number-1], 2), (pow(data['N43'].iloc[self._generate_number-1], 2) + pow(data['N44'].iloc[self._generate_number-1], 2)), pow(data['N45'].iloc[self._generate_number-1], 2)) == pow(data['N45'].iloc[self._generate_number-1], 2):
                cs13chi_in = cs13chi_pb - (data['c1barn4_pb'].iloc[self._generate_number-1] + data['c1n4_pb'].iloc[self._generate_number-1] + data['c2barn4_pb'].iloc[self._generate_number-1] + data['c2n4_pb'].iloc[self._generate_number-1] + data['n4n4_pb'].iloc[self._generate_number-1] + data['n2n4_pb'].iloc[self._generate_number-1] + data['n3n4_pb'].iloc[self._generate_number-1] + data['n4n5_pb'].iloc[self._generate_number-1])
            if max(pow(data['N51'].iloc[self._generate_number-1], 2), pow(data['N52'].iloc[self._generate_number-1], 2), (pow(data['N53'].iloc[self._generate_number-1], 2) + pow(data['N54'].iloc[self._generate_number-1], 2)), pow(data['N55'].iloc[self._generate_number-1], 2)) == pow(data['N55'].iloc[self._generate_number-1], 2):
                cs13chi_in = cs13chi_pb - (data['c1barn5_pb'].iloc[self._generate_number-1] + data['c1n5_pb'].iloc[self._generate_number-1] + data['c2barn5_pb'].iloc[self._generate_number-1] + data['c2n5_pb'].iloc[self._generate_number-1] + data['n5n5_pb'].iloc[self._generate_number-1] + data['n2n5_pb'].iloc[self._generate_number-1] + data['n3n5_pb'].iloc[self._generate_number-1] + data['n4n5_pb'].iloc[self._generate_number-1])
            return Index, r_smodels, cs13chi_in, cs13smu_in, cs13chi_pb

        os.chdir(self._Support_path)
        os.system('rm -rf ck_input.dat')                                                                                # 删除旧的ck_input.dat文件
        Index, r_smodels, cs13chi_in, cs13smu_in, cs13chi_pb = ck_input(self)
        with open('ck_input.dat', 'w') as ck_input_file:
            ck_input_file.write("Index\tr_smodels\tcs13chi_in\tcs13smu_pb\tcs13chi_pb\n")                               # 写入ck_input.dat文件
            ck_input_file.write("{}\t{}\t{}\t{}\t{}\n".format(Index, r_smodels, cs13chi_in, cs13smu_in, cs13chi_pb))    # 写入ck_input.dat文件
        os.chdir(self._main_path)                                                                                       # 返回主目录

    def remove_old_CM_result(self) -> None:
        '''
        删除旧的CheckMate结果
        '''
        if os.path.exists(os.path.join(self._CheckMate_path, 'results/')):
            shutil.rmtree(os.path.join(self._CheckMate_path, 'results/'))
        else:
            pass 

    def after_ck_Execute(self) -> None:
        '''
        在单次进程所有的CheckMate程序运行完成后，进行一些结果收集操作，结果存放在了ck_r.txt文件中
        '''
        def after_ck(self) -> float:
            '''
            修改自@张迪的代码，用于Checkmate结果处理函数
            详情咨询@张迪。
            '''
            after_ck_path = os.path.join(self._main_path, '../Externals/ck/')
            os.chdir(after_ck_path)
            data = pd.read_csv("{}/ck_input.csv".format(self._data_path))
            Index = data['Index'].iloc[self._generate_number - 1]
            folder_dir = "{}/after_ck/{}".format(after_ck_path, self._generate_number)
            if not os.path.exists(folder_dir):
                os.makedirs(folder_dir)
            chi_save = os.path.abspath("{}/../Madgraph/gnmssm_chi/Events/run_01/run_01_tag_1_banner.txt".format(after_ck_path))
            os.system("cp {} {}/{}_chi.banner.txt".format(chi_save, folder_dir, Index))
            smu_save = os.path.abspath("{}/../Madgraph/gnmssm_smusmu/Events/run_01/run_01_tag_1_banner.txt".format(after_ck_path))
            os.system("cp {} {}/{}_smu.banner.txt".format(smu_save, folder_dir, Index))
            ck_dir = os.path.abspath("{}/../CheckMATE/CM_v2_26/results/".format(after_ck_path))
            os.system("cp -r {}/gnmssm {}/{}_ck".format(ck_dir, folder_dir, Index))
            os.system("rm -rf {}/{}_ck/mg5amcatnlo/".format(folder_dir, Index))
            def turn(datalist):
                return np.array(list(map(float, list(copy.copy(datalist)))))
            def index_item(ite, itelis):
                return list(itelis).index(ite)
            def loaddata(data):
                #analysis_ind = index_item("analysis", data[0, :])
                #sr_ind = index_item("sr", data[0, :])
                s_ind = index_item("s", data[0, :])
                #s95_ind = index_item("s95obs", data[0, :])
                s95obs_ind = index_item("s95obs", data[0, :])
                s95exp_ind = index_item("s95exp", data[0, :])
                #analysis = turn(data[1:, analysis_ind])
                #sr = turn(data[1:, sr_ind])
                s = turn(data[1:, s_ind])
                s95obs = turn(data[1:, s95obs_ind])
                s96exp = turn(data[1:, s95exp_ind])
                robscons_ind = index_item("robscons", data[0, :])
                robscons = turn(data[1:, robscons_ind])
                rexpcons_ind = index_item("rexpcons", data[0, :])
                rexpcons = turn(data[1:, rexpcons_ind])
                return s, s95obs, s96exp, s/s95obs, s/s96exp, robscons, rexpcons
            if not os.path.exists("{}/gnmssm/evaluation/total_results.txt".format(ck_dir)):
                s=s95obs=s95exp=robs=rexp=robscons=rexpcons  = turn([-1,-3])
            else:
                data_ck = np.loadtxt("{}/gnmssm/evaluation/total_results.txt".format(ck_dir), dtype=str)
                s, s95obs, s95exp, robs, rexp, robscons, rexpcons = loaddata(data_ck)
            #data_ck_cms = np.loadtxt("{}/ck_cms/evaluation/total_results.txt".format(ck_dir), dtype=str)
            #s_cms, s95obs_cms, s95exp_cms, robs_cms, rexp_cms, robscons_cms, rexpcons_cms = loaddata(data_ck_cms)
            # os.system("rm -rf {}/*".format(ck_dir))
            return folder_dir, max(robs), max(rexp), max(robscons), max(rexpcons)
        
        os.chdir(self._Support_path)                                                     # 切换到ck结果存放路径
        #   !!!! 注意，以下内容旨在输出必要的数据，因此在不同的项目中极有可能不同 !!!!
        folder_dir, robs, rexp, robscons, rexpcons = after_ck(self)
        with open("{}/after_ck/ck_r.txt".format(self._Support_path), 'a') as ck_r:
            ck_r.write("{}\t{}\t{}\t{}\n".format(robs, rexp, robscons, rexpcons))
        os.chdir(self._main_path)

class MadGraph(object):
    '''
    MadGraph类，获取单个MadGraph进程的信息，并调用MadGraph进程。
    '''
    def __init__(self, generate_number_) -> None:
        self._main_path = MC_sim._main_path                                                                     #获得主目录
        self._data_path = MC_sim._data_path_                                                                    #获得数据目录
        self._MadGraph_path = os.path.join(self._main_path, '../Externals/MadGraph/')                           #获得MadGraph的目录
        self._CheckMate_path = os.path.join(self._main_path, '../Externals/CheckMATE/CM_v2_26/')                #获得CheckMate的目录
        self._Support_path = os.path.join(self._main_path, '../Externals/ck/')                                  #获得ck的目录
        self._generate_number = generate_number_

    def prepare_MadGraph(self) -> None:
        '''
        准备MadGraph的param_card.dat输入文件以及proc_chi输入文件
        '''
        def pre_generate(self) -> None:
            '''
            修改自@张迪的代码，用于准备MadGraph的param_card.dat输入文件以及proc_chi输入文件。proc_chi是generate EW过程文件的输入文件 
            param_card.dat文件来自于一个Spectrum文件的修改。
            proc_chi来源于MadGraph_path/proc/proc_n*文件，其中n*是neutralino*。
            至于为什么判断条件如此设置，请咨询@张迪，后续@贾兴隆会尽可能添加解释。
            '''
            data = pd.read_csv("{}/ck_input.csv".format(self._data_path))                                           # 读取ck_input.csv文件
            Index = data['Index'].iloc[self._generate_number-1]                                                     # 获取Spectrum的Index
            with open("{}/muonSPhenoSPC_1/SPhenoSPC_{}.txt".format(self._data_path, str(Index)), 'r') as f1:        # 读取Spectrum文件
                with open("{}/../Madgraph/param_card.dat".format(self._Support_path), 'w') as f2:                    # 写入param_card.dat文件
                    f2.write(f1.read())


            ## 注意 !!!!  以下代码用于获得proc_chi文件，在未来的工作中判断条件有可能会被更改。  !!!!
            if max(pow(data['N11'].iloc[self._generate_number-1], 2), pow(data['N12'].iloc[self._generate_number-1], 2), (pow(data['N13'].iloc[self._generate_number-1], 2) + pow(data['N14'].iloc[self._generate_number-1], 2)), pow(data['N15'].iloc[self._generate_number-1], 2)) == pow(data['N15'].iloc[self._generate_number-1], 2):  
                os.system("cp {}/../Madgraph/proc/proc_n1 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))
            if max(pow(data['N21'].iloc[self._generate_number-1], 2), pow(data['N22'].iloc[self._generate_number-1], 2), (pow(data['N23'].iloc[self._generate_number-1], 2) + pow(data['N24'].iloc[self._generate_number-1], 2)), pow(data['N25'].iloc[self._generate_number-1], 2)) == pow(data['N25'].iloc[self._generate_number-1], 2):
                os.system("cp {}/../Madgraph/proc/proc_n2 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))
            if max(pow(data['N31'].iloc[self._generate_number-1], 2), pow(data['N32'].iloc[self._generate_number-1], 2), (pow(data['N33'].iloc[self._generate_number-1], 2) + pow(data['N34'].iloc[self._generate_number-1], 2)), pow(data['N35'].iloc[self._generate_number-1], 2)) == pow(data['N35'].iloc[self._generate_number-1], 2):
                os.system("cp {}/../Madgraph/proc/proc_n3 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))
            if max(pow(data['N41'].iloc[self._generate_number-1], 2), pow(data['N42'].iloc[self._generate_number-1], 2), (pow(data['N43'].iloc[self._generate_number-1], 2) + pow(data['N44'].iloc[self._generate_number-1], 2)), pow(data['N45'].iloc[self._generate_number-1], 2)) == pow(data['N45'].iloc[self._generate_number-1], 2):
                os.system("cp {}/../Madgraph/proc/proc_n4 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))
            if max(pow(data['N51'].iloc[self._generate_number-1], 2), pow(data['N52'].iloc[self._generate_number-1], 2), (pow(data['N53'].iloc[self._generate_number-1], 2) + pow(data['N54'].iloc[self._generate_number-1], 2)), pow(data['N55'].iloc[self._generate_number-1], 2)) == pow(data['N55'].iloc[self._generate_number-1], 2):
                os.system("cp {}/../Madgraph/proc/proc_n5 {}/../Madgraph/proc_chi".format(self._Support_path, self._Support_path))

        os.chdir(self._Support_path)
        os.system('rm -rf ../Madgraph/param_card.dat')                              # 删除原有的param_card.dat文件
        os.system('rm -rf ../Madgraph/proc_chi')                                    # 删除原有的proc_chi文件
        pre_generate(self)
        os.chdir(self._main_path)                                                   # 回到主目录

