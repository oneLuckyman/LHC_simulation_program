#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ast import keyword
from email import message
from lib2to3.pgen2.pgen import generate_grammar
from logging import WARNING
import os,sys,re
import pandas as pd 
import shutil 
import numpy as np 
import copy 
os.sys.path.append(os.path.join(sys.path[0], 'MC_sim_class'))
from MC_sim_class import MC_sim
from MC_sim_class import bcolors

'''
@作者:  贾兴隆
@说明:  本程序的目标功能是实现蒙特卡洛模拟LHC对撞实验的自动化，本系列文件为继Alpha,Beta,Gamma,Delta,Epsilon后的Zeta版本。
        由于程序整体的文件结构出现了重大变化，所以开始编写第六个大版本
        根据前五个版本的经验，整个自动化过程仍然使数据（类的属性）和要执行的动作（类的方法）分为三重大的类别：
            第一种类型：一旦进程启动轻易不会更改的属性和方法，例如主进程的目录，数据存放的目录，各个子程序的目录等等
            第二种类型：在单核的进程开始后，也就是当generate_numbers确定以后，不会再改变的数据和操作
            第三种类型：在单个参数点的计算开始后，也就是当generater_number确定以后，不会再改变的数据和操作
                这一种类型下还包括一种子类型，MadGraph类和CheckMATE类，这种子进程类可能会在第三种类型中多次调用，但每次实例化的过程相同。
            本文件包含第一种类型。
@开发日志：
        2022年4月22日：开始编写Zeta版本
'''

class Prepare_program(object):
    '''
    单个模拟进程开始前的准备工作。
    这个类中的方法只会在单个模拟进程开始前调用一次，一旦generate_numbers固定后这个类不会再发生改变，属于第二大类。
    '''
    def __init__(self) -> None:
        self._main_path = MC_sim._main_path                                                     #获得主目录
        self._data_path = MC_sim._data_path                                                     #获得数据目录
        self._process_name = MC_sim._process_name                                               #获得对应的进程序号
        self._MadGraph_path = MC_sim.MadGraph_path                                              #获得MadGraph的目录
        self._CheckMate_path = MC_sim.CheckMate_path                                            #获得CheckMate的目录
        self._Support_path = MC_sim.Support_path                                                #获得ck的目录
        self._result_path = MC_sim._result_path                                                 #获得结果目录
        self._info_name_list = MC_sim._info_name_list                                           #获得信息名称列表
        self._model_name = MC_sim._model_name                                                   #获得模型名称
        self._Event_root_path = MC_sim._Event_root_path                                         #获得存放madgraph的event文件的根目录
        self._Event_path = MC_sim._Event_path                                                   #获得madgraph的event文件存放的目录
        
        
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
                    generate_numbers = list(range(generate_number_range[0], generate_number_range[1] + 1, 1))              #获得要计算的目标参数点的序列
        return generate_numbers

    def refresh_ck_r(self) -> None:
        '''
        刷新ck_r.txt文件。ck_r.txt是存放CheckMATE结果的文件，每次运行程序时，都会将ck_r.txt清空，然后将结果写入ck_r.txt。
        '''
        os.chdir(self._Support_path)                                                     # 切换到ck结果存放路径
        os.system('rm -rf after_ck/ck_r.txt')                                       # 删除旧的ck结果文件
        #   !!!! 注意，以下内容旨在输出必要的数据，因此在不同的项目中极有可能不同 !!!!
        with open(os.path.join(self._Support_path, 'after_ck/ck_r.txt'), 'w') as ck_r:
            ck_r.write("{}\t{}\t{}\t{}\n".format("robs", "rexp", "robscons", "rexpcons"))
    
    def write_list_to_file(self, list, file) -> None:
        '''
        把一个列表的信息写入文件的第一行
        '''
        with open(file,'w') as f:
            for i in list:
                f.write(str(i)+'\t')
            f.write('\n')
    
    def refresh_results_file(self) -> None:
        '''
        刷新GridData.txt文件。这里存放着最终需要的所有数据。
        '''
        os.chdir(self._result_path)                                                             # 切换到结果存放路径
        os.system('rm -rf GridData.txt')                                                        # 删除旧的结果文件
        all_info_name = self._info_name_list + ["robs", "rexp", "robscons", "rexpcons"]         # 将所有信息名称和ck结果名称添加到一个列表中
        self.write_list_to_file(all_info_name,'GridData.txt')                                   # 将信息名称写入结果文件
        os.chdir(self._main_path)                                                               # 切换到主目录
    
    def refresh_event_file(self) -> None:
        # os.chdir(self._Event_path)                                                              # 切换到event文件存放路径
        # os.system('rm -rf ./*')                                                                 # 删除旧的event文件
        # os.chdir(self._main_path)                                                               # 切换到主目录
        pass
 
