#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
@作者:  贾兴隆
@说明:  本程序的目标功能是实现蒙特卡洛模拟LHC对撞实验的自动化，与上个系列不同，该系列程序将囊括从准备到收集结果的所有步骤，同时支持多核运行并最大程度保持灵活性。
    类的设置仍然分为三大类：
        第一大类：应用于全局的类，一旦项目开始就不再变化的数据和方法
        第二大类：应用于项目中每个进程的类，一旦一个进程开始就不再变化的数据和方法，或者说generate_numbers一旦确定就不再变化的类
        第三大类：应用于每个进程的每个循环的类，一旦一个循环开始就不再变化的数据和方法，或者说generate_number一旦确定就不再变化的类

    起始于根目录级的主要文件结构：
        MC_data/:                           # 用于存放所有的数据文件，原gnmssm文件夹
            ck_input.csv                        # 存放所有Checkmate可能的输入数据的文件
            muonSPhenoSPC_1/                    # 存放所有SPheno输出谱的文件夹
            slhaReaderOutPut.csv                # 存放所有SPheno输出数据的文件
            ck/                                 # 存放Checkmate输出数据的文件夹
                h1/                                 # 收集不同批次Checkmate数据的子文件夹
                h2/                                 # 同上

        Project_prepare/:                    # 存放着所有用于准备一个新项目的文件
            CM_v2_26.tar.gz                     # Checkmate的tar包
            MG5_aMC_v2_6_4.tar.gz               # MG5_aMC的tar包
            mg5_configuration.txt               # MG5_aMC的配置文件
            installP8                           # 安装Pythia8的脚本
            madevent_interface.py               # madevent的接口文件
            pythia8_card.dat                    # Pythia8的配置文件
            proc/                               # 存放generate events脚本的文件夹
                proc_n1                             # generate events的脚本
                proc_n2                             # generate events的脚本
                proc_n3                             # generate events的脚本
                proc_n4                             # generate events的脚本
                proc_n5                             # generate events的脚本
                proc_mssm                           # generate events的脚本
            proc_smusmu                         # generate events的脚本
            run_chi.dat                         # 事例模拟所需要的run_card.dat模板文件
            run_smu.dat                         # 事例模拟所需要的run_card.dat模板文件
            gnmssm_chi.dat                      # checkmate输入模板文件
            gnmssm_smusmu.dat                   # checkmate输入模板文件

        process_*/:                           # 单一的进程文件夹，项目调用多少进程就会有多少个这样的文件夹，下面的所有文件夹都是针对单一进程的
            CheckMATE/                          # 存放所有与Checkmate有关系的文件
                ck_input.dat                        # Checkmate输入数据文件
                CM_v2_26/                           # Checkmate主程序文件夹
                    bin/                              # Checkmate启动文件所在的文件夹
                        gnmssm_chi.dat                  # Checkmate输入模板文件，从Project_prepare中复制而来
                        gnmssm_smusmu.dat               # Checkmate输入模板文件，从Project_prepare中复制而来
            Madgraph/                           # 存放所有与Madgraph有关系的文件
                MG5_aMC_v2_6_4/                     # Madgraph主程序文件夹
            Results/                            # 存放所有结果的文件夹
                GridData.txt                        # 存放所有收集的数值结果的文件
                after_ck/                           # 运行完Checkmate后收集的Madgraph结果和Checkmate结果
                    ck_r.txt                            # 存放Checkmate输出的结果
                    *index*/                            # 存放单个参数点的Madgraph结果和Checkmate结果，单一进程计算了多少个参数点就会有多少个
    
    游离于根目录级之外的文件夹，这些文件可以存放在任何路径下：
        process_*/:                          # 运行事例模拟以及存放事例模拟结果的文件夹，项目调用多少进程就会有多少个这样的文件夹，这个目录可以是任何名字，可以在任何路径下
            gnmssm_chi/                         # 模拟某一些过程的事例，这个例子中是与chi有关的
            gnmssm_smusmu/                      # 模拟某一些过程的事例，这个例子中是与smu有关的
            template/                           # 所有运行事例模拟所需要的模板文件，从Project_prepare中复制而来
                proc/                               # 存放generate events脚本的文件夹
                    proc_n1                             # generate events的脚本
                    proc_n2                             # generate events的脚本
                    proc_n3                             # generate events的脚本
                    proc_n4                             # generate events的脚本
                    proc_n5                             # generate events的脚本
                proc_chi                            # generate events的脚本
                proc_smusmu                         # generate events的脚本
                run_chi.dat                         # 事例模拟所需要的run_card.dat模板文件
                run_smu.dat                         # 事例模拟所需要的run_card.dat模板文件


