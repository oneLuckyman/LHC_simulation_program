#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
@作者:  贾兴隆
@说明:  本程序的目标功能是实现蒙特卡洛模拟LHC对撞实验的自动化，与上个系列不同，该系列程序将囊括从准备到收集结果的所有步骤，同时支持多核运行并最大程度保持灵活性。
    
    下面是文件结构的一个例子，暂时使用的是当前各服务器正在使用的名称
    起始于根目录级的主要文件结构：
        Data_dir/:                           # 用于存放所有的数据文件，原gnmssm文件夹
            ck_input.csv                        # 存放所有Checkmate可能的输入数据的文件
            muonSPhenoSPC/                      # 存放所有smodels输入谱的文件夹
            muonSPhenoSPC_1/                    # 存放所有SPheno输出谱的文件夹
            InputsForProspino/                  # 存放所有Prospino输入谱的数据文件
            smodels/                            # 存放所有smodels输出数据的文件夹
                h1/                                 # 收集不同批次smodels数据的子文件夹
                h2/                                 # 同上
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
            proc_chi                            # generate events的脚本
            proc_smusmu                         # generate events的脚本
            run_card.dat                        # 事例模拟所需要的run_card.dat模板文件
            run_chi.dat                         # 事例模拟所需要的run_card.dat模板文件
            run_smu.dat                         # 事例模拟所需要的run_card.dat模板文件
            gnmssm_chi.dat                      # checkmate输入模板文件
            gnmssm_smusmu.dat                   # checkmate输入模板文件

        2tau8c_*/:                           # 单一的进程文件夹，项目调用多少进程就会有多少个这样的文件夹，下面的所有文件夹都是针对单一进程的
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
        2tau8c_*/:                          # 运行事例模拟以及存放事例模拟结果的文件夹，项目调用多少进程就会有多少个这样的文件夹，这个目录可以是任何名字，可以在任何路径下
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
                run_card.dat                        # 事例模拟所需要的run_card.dat模板文件
                run_chi.dat                         # 事例模拟所需要的run_card.dat模板文件
                run_smu.dat                         # 事例模拟所需要的run_card.dat模板文件


@开发日志：
        2022年4月23日：开始编写程序的文档，说明文件结构
        2022年4月24日：文件结构说明完毕，Base_message类写完了
        2022年4月25日：Project_prepare类基本写完了