class Prepare_subprocess(object):
    '''
    用于准备和收尾各个子进程的类，通常generate_number确定后，这个类中的方法在指定位置只会调用一次，因此属于第三大类
    '''
    def __init__(self, generate_number_: int) -> None:
        self._main_path = MC_sim._main_path                                                     #获得主目录
        self._data_path = MC_sim._data_path                                                     #获得数据目录
        self._process_name = MC_sim._process_name                                               #获得对应的进程序号
        self._MadGraph_path = MC_sim.MadGraph_path                                              #获得MadGraph的目录
        self._CheckMate_path = MC_sim.CheckMate_path                                            #获得CheckMate的目录
        self._Support_path = MC_sim.Support_path                                                #获得ck的目录
        self._generate_number = generate_number_                                                #获得要计算的目标参数点
        self._result_path = MC_sim._result_path                                                 #获得结果目录
        self._info_name_list = MC_sim._info_name_list                                           #获得信息名称列表
        self._model_name = MC_sim._model_name                                                   #获得模型名称
        self._Event_root_path = MC_sim._Event_root_path                                         #获得event的根目录
        self._Event_path = MC_sim._Event_path                                                   #获得madgraph的event文件存放的目录

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
                with open("{}/param_card.dat".format(self._Event_path), 'w') as f2:                     # 写入param_card.dat文件
                    f2.write(f1.read())

            ## 注意 !!!!  以下代码用于获得proc_chi文件，在未来的工作中判断条件有可能会被更改。  !!!!
            if self._model_name == 'MSSM':
                os.system("cp {0}/proc/proc_mssm {0}/proc_chi".format(self._Event_path))
            elif self._model_name == 'NMSSM':
                if max(pow(data['N11'].iloc[self._generate_number-1], 2), pow(data['N12'].iloc[self._generate_number-1], 2), (pow(data['N13'].iloc[self._generate_number-1], 2) + pow(data['N14'].iloc[self._generate_number-1], 2)), pow(data['N15'].iloc[self._generate_number-1], 2)) == pow(data['N15'].iloc[self._generate_number-1], 2):  
                    os.system("cp {0}/proc/proc_n1 {0}/proc_chi".format(self._Event_path))
                if max(pow(data['N21'].iloc[self._generate_number-1], 2), pow(data['N22'].iloc[self._generate_number-1], 2), (pow(data['N23'].iloc[self._generate_number-1], 2) + pow(data['N24'].iloc[self._generate_number-1], 2)), pow(data['N25'].iloc[self._generate_number-1], 2)) == pow(data['N25'].iloc[self._generate_number-1], 2):
                    os.system("cp {0}/proc/proc_n2 {0}/proc_chi".format(self._Event_path))
                if max(pow(data['N31'].iloc[self._generate_number-1], 2), pow(data['N32'].iloc[self._generate_number-1], 2), (pow(data['N33'].iloc[self._generate_number-1], 2) + pow(data['N34'].iloc[self._generate_number-1], 2)), pow(data['N35'].iloc[self._generate_number-1], 2)) == pow(data['N35'].iloc[self._generate_number-1], 2):
                    os.system("cp {0}/proc/proc_n3 {0}/proc_chi".format(self._Event_path))
                if max(pow(data['N41'].iloc[self._generate_number-1], 2), pow(data['N42'].iloc[self._generate_number-1], 2), (pow(data['N43'].iloc[self._generate_number-1], 2) + pow(data['N44'].iloc[self._generate_number-1], 2)), pow(data['N45'].iloc[self._generate_number-1], 2)) == pow(data['N45'].iloc[self._generate_number-1], 2):
                    os.system("cp {0}/proc/proc_n4 {0}/proc_chi".format(self._Event_path))
                if max(pow(data['N51'].iloc[self._generate_number-1], 2), pow(data['N52'].iloc[self._generate_number-1], 2), (pow(data['N53'].iloc[self._generate_number-1], 2) + pow(data['N54'].iloc[self._generate_number-1], 2)), pow(data['N55'].iloc[self._generate_number-1], 2)) == pow(data['N55'].iloc[self._generate_number-1], 2):
                    os.system("cp {0}/proc/proc_n5 {0}/proc_chi".format(self._Event_path))

        os.chdir(self._Event_path)
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
            if self._model_name == 'MSSM':
                cs13chi_in = cs13chi_pb
            elif self._model_name == 'NMSSM':
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
            修改自@张迪的代码，用于处理Checkmate结果的函数
            详情咨询@张迪。
            '''
            os.chdir(self._Support_path)
            data = pd.read_csv("{}/ck_input.csv".format(self._data_path))
            Index = data['Index'].iloc[self._generate_number - 1]
            folder_dir = os.path.join(self._Support_path, 'after_ck/', str(self._generate_number))
            if not os.path.exists(folder_dir):
                os.makedirs(folder_dir)
            chi_save = os.path.abspath("{}/gnmssm_chi/Events/run_01/run_01_tag_1_banner.txt".format(self._Event_path))
            os.system("cp {} {}/{}_chi.banner.txt".format(chi_save, folder_dir, Index))
            smu_save = os.path.abspath("{}/gnmssm_smusmu/Events/run_01/run_01_tag_1_banner.txt".format(self._Event_path))
            os.system("cp {} {}/{}_smu.banner.txt".format(smu_save, folder_dir, Index))
            ck_dir = os.path.abspath("{}/../CheckMATE/CM_v2_26/results/".format(self._Support_path))
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
            return folder_dir, Index, max(robs), max(rexp), max(robscons), max(rexpcons)
        
        os.chdir(self._Support_path)                                                     # 切换到ck结果存放路径
        #   !!!! 注意，以下内容旨在输出必要的数据，因此在不同的项目中极有可能不同 !!!!
        folder_dir, self.Index, self.robs, self.rexp, self.robscons, self.rexpcons = after_ck(self)
        with open("{}/after_ck/ck_r.txt".format(self._Support_path), 'a') as ck_r:
            ck_r.write("{}\t{}\t{}\t{}\n".format(self.robs, self.rexp, self.robscons, self.rexpcons))
        os.chdir(self._main_path)
    
    def collect_result(self) -> None:
        '''
        收集单个参数点所有必要的数据
        '''
        def write_list_to_file(list,file) -> None:
            '''
            把一个列表的信息写入文件的末尾一行
            '''
            with open(file,'a') as f:
                for i in list:
                    f.write(str(i)+'\t')
                f.write('\n')
        
        os.chdir(self._result_path)                                                             # 切换到结果存放路径
        data_df = pd.read_csv("{}/ck_input.csv".format(self._data_path))                        # 读取ck_input.csv文件
        info_list = list(data_df[self._info_name_list].iloc[self._generate_number - 1])         # 获取该参数点的信息
        result_list = info_list + [self.robs, self.rexp, self.robscons, self.rexpcons]          # 将该参数点的信息和ck结果添加到result_list
        write_list_to_file(result_list, 'GridData.txt')                                         # 将result_list写入GridData.txt文件
        os.chdir(self._main_path)                                                               # 切换到主路径
        
class MadGraph(object):
    '''
    MadGraph类，获取单个MadGraph进程的信息，并调用MadGraph进程。
    '''
    def __init__(self, mg5_name_: str, mg5_category_: str, mg5_run_card_: str) -> None:
        '''
        mg5_name: 要执行的MadGraph程序的名字，如：'gnmssm_chi'，来源于proc_chi的最后一行output gnmssm_chi，放置在../Externals/Madgrapg/下。
        mg5_category: 要执行的MadGraph程序的类别，目前为止有两种类别，'EW'(electroweakinos)和'SL'(sleptons)。
        mg5_run_card: 要执行的MadGraph程序的run_card.dat的名字，如：'run_chi.dat'，放置在../Externals/Madgrapg/下。  
        '''
        self._main_path = MC_sim._main_path                                                                     #获得主目录
        self._process_name = MC_sim._process_name                                                               #对应的进程序号
        self._data_path = MC_sim._data_path                                                                     #获得数据目录
        self._MadGraph_path = MC_sim.MadGraph_path                                                              #获得MadGraph的目录
        self._CheckMate_path = MC_sim.CheckMate_path                                                            #获得CheckMate的目录
        self._Support_path = MC_sim.Support_path                                                                #获得ck的目录
        self._mg5_name = mg5_name_
        self._mg5_category = mg5_category_.upper()
        self._mg5_run_card = mg5_run_card_
        self._model_name = MC_sim._model_name                                                                   #获得模型名称
        self._Event_root_path = MC_sim._Event_root_path                                                         #获得event的根目录
        self._Event_path = os.path.join(MC_sim._Event_root_path, MC_sim._process_name)                          #获得madgraph的event文件存放的目录
        
    @property
    def mg5_name(self):
        '''
        获取mg5_name。
        '''
        return self._mg5_name

    @mg5_name.setter
    def mg5_name(self, mg5_name_: str):
        '''
        设置mg5_name。
        '''
        if not isinstance(mg5_name_, str):
            raise ValueError(bcolors.print_WARNING('Mg5 name path must be a string!!!'))                # 判断mg5_name是否为字符串
        self._mg5_name = mg5_name_

    @property
    def mg5_category(self):
        '''
        获取mg5_category。
        '''
        return self._mg5_category

    @mg5_category.setter
    def mg5_category(self, mg5_category_: str):
        '''
        设置mg5_category。
        '''
        if not isinstance(mg5_category_, str):
            raise ValueError(bcolors.print_WARNING('Mg5 category path must be a string!!!'))                # 判断mg5_category是否为字符串
        mg5_category_ = mg5_category_.upper()
        if mg5_category_ != 'EW' and mg5_category_ != 'SL':
            raise ValueError(bcolors.print_WARNING('Mg5 category must be EW or SL!!!'))                # 判断mg5_category是否为EW或SL
        self._mg5_category = mg5_category_

    @property
    def mg5_run_card(self):
        '''
        获取mg5_run_card。
        '''
        return self._mg5_run_card

    @mg5_run_card.setter
    def mg5_run_card(self, mg5_run_card_: str):
        '''
        设置mg5_run_card。
        '''
        if not isinstance(mg5_run_card_, str):
            raise ValueError(bcolors.print_WARNING('Mg5 run card path must be a string!!!'))                # 判断mg5_run_card是否为字符串
        self._mg5_run_card = mg5_run_card_

    def mg5_Execute(self) -> None:
        '''
        启动MadGraph程序，并获取结果。
        '''
        os.chdir(self._Event_path)
        if self._mg5_category == 'EW':
            os.system('rm -rf {}'.format(self._mg5_name))                                                                   # 删除上一次生成的文件夹
            os.system('{0}/MG5_aMC_v2_6_4/bin/mg5_aMC proc_chi'.format(self._MadGraph_path))                                # 启动MadGraph中生成相互作用过程的程序，产生“过程”文件，对应于mg5中的generate命令。这里的proc_chi是上一步生成的文件，如果需要改动这个文件的名字应该在上一步中改动。
        elif self._mg5_category == 'SL':
            os.system('rm -rf {0}/RunWeb {0}/index.html {0}/crossx.html {0}/HTML/* {0}/Events/*'.format(self._mg5_name))    # 删除上一次生成的文件，与EW不同的是，为了节省时间，SL的过程文件在运行了prepare.py之后已经生成过一次，因此只删除“过程”文件夹中必要的部分即可。
        os.system('cp param_card.dat pythia8_card.dat {0}/Cards/'.format(self._mg5_name))                                   # 将param_card.dat和pythia8_card.dat复制到mg5_name/Cards/下。
        os.system('cp {1} {0}/Cards/run_card.dat'.format(self._mg5_name, self._mg5_run_card))                               # 将mg5_run_card.dat复制到mg5_name/Cards/下。
        os.system('cp madevent_interface.py {0}/bin/internal/'.format(self._mg5_name))                                      # 将madevent_interface.py复制到mg5_name/bin/internal/下。该文件为提前生成的文件，初始位置放在MadGraph_path下。
        os.system('./{0}/bin/generate_events -f'.format(self._mg5_name))                                                    # 启动MadGraph中生成事例的程序，产生“事例”文件夹，对应于mg5中的launch命令。这也是单个MadGraph程序的最后一步。输出结果保存在mg5_name/Events/run_01/下。
        os.chdir(self._main_path)                                                                                           # 返回主目录。

    def remove_result(self) -> None:
        '''
        删除这一个MG5生成的结果
        '''
        os.chdir(self._MadGraph_path)
        os.remove(os.path.join(self._mg5_name, 'Events', 'run_01', 'tag_1_pythia8_events.hepmc'))                            # 删除这一个MG5生成的结果
        os.chdir(self._main_path)
    
    def pass_():
        pass

class CheckMATE(object):
    '''
    CheckMATE类，获取单个CheckMATE进程的信息，并调用CheckMATE进程。
    '''
    def __init__(self, CM_input_name_: str, mg5_name_: str, XSect_name_: str, XSect_replace_: str) -> None:
        self._main_path = MC_sim._main_path                                                                     #获得主目录
        self._process_name = MC_sim._process_name                                                               #对应的进程序号
        self._data_path = MC_sim._data_path                                                                     #获得数据目录
        self._MadGraph_path = MC_sim.MadGraph_path                                                              #获得MadGraph的目录
        self._CheckMate_path = MC_sim.CheckMate_path                                                            #获得CheckMate的目录
        self._Support_path = MC_sim.Support_path                                                                #获得ck的目录
        self._CM_input_name = CM_input_name_                                                                    #获取CheckMATE输入文件名。
        self._mg5_name = mg5_name_                                                                              #获取CheckMATE输入所需的MG5文件名。
        self._XSect_name = XSect_name_                                                                          #获取XSect输入文件名。
        self._XSect_replace = XSect_replace_                                                                    #获取XSect替换字典。
        self._model_name = MC_sim._model_name                                                                   #获得模型名称
        self._Event_root_path = MC_sim._Event_root_path                                                         #获得event的根目录
        self._Event_path = os.path.join(MC_sim._Event_root_path, MC_sim._process_name)                          #获得madgraph的event文件存放的目录
    
    @property 
    def CM_input_name(self):
        '''
        获取CM_input_name。
        '''
        return self._CM_input_name
        
    @CM_input_name.setter
    def CM_input_name(self, CM_input_name_: str):
        '''
        设置CM_input_name。
        '''
        if not isinstance(CM_input_name_, str):
            raise ValueError(bcolors.print_WARNING('CM input name must be a string!!!'))                            # 判断CM_input_name是否为字符串
        self._CM_input_name = CM_input_name_

    @property
    def XSect_name(self):
        '''
        获取XSect_name。
        '''
        return self._XSect_name

    @XSect_name.setter
    def XSect_name(self, XSect_name_: str):
        '''
        设置XSect_name。
        '''
        if not isinstance(XSect_name_, str):
            raise ValueError(bcolors.print_WARNING('XSect name must be a string!!!'))                                # 判断XSect_name是否为字符串
        self._XSect_name = XSect_name_

    @property
    def XSect_replace(self):
        '''
        获取XSect_replace。
        '''
        return self._XSect_replace

    @XSect_replace.setter
    def XSect_replace(self, XSect_replace_: str):
        '''
        设置XSect_replace。
        '''
        if not isinstance(XSect_replace_, str):
            raise ValueError(bcolors.print_WARNING('XSect replace must be a string!!!'))                              # 判断XSect_replace是否为字符串
        self._XSect_replace = XSect_replace_

    def CM_Execute(self) -> None:
        '''
        执行CheckMATE程序。
        首先是生成输入文件，替换关键字符串成截面数据，然后执行CheckMATE程序。
        '''
        def get_XSect_number(self) -> None:
            '''
            读取/Externals/ck/ck_input.dat中的XSect信息,获取截面信息。
            '''
            ck_input_df = pd.read_csv(os.path.join(self._Support_path, 'ck_input.dat'), sep='\s+', dtype=str)   # 读取ck_input.dat文件。
            self._XSect_number = ck_input_df.loc[0, self._XSect_name]                                           # 获取Xsect的值。

        def replace_Xsect(self) -> None:
            '''
            进入到CheckMATE_path/bin/下，对CM_input_name文件中截面位置的关键字进行替换操作，并且生成一个备份文件在计算完毕后再还原回来。
            '''
            CM_inputfile_path = os.path.join(self._CheckMate_path, './bin')     # 获取CheckMATE输入文件的路径。
            os.chdir(CM_inputfile_path)                             # 切换到CheckMATE输入文件的路径下。
            backup_file = self._CM_input_name + '.bak'              # 创建一个备份文件。
            temp_file = self._CM_input_name + '.tmp'                # 创建一个临时文件。
            if not os.path.exists(backup_file):
                shutil.copy2(self._CM_input_name, backup_file)                                                                 # 创建备份文件。
                with open(self._CM_input_name, mode = 'r') as fr, open(temp_file, mode = 'w') as fw:
                    for line in fr:
                        fw.write(line.replace(self._XSect_replace, self._XSect_number))                                        # 替换截面位置的关键字。
                os.remove(self._CM_input_name)                                                                                 # 删除原文件。
                os.rename(temp_file, self._CM_input_name)                                                                      # 重命名临时文件。
                os.chdir(self._main_path)                                                                                      # 返回主目录。

        def restore_CM_inputfile(self) -> None:
            '''
            进入到CheckMATE_path/bin/下，还原CheckMATE输入文件。
            '''
            CM_inputfile_path = os.path.join(self._CheckMate_path, './bin')     # 获取CheckMATE输入文件的路径。
            os.chdir(CM_inputfile_path)                                         # 切换到CheckMATE输入文件的路径下。
            backup_file = self._CM_input_name + '.bak'                          # 告知备份文件名。
            os.remove(self._CM_input_name)                                      # 删除原文件。
            os.rename(backup_file, self._CM_input_name)                         # 重命名备份文件。
            os.chdir(self._main_path)                                           # 返回主目录。

        def specify_event_path(self) -> None:
            '''
            为Checkmate的输入文件指定event
            '''
            CM_inputfile_path = os.path.join(self._CheckMate_path, './bin')                                             # 获取CheckMATE输入文件的路径。
            os.chdir(CM_inputfile_path)                                                                                 # 切换到CheckMATE输入文件的路径下。
            P8_event_path = "Events/run_01/tag_1_pythia8_events.hepmc"
            with open(self._CM_input_name, mode = 'a') as ck_input_file:
                ck_input_file.write("Events: " + os.path.join(self._Event_path, self._mg5_name, P8_event_path))         # 为CheckMATE的输入文件指定event路径。
            os.chdir(self._main_path)                                                                                   # 返回主目录。

        get_XSect_number(self)                                                      # 从ck_input.dat中获取XSect。
        replace_Xsect(self)                                                         # 替换CheckMATE输入文件中的XSect。
        specify_event_path(self)                                                    # 为Checkmate的输入文件指定event。
        os.chdir(self._CheckMate_path)                                              # 切换到CheckMATE_path目录下。
        os.system('./bin/CheckMATE bin/{}'.format(self._CM_input_name))             # 执行CheckMATE程序。
        os.chdir(self._main_path)                                                   # 返回主目录。
        restore_CM_inputfile(self)                                                  # 恢复CheckMATE输入文件。


if __name__ == '__main__':
    #测试一个进程

    #Prepare_program 
    prepare_program = Prepare_program()
    generate_numbers = prepare_program.get_generate_numbers_from_ck_ini()
    prepare_program.refresh_ck_r()
    prepare_program.refresh_results_file() 

    for generate_number in generate_numbers:
        ## prepare_subprocess
        prepare_subprocess = Prepare_subprocess(generate_number)
        prepare_subprocess.prepare_MadGraph()
        prepare_subprocess.prepare_CheckMATE()
        prepare_subprocess.remove_old_CM_result()

        ## Execute
        mg5_gnmssm_chi = MadGraph('gnmssm_chi', 'ew', 'run_chi.dat')
        mg5_gnmssm_chi.mg5_Execute()
        CM_gnmssm_chi = CheckMATE('gnmssm_chi.dat', 'gnmssm_chi', 'cs13chi_in', 'ES_cs13chi')
        CM_gnmssm_chi.CM_Execute()
        # mg5_gnmssm_chi.remove_result()

        mg5_gnmssm_smusmu = MadGraph('gnmssm_smusmu', 'SL', 'run_smu.dat')
        mg5_gnmssm_smusmu.mg5_Execute()
        CM_gnmssm_smusmu = CheckMATE('gnmssm_smusmu.dat', 'gnmssm_smusmu', 'cs13smu_pb', 'ES_cs13smu')
        CM_gnmssm_smusmu.CM_Execute()
        # mg5_gnmssm_smusmu.remove_result()

        ## end
        prepare_subprocess.after_ck_Execute()
        # prepare_subprocess.remove_old_CM_result()
        prepare_subprocess.collect_result()