@开发日志：
        2022年4月23日：开始编写程序的文档，说明文件结构
        2022年4月24日：文件结构说明完毕，Base_message类写完了
        2022年4月25日：Project_prepare类基本写完了
        2022年4月26日：编写了generate_number相关的方法
        2022年4月27日：编写了Process_prepare类
        2022年4月28日：添加了Support_subprocess类，编写了pre_generate方法
        2022年4月29日：修改了一些文件结构
        2022年5月1日：进一步修改了文件结构中不合理的部分
        2022年5月：一个月以来修正了一些路径错误，改动很小所以没有写入开发日志中。
        2022年5月29日：pre_generate中的错误已经全部修正
        2022年5月30日：编写了Support_subprocess类中的prepare_CheckMATE方法
'''


import argparse
import numpy as np
import pandas as pd
import os,sys,re
import shutil

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
ranks = comm.Get_size()

class Base_message(object):
    '''
    这个类包含了所有的基本信息
    属于第一大类
    '''
    def __init__(self, Event_root_path_, model_name_: str, size_: int, min_num_: int, max_num_: int, info_name_list_: list,
                        Madgraph_inputs: list, Checkmate_inputs: list,  
                        main_path_: str = sys.path[0], data_path_: str = 'MC_data/', project_prepare_path_: str = 'Project_prepare/', process_name_: str = 'process',
                        comm_ = MPI.COMM_WORLD, rank_ = comm.Get_rank(), ranks_ = comm.Get_size()) -> None:

        self.main_path = main_path_
        self.data_path = os.path.join(self.main_path, data_path_)
        self.data_df = pd.read_csv(os.path.join(self.data_path, 'ck_input.csv'))
        self.Event_root_path = Event_root_path_
        self.project_prepare_path = os.path.join(self.main_path, project_prepare_path_)
        self.model_name = model_name_
        self.size = size_
        self.all_generate_num = list(range(min_num_, max_num_))
        self.comm = comm_
        self.rank = rank_
        self.ranks = ranks_
        self.info_name_list = info_name_list_
        self.Madgraph_inputs = Madgraph_inputs
        self.Checkmate_inputs = Checkmate_inputs
        self.process_name = process_name_
        self.processes = self.get_process_name()
        self.generate_numbers_lst = self.get_generate_numbers_lst()
        self.process_paths = self.get_process_paths()
        self.Madgraph_paths = self.get_Madgraph_paths()
        self.CheckMATE_paths = self.get_CheckMATE_paths()
        self.Results_paths = self.get_Results_paths()
        self.after_ck_paths = self.get_after_ck_paths()
        self.Event_paths = self.get_Event_paths()
        self.Event_template_paths = self.get_Event_template_paths()

    def get_process_name(self) -> list:
        '''
        获得所有进程文件夹的名字
        '''
        process_names = []
        for i in range(self.size):
            process_names.append(self.process_name + '_' + str(i))
        return process_names
    
    def get_process_paths(self) -> list:
        '''
        获得所有进程文件夹的路径
        '''
        process_paths = []
        for i in range(self.size):
            process_paths.append(os.path.join(self.main_path, self.process_name + '_' + str(i)))
        return process_paths
    
    def get_generate_numbers_lst(self) -> list:
        '''
        将一个list分成数个list
        分配每个进程要计算的generate_numbers
        '''
        generate_numbers_lst = np.array_split(self.all_generate_num, self.size)
        return generate_numbers_lst

    def get_Madgraph_paths(self) -> list:
        '''
        获得所有Madgraph文件夹的路径
        '''
        MG5_paths = []
        for i in range(self.size):
            MG5_path = os.path.join(self.main_path, self.processes[i], 'Madgraph')
            MG5_paths.append(MG5_path)
        return MG5_paths
    
    def get_Checkmate_paths(self) -> list:
        '''
        获得所有Checkmate文件夹的路径
        '''
        CM_paths = []
        for i in range(self.size):
            CM_path = os.path.join(self.main_path, self.processes[i], 'CheckMATE')
            CM_paths.append(CM_path)
        return CM_paths

    def get_Results_paths(self) -> list:
        '''
        获得所有Results文件夹的路径
        '''
        Results_paths = []
        for i in range(self.size):
            Results_path = os.path.join(self.main_path, self.processes[i], 'Results/')
            Results_paths.append(Results_path)
        return Results_paths
    
    def get_after_ck_paths(self) -> list:
        '''
        获得所有after_ck文件夹的路径
        '''
        after_ck_paths = []
        for i in range(self.size):
            after_ck_path = os.path.join(self.main_path, self.processes[i], 'Results/', 'after_ck/')
            after_ck_paths.append(after_ck_path)
        return after_ck_paths
    
    def get_after_ck_paths(self) -> list:
        '''
        获得所有Results文件夹下的after_ck文件夹的路径
        '''
        after_ck_paths = []
        for i in range(self.size):
            after_ck_path = os.path.join(self.main_path, self.processes[i], 'Results', 'after_ck/')
            after_ck_paths.append(after_ck_path)
        return after_ck_paths

    def get_Event_paths(self) -> list:
        '''
        获得所有Event文件夹的路径
        '''
        Event_paths = []
        for i in range(self.size):
            Event_path = os.path.join(self.Event_root_path, self.processes[i])
            Event_paths.append(Event_path)
        return Event_paths
    
    def get_Event_template_paths(self) -> list:
        '''
        获得所有Event文件夹下存放所有模板的文件夹路径
        '''
        Event_template_paths = []
        for i in range(self.size):
            Event_template_path = os.path.join(self.Event_root_path, self.processes[i], 'template/')
            Event_template_paths.append(Event_template_path)
        return Event_template_paths

class Project_prepare(object):
    '''
    项目开始前的准备，包括文件结构的建立，程序的安装，各类输入文件的放置
    属于第一大类
    '''
    def __init__(self, base_message_: Base_message) -> None:
        self.base_message = base_message_

    def mkdirs(self, i: int) -> None:
        '''
        建立项目所需要的的文件结构
        '''
        if not os.path.exists(self.base_message.process_paths[i]):
            os.mkdir(self.base_message.process_paths[i])
        if not os.path.exists(self.base_message.Madgraph_paths[i]):
            os.mkdir(self.base_message.Madgraph_paths[i])
        if not os.path.exists(self.base_message.CheckMATE_paths[i]):
            os.mkdir(self.base_message.CheckMATE_paths[i])
        if not os.path.exists(self.base_message.Results_paths[i]):
            os.mkdir(self.base_message.Results_paths[i])
        if not os.path.exists(self.base_message.after_ck_paths[i]):
            os.mkdir(self.base_message.after_ck_paths[i])
        if not os.path.exists(self.base_message.Event_paths[i]):
            os.mkdir(self.base_message.Event_paths[i])
        if not os.path.exists(self.base_message.Event_template_paths[i]):
            os.mkdir(self.base_message.Event_template_paths[i])

    def install_Madgraph(self, i: int) -> None:
        '''
        安装Madgraph
        '''
        shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'MG5_aMC_v2_6_4.tar.gz'), self.base_message.Madgraph_paths[i])
        os.chdir(self.base_message.Madgraph_paths[i])
        os.system('tar -zxvf MG5_aMC_v2_6_4.tar.gz')
        os.system('rm -rf MG5_aMC_v2_6_4.tar.gz')
        os.chdir(self.base_message.project_prepare_path)
        os.system(os.path.join(self.base_message.Madgraph_paths[i], 'MG5_aMC_v2_6_4/bin/mg5_aMC installP8'))
        os.chdir(self.base_message.main_path)

        for Madgraph_input in self.base_message.Madgraph_inputs:
            if os.path.isdir(os.path.join(self.base_message.project_prepare_path, Madgraph_input)):
                shutil.copytree(os.path.join(self.base_message.project_prepare_path, Madgraph_input), os.path.join(self.base_message.Event_template_paths[i], Madgraph_input))
            elif os.path.isfile(os.path.join(self.base_message.project_prepare_path, Madgraph_input)):
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, Madgraph_input), self.base_message.Event_template_paths[i]) 
                
        os.chdir(self.base_message.Event_paths[i])
        os.system(os.path.join(self.base_message.Madgraph_paths[i], 'MG5_aMC_v2_6_4/bin/') + 'mg5_aMC proc_smusmu')
        os.chdir(self.base_message.main_path)

    def install_CheckMATE(self, i: int) -> None:
        '''
        安装CheckMATE，并把CheckMATE的输入文件复制到CheckMATE的运行目录下
        '''
        shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'CM_v2_26.tar.gz'), self.base_message.CheckMATE_paths[i])
        os.chdir(self.base_message.CheckMATE_paths[i])
        os.system('tar -zxvf CM_v2_26.tar.gz')
        os.system('rm -rf CM_v2_26.tar.gz')
        os.chdir('CM_v2_26')
        # 配置环境如果发生改变需要修改下面这一行中的路径
        os.system("./configure --with-rootsys=/opt/root-6.18.04/installdir --with-delphes=/opt/delphes_for_CheckMATE --with-pythia=/opt/pythia8245 --with-hepmc=/opt/HepMC-2.06.11")
        os.system('make -j 20')

        os.chdir(self.base_message.project_prepare_path)
        for CheckMATE_input in self.base_message.CheckMATE_inputs:
            if os.path.isdir(os.path.join(self.base_message.project_prepare_path, CheckMATE_input)):
                shutil.copytree(os.path.join(self.base_message.project_prepare_path, CheckMATE_input), os.path.join(self.base_message.CheckMATE_paths[i],'CM_v2_26','bin', CheckMATE_input))
            elif os.path.isfile(os.path.join(self.base_message.project_prepare_path, CheckMATE_input)):
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, CheckMATE_input), os.path.join(self.base_message.CheckMATE_paths[i],'CM_v2_26','bin'))
        os.chdir(self.base_message.main_path)


    def main(self) -> None:
        '''
        多核运行项目准备类
        '''
        for process_num in range(self.base_message.size):
            if self.rank == process_num:
                self.mkdirs(process_num)
                self.install_Madgraph(process_num)
                self.install_CheckMATE(process_num)


class Process_prepare(object):
    '''
    单个进程开始前的准备，包括获得generate_numbers,清洗单个进程内的旧文件,生成对应新文件
    属于第二大类
    '''
    def __init__(self, base_message_: Base_message, process_num_: int) -> None:
        '''
        process_num是进程的编号
        '''
        self.base_message = base_message_
        self.process_num = process_num_
        self.generate_numbers = self.base_message.generate_numbers_lst[self.process_num]

    def refresh_ck_r(self) -> None:
        '''
        刷新ck_r.txt文件。ck_r.txt是存放CheckMATE结果的文件，每次运行程序时，都会将ck_r.txt清空，然后将结果写入ck_r.txt。
        '''
        os.chdir(self.base_message.after_ck_paths[self.process_num])                                               # 切换到ck结果存放路径
        os.system('rm -rf after_ck/ck_r.txt')                                                       # 删除旧的ck结果文件
        #   !!!! 注意，以下内容旨在输出必要的数据，因此在不同的项目中极有可能不同 !!!!
        with open(os.path.join(self.base_message.after_ck_paths[self.process_num], 'ck_r.txt'), 'w') as ck_r:
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
        all_info_name = self.info_name_list + ["robs", "rexp", "robscons", "rexpcons"]                              # 将所有信息名称和ck结果名称添加到一个列表中
        shutil.rmtree(os.path.join(self.base_message.Results_paths[self.process_num], 'GridData.txt'))
        self.write_list_to_file(all_info_name,os.path.join(self.base_message.Results_paths[self.process_num], 'GridData.txt')) # 将信息名称写入结果文件


    
class Support_subprocess(object):
    '''
    用于准备和收尾各个子进程的类，在generate_number确定后，也就是要计算的参数点确定后才运行，因此属于第三大类
    '''
    def __init__(self, base_message_: Base_message, process_num_: int, generate_number_: int) -> None:
        self.base_message = base_message_
        self.process_num = process_num_
        self.generate_number = generate_number_

    def prepare_MadGraph(self) -> None:
        '''
        准备MadGraph的param_card.dat输入文件以及proc_chi输入文件
        '''
        def pre_generate(self, data: pd.DataFrame = self.base_message.data_df) -> None:
            '''
            修改自@张迪的代码，用于准备MadGraph的param_card.dat输入文件以及proc_chi输入文件。proc_chi是generate EW过程文件的输入文件 
            param_card.dat文件来自于一个Spectrum文件的修改。
            如果是NMSSM模型，proc_chi来源于MadGraph_path/proc/proc_n*文件，其中n*是neutralino*，因为需要判断n*中哪一个是siglino为主，从而选择不同的proc。
            MSSM模型没有siglino，所以不需要判断n*是不是siglino为主。
            '''
            Index = data['Index'].iloc[self.generate_number]                                                                    # 获取Spectrum的Index
            with open("{}/muonSPhenoSPC_1/SPhenoSPC_{}.txt".format(self.base_message.data_path, str(Index)), 'r') as f1:        # 读取Spectrum文件
                with open("{}/../Madgraph/param_card.dat".format(self.base_message.Event_paths[self.process_num]), 'w') as f2:                               # 写入param_card.dat文件
                    f2.write(f1.read())

            ## 注意 !!!!  以下代码用于获得proc_chi文件，在未来的工作中判断条件有可能会被更改。  !!!!
            if self._model_name == 'MSSM':
                os.system("cp {0}/../Madgraph/proc_mssm {0}/../Madgraph/proc_chi".format(self.base_message.Event_paths[self.process_num]))
            elif self._model_name == 'NMSSM':
                if max(pow(data['N11'].iloc[self.generate_number], 2), pow(data['N12'].iloc[self.generate_number], 2), (pow(data['N13'].iloc[self.generate_number], 2) + pow(data['N14'].iloc[self.generate_number], 2)), pow(data['N15'].iloc[self.generate_number], 2)) == pow(data['N15'].iloc[self.generate_number], 2):  
                    os.system("cp {0}/../Madgraph/proc/proc_n1 {0}/../Madgraph/proc_chi".format(self.base_message.Event_paths[self.process_num]))
                if max(pow(data['N21'].iloc[self.generate_number], 2), pow(data['N22'].iloc[self.generate_number], 2), (pow(data['N23'].iloc[self.generate_number], 2) + pow(data['N24'].iloc[self.generate_number], 2)), pow(data['N25'].iloc[self.generate_number], 2)) == pow(data['N25'].iloc[self.generate_number], 2):
                    os.system("cp {0}/../Madgraph/proc/proc_n2 {0}/../Madgraph/proc_chi".format(self.base_message.Event_paths[self.process_num]))
                if max(pow(data['N31'].iloc[self.generate_number], 2), pow(data['N32'].iloc[self.generate_number], 2), (pow(data['N33'].iloc[self.generate_number], 2) + pow(data['N34'].iloc[self.generate_number], 2)), pow(data['N35'].iloc[self.generate_number], 2)) == pow(data['N35'].iloc[self.generate_number], 2):
                    os.system("cp {0}/../Madgraph/proc/proc_n3 {0}/../Madgraph/proc_chi".format(self.base_message.Event_paths[self.process_num]))
                if max(pow(data['N41'].iloc[self.generate_number], 2), pow(data['N42'].iloc[self.generate_number], 2), (pow(data['N43'].iloc[self.generate_number], 2) + pow(data['N44'].iloc[self.generate_number], 2)), pow(data['N45'].iloc[self.generate_number], 2)) == pow(data['N45'].iloc[self.generate_number], 2):
                    os.system("cp {0}/../Madgraph/proc/proc_n4 {0}/../Madgraph/proc_chi".format(self.base_message.Event_paths[self.process_num]))
                if max(pow(data['N51'].iloc[self.generate_number], 2), pow(data['N52'].iloc[self.generate_number], 2), (pow(data['N53'].iloc[self.generate_number], 2) + pow(data['N54'].iloc[self.generate_number], 2)), pow(data['N55'].iloc[self.generate_number], 2)) == pow(data['N55'].iloc[self.generate_number], 2):
                    os.system("cp {0}/../Madgraph/proc/proc_n5 {0}/../Madgraph/proc_chi".format(self.base_message.Event_paths[self.process_num]))

        os.chdir(self.base_message.Event_paths[self.process_num])
        os.system('rm -rf ../Madgraph/param_card.dat')                              # 删除原有的param_card.dat文件
        os.system('rm -rf ../Madgraph/proc_chi')                                    # 删除原有的proc_chi文件
        pre_generate(self)
        os.chdir(self.base_message.main_path)                                       # 回到主目录

    def prepare_CheckMATE(self) -> None:
        '''
        修改自@张迪的代码，用于获得checkmate的输入数据，写进ck_input.dat里
        其中一个重要的输入是截面数据，cs13chi_pb需要进行一系列判断再决定具体的数值
        最终所有输入数据都被写入ck_input.dat文件中，供下一步使用
        '''
        def ck_input(self, data: pd.DataFrame  = self.base_message.data_df) -> float:
            ## 注意 !!!!  以下代码用于获得checkmate的输入参数，在不同的工作中有可能会被更改  !!!!

            Index = data['Index'].iloc[self.generate_number]                                                     # 获取Spectrum的Index
            r_smodels = data['r_smodels'].iloc[self.generate_number]                                             # 获取Spectrum的r_smodels
            cs13chi_pb = data['cs13chi_pb'].iloc[self.generate_number]                                           # 获取Spectrum的cs13chi_pb，该数字是EW的产生截面数据。在作为checkmate输入数值之前，该截面还需要进一步计算。
            cs13smu_in = data['cs13smu_pb'].iloc[self.generate_number]                                           # 获取Spectrum的cs13smu_pb，该数字是SM的产生截面数据，是checkmate的重要输入数值。
            if self._model_name == 'MSSM':
                cs13chi_in = cs13chi_pb
            elif self._model_name == 'NMSSM':
                if max(pow(data['N11'].iloc[self.generate_number], 2), pow(data['N12'].iloc[self.generate_number], 2), (pow(data['N13'].iloc[self.generate_number], 2) + pow(data['N14'].iloc[self.generate_number], 2)), pow(data['N15'].iloc[self.generate_number], 2)) == pow(data['N15'].iloc[self.generate_number], 2):
                    cs13chi_in = cs13chi_pb
                if max(pow(data['N21'].iloc[self.generate_number], 2), pow(data['N22'].iloc[self.generate_number], 2), (pow(data['N23'].iloc[self.generate_number], 2) + pow(data['N24'].iloc[self.generate_number], 2)), pow(data['N25'].iloc[self.generate_number], 2)) == pow(data['N25'].iloc[self.generate_number], 2):
                    cs13chi_in = cs13chi_pb - (data['c1barn2_pb'].iloc[self.generate_number] + data['c1n2_pb'].iloc[self.generate_number] + data['c2barn2_pb'].iloc[self.generate_number] + data['c2n2_pb'].iloc[self.generate_number] + data['n2n2_pb'].iloc[self.generate_number] + data['n2n3_pb'].iloc[self.generate_number] + data['n2n4_pb'].iloc[self.generate_number] + data['n2n5_pb'].iloc[self.generate_number])
                if max(pow(data['N31'].iloc[self.generate_number], 2), pow(data['N32'].iloc[self.generate_number], 2), (pow(data['N33'].iloc[self.generate_number], 2)+ pow(data['N34'].iloc[self.generate_number], 2)), pow(data['N35'].iloc[self.generate_number], 2)) == pow(data['N35'].iloc[self.generate_number], 2):
                    cs13chi_in = cs13chi_pb - (data['c1barn3_pb'].iloc[self.generate_number] + data['c1n3_pb'].iloc[self.generate_number] + data['c2barn3_pb'].iloc[self.generate_number] + data['c2n3_pb'].iloc[self.generate_number] + data['n3n3_pb'].iloc[self.generate_number] + data['n2n3_pb'].iloc[self.generate_number] + data['n3n4_pb'].iloc[self.generate_number] + data['n3n5_pb'].iloc[self.generate_number])
                if max(pow(data['N41'].iloc[self.generate_number], 2), pow(data['N42'].iloc[self.generate_number], 2), (pow(data['N43'].iloc[self.generate_number], 2) + pow(data['N44'].iloc[self.generate_number], 2)), pow(data['N45'].iloc[self.generate_number], 2)) == pow(data['N45'].iloc[self.generate_number], 2):
                    cs13chi_in = cs13chi_pb - (data['c1barn4_pb'].iloc[self.generate_number] + data['c1n4_pb'].iloc[self.generate_number] + data['c2barn4_pb'].iloc[self.generate_number] + data['c2n4_pb'].iloc[self.generate_number] + data['n4n4_pb'].iloc[self.generate_number] + data['n2n4_pb'].iloc[self.generate_number] + data['n3n4_pb'].iloc[self.generate_number] + data['n4n5_pb'].iloc[self.generate_number])
                if max(pow(data['N51'].iloc[self.generate_number], 2), pow(data['N52'].iloc[self.generate_number], 2), (pow(data['N53'].iloc[self.generate_number], 2) + pow(data['N54'].iloc[self.generate_number], 2)), pow(data['N55'].iloc[self.generate_number], 2)) == pow(data['N55'].iloc[self.generate_number], 2):
                    cs13chi_in = cs13chi_pb - (data['c1barn5_pb'].iloc[self.generate_number] + data['c1n5_pb'].iloc[self.generate_number] + data['c2barn5_pb'].iloc[self.generate_number] + data['c2n5_pb'].iloc[self.generate_number] + data['n5n5_pb'].iloc[self.generate_number] + data['n2n5_pb'].iloc[self.generate_number] + data['n3n5_pb'].iloc[self.generate_number] + data['n4n5_pb'].iloc[self.generate_number])
            return Index, r_smodels, cs13chi_in, cs13smu_in, cs13chi_pb

        os.chdir(self.base_message.CheckMATE_paths[self.process_num])
        os.system('rm -rf ck_input.dat')                                                                                # 删除旧的ck_input.dat文件
        Index, self.r_smodels, self.cs13chi_in, self.cs13smu_in, self.cs13chi_pb = ck_input(self)
        with open('ck_input.dat', 'w') as ck_input_file:
            ck_input_file.write("Index\tr_smodels\tcs13chi_in\tcs13smu_pb\tcs13chi_pb\n")                                                   # 写入ck_input.dat文件
            ck_input_file.write("{}\t{}\t{}\t{}\t{}\n".format(Index, self.r_smodels, self.cs13chi_in, self.cs13smu_in, self.cs13chi_pb))    # 写入ck_input.dat文件
        os.chdir(self.base_message.main_path)                                                                                               # 返回主目录