'''

import argparse
import os,sys,re
import shutil

from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
ranks = comm.Get_size()

class Base_message(object):
    '''
    这个类包含了所有的基本信息
    '''
    def __init__(self, Event_root_path_, model_name_: str, size_: int, info_name_list_: list, 
                        main_path_: str = sys.path[0], data_path_: str = 'gnmssm/', project_prepare_path_: str = 'Project_prepare/', process_name_: str = '2tau8c',
                        comm_ = MPI.COMM_WORLD, rank_ = comm.Get_rank(), ranks_ = comm.Get_size()) -> None:

        self.main_path = main_path_
        self.data_path = os.path.join(self.main_path, data_path_)
        self.Event_root_path = Event_root_path_
        self.project_prepare_path = os.path.join(self.main_path, project_prepare_path_)
        self.model_name = model_name_
        self.size = size_
        self.comm = comm_
        self.rank = rank_
        self.ranks = ranks_
        self.info_name_list = info_name_list_
        self.process_name = process_name_
        self.processes = self.get_process_name()
        self.process_paths = self.get_process_path()
        self.Madgraph_paths = self.get_Madgraph_paths()
        self.CheckMATE_paths = self.get_CheckMATE_paths()
        self.Results_paths = self.get_Results_paths()
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
    
    def get_process_path(self) -> list:
        '''
        获得所有进程文件夹的路径
        '''
        process_paths = []
        for i in range(self.size):
            process_paths.append(os.path.join(self.main_path, self.process_name + '_' + str(i)))
        return process_paths
    
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
    def __init__(self, base_message_: Base_message) -> None:
        self.base_message = base_message_

    def mkdirs(self) -> None:
        for i in range(self.base_message.size):
            if not os.path.exists(self.base_message.process_paths[i]):
                os.makedirs(self.base_message.process_paths[i])
            if not os.path.exists(self.base_message.Madgraph_paths[i]):
                os.makedirs(self.base_message.Madgraph_paths[i])
            if not os.path.exists(self.base_message.CheckMATE_paths[i]):
                os.makedirs(self.base_message.CheckMATE_paths[i])
            if not os.path.exists(self.base_message.Results_paths[i]):
                os.makedirs(self.base_message.Results_paths[i])
            if not os.path.exists(self.base_message.Event_paths[i]):
                os.makedirs(self.base_message.Event_paths[i])
            if not os.path.exists(self.base_message.Event_template_paths[i]):
                os.makedirs(self.base_message.Event_template_paths[i])

    def install_Madgraph(self) -> None:
        '''
        安装Madgraph
        '''
        for i in range(self.base_message.size):
            if self.base_message.rank == i:
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'MG5_aMC_v2_6_4.tar.gz'), self.base_message.Madgraph_paths[i])
                os.chdir(self.base_message.Madgraph_paths[i])
                os.system('tar -zxvf MG5_aMC_v2_6_4.tar.gz')
                os.system('rm -rf MG5_aMC_v2_6_4.tar.gz')
                os.chdir(self.base_message.project_prepare_path)
                os.system(os.path.join(self.base_message.Madgraph_paths[i], 'MG5_aMC_v2_6_4/bin/mg5_aMC installP8'))
                os.chdir(self.base_message.main_path)

    def install_CheckMATE(self) -> None:
        '''
        安装CheckMATE
        '''
        for i in range(self.base_message.size):
            if self.base_message.rank == i:
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'CM_v2_26.tar.gz'), self.base_message.CheckMATE_paths[i])
                os.chdir(self.base_message.CheckMATE_paths[i])
                os.system('tar -zxvf CM_v2_26.tar.gz')
                os.system('rm -rf CM_v2_26.tar.gz')
                os.chdir('CM_v2_26')
                # 配置环境如果发生改变需要修改下面这一行中的路径
                os.system("./configure --with-rootsys=/opt/root-6.18.04/installdir --with-delphes=/opt/delphes_for_CheckMATE --with-pythia=/opt/pythia8245 --with-hepmc=/opt/HepMC-2.06.11")
                os.system('make -j 20')
                os.chdir(self.base_message.project_prepare_path)
                shutil.copy2('gnmssm_chi.dat',os.path.join(self.base_message.CheckMATE_paths[i],'CM_v2_26','bin'))
                shutil.copy2('gnmssm_smusmu.dat',os.path.join(self.base_message.CheckMATE_paths[i],'CM_v2_26','bin'))
                os.chdir(self.base_message.main_path)

    def Prepare_Madgraph_inputfile(self) -> None:
        '''
        准备Madgraph输入文件
        '''
        for i in range(self.base_message.size):
            if self.base_message.rank == i:
                shutil.copytree(os.path.join(self.base_message.project_prepare_path, 'proc/'), os.path.join(self.base_message.Event_template_paths[i], 'proc/'))
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'proc_chi'), self.base_message.Event_template_paths[i])
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'proc_smusmu'), self.base_message.Event_template_paths[i])
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'run_card.dat'), self.base_message.Event_template_paths[i])
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'run_chi.dat'), self.base_message.Event_template_paths[i])
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'run_smu.dat'), self.base_message.Event_template_paths[i])
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'madevent_interface.py'), self.base_message.Event_template_paths[i])
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'mg5_configuration.txt'), self.base_message.Event_template_paths[i])
                shutil.copy2(os.path.join(self.base_message.project_prepare_path, 'pythia8_card.dat'), self.base_message.Event_template_paths[i])
                
                os.chdir(self.base_message.Event_paths[i])
                os.system(os.path.join(self.base_message.Madgraph_paths[i], 'MG5_aMC_v2_6_4/bin/') + 'mg5_aMC proc_smusmu')
                os.chdir(self.base_message.main_path)

    def sel_ck():
        pass



            
            