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
        2tau8c_*/:                          # 运行事例模拟以及存放事例模拟结果的文件夹，项目调用多少进程就会有多少个这样的文件夹，这个目录可以是任何目录
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
                gnmssm_chi.dat                      # checkmate输入模板文件
                gnmssm_smusmu.dat                   # checkmate输入模板文件


@开发日志：
        2022年4月23日：开始编写程序的文档，说明文件结构
'''

