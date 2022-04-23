#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
@作者:  贾兴隆
@说明:  本程序的目标功能是实现蒙特卡洛模拟LHC对撞实验的自动化，与上个系列不同，该系列程序将囊括从准备到收集结果的所有步骤，同时支持多核运行并最大程度保持灵活性。
    
    下面是文件结构的一个例子，暂时使用的是当前各服务器正在使用的名称
    主要的根目录级文件结构：
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

         Project_prepare/:                   # 存放着所有用于准备一个新项目的文件
            CM_v2_26.tar.gz                     # Checkmate的tar包
            MG5_aMC_v2_6_4.tar.gz               # MG5_aMC的tar包
            mg5_configuration.txt               # MG5_aMC的配置文件
            installP8                           # 安装Pythia8的脚本
            madevent_interface.py               # madevent的接口文件
            proc/
            proc_chi
            proc_smusmu
            run_card.dat
            run_chi.dat
            run_smu.dat
            gnmssm_chi.dat
            gnmssm_smusmu.dat

        2tau8c_*/:                           # 单一的进程文件夹，项目调用多少进程就会有多少个这样的文件夹，下面的所有文件夹都是针对单一进程的
            CheckMATE/                            # 存放所有与Checkmate有关系的文件
                ck_input.dat                        # Checkmate输入数据文件
            Results/                              # 存放所有结果的文件夹
                GridData.txt
                after_ck/                           # 运行完Checkmate后收集的Madgraph结果和Checkmate结果
                    ck_r.txt                        # 存放Checkmate输出的结果
                    *index*/                        # 存放单个参数点的Madgraph结果和Checkmate结果，单一进程计算了多少个参数点就会有多少个



@开发日志：
        2022年4月23日：开始编写程序的文档，说明文件结构
'''

