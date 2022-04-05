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
        2022年4月4日：开始使用Copilot辅助。构造了Support_MCsim方法，mg5_Execution方法，Get_MG5_info方法。
'''

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

class Prepare_program(object):
    '''
    单个模拟进程开始前的准备工作。
    将来会用于替换prepare.py。
    '''
    def __init__(self) -> None:
        pass

    def get_generate_numbers_from_ck_ini(self, ck_ini: str) -> list:
        '''
        输入一个ck.ini文件，并获取本次进程所需的所有generate_numbers。
        '''
        search_keyword = 'Input parameters:'
        with open('{}/ck.ini'.format(self._main_path)) as ck_ini:       #本文件同目录下存在一个ck.ini文件，这是一个easyscan配置文件，其中包含了要执行的单个进程所需的所有信息。旧的程序正是依赖easyscan运行的。
            for line in ck_ini:
                if search_keyword in line:
                    ck_ini_message = re.split(r'[\s\,]+', line)         #本程序所需的ck.ini中的信息是，要计算的目标参数点所对应的ck_input.csv的行数
                    generate_number_range = [int(round(float(ck_ini_message[-3]))),int(round(float(ck_ini_message[-2])))]   #获得要计算的目标参数点的范围
                    generate_numbers = list(range(generate_number_range[1] - generate_number_range[0] - 1, 1))              #获得要计算的目标参数点的序列
        return generate_numbers


class Monte_Carlo_simulation(object):
    '''
    这是单个蒙特卡洛模拟进程的主类，所有必要的属性和方法都存在这里。
    每当一个Monte_Carlo_simulation类被实例化时，即可视为一次蒙特卡洛模拟进程开始了。
    '''
    def __init__(self, data_path_: str, generate_number_: int, main_path_: str = sys.path[0]) -> None:
        '''
        进程的初始化，获得: 主进程目录，数据目录，generate_number， MadGraph目录
        数据目录包含了Spectrums文件夹，以及ck_input.csv文件。ck_input.csv文件中包含了所有要计算的参数点信息。
        '''
        main_path(main_path_)                                                           #获得主进程目录
        data_path(data_path_)                                                           #获得数据目录
        generate_number(generate_number_)                                               #获得要计算的目标参数点对应的ck_input.csv的行数
        MadGraph_path('{}/../Externals/MadGraph'.format(self._main_path))               #获得MadGraph的目录

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
                raise ValueError(bcolors.print_WARNING('Generate number must be a integer!!!'))             # generate_number必须是一个整数
            self._generate_number = generate_number_

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


    def Support_MCsim(self) -> None:
        '''
        无论是MadGraph还是Checkmate，都需要在程序开始前和结束后进行一些准备和收尾工作，这个方法就是这些工作的集合
        '''

        def prepare_MadGraph(self) -> None:
            '''
            准备MadGraph
            '''
            pre_generate_path = self._main_path + '../Externals/ck/'     # 这是一个绝对路径，对prepare_MadGraph来说，所有的其他路径都是相对于这个路径的
            os.chdir(pre_generate_path)
            os.system('rm -rf ../Madgraph/param_card.dat')               # 删除原有的param_card.dat文件
            os.system('rm -rf ../Madgraph/proc_chi')                     # 删除原有的proc_chi文件
            pre_generate(pre_generate_path)
            os.chdir(self._main_path)                                    # 回到主目录
            
            def pre_generate(self, pre_generate_path: str) -> None:
                '''
                修改自@张迪的代码，用于准备MadGraph的param_card.dat输入文件以及proc_chi输入文件。proc_chi是generate EW过程文件的输入文件 
                param_card.dat文件来自于一个Spectrum文件的修改。
                proc_chi来源于MadGraph_path/proc/proc_n*文件，其中n*是neutralino*。
                至于为什么判断条件如此设置，请咨询@张迪，后续@贾兴隆会尽可能添加解释。
                '''
                data = pd.read_csv("{}/ck_input.csv".format(self._data_path))                                           # 读取ck_input.csv文件
                Index = data['Index'].iloc[self._generate_number-1]                                                     # 获取Spectrum的Index
                with open("{}/muonSPhenoSPC_1/SPhenoSPC_{}.txt".format(self._data_path, str(Index)), 'r') as f1:        # 读取Spectrum文件
                    with open("{}/../Madgraph/param_card.dat".format(pre_generate_path), 'w') as f2:                    # 写入param_card.dat文件
                        f2.write(f1.read())


                ## 注意 !!!!  以下代码用于获得proc_chi文件，在未来的工作中判断条件有可能会被更改。  !!!!
                if max(pow(data['N11'].iloc[self._generate_number-1], 2), pow(data['N12'].iloc[self._generate_number-1], 2), (pow(data['N13'].iloc[self._generate_number-1], 2) + pow(data['N14'].iloc[self._generate_number-1], 2)), pow(data['N15'].iloc[self._generate_number-1], 2)) == pow(data['N15'].iloc[self._generate_number-1], 2):  
                    os.system("cp {}/../Madgraph/proc/proc_n1 {}/../Madgraph/proc_chi".format(pre_generate_path, pre_generate_path))
                if max(pow(data['N21'].iloc[self._generate_number-1], 2), pow(data['N22'].iloc[self._generate_number-1], 2), (pow(data['N23'].iloc[self._generate_number-1], 2) + pow(data['N24'].iloc[self._generate_number-1], 2)), pow(data['N25'].iloc[self._generate_number-1], 2)) == pow(data['N25'].iloc[self._generate_number-1], 2):
                    os.system("cp {}/../Madgraph/proc/proc_n2 {}/../Madgraph/proc_chi".format(pre_generate_path, pre_generate_path))
                if max(pow(data['N31'].iloc[self._generate_number-1], 2), pow(data['N32'].iloc[self._generate_number-1], 2), (pow(data['N33'].iloc[self._generate_number-1], 2) + pow(data['N34'].iloc[self._generate_number-1], 2)), pow(data['N35'].iloc[self._generate_number-1], 2)) == pow(data['N35'].iloc[self._generate_number-1], 2):
                    os.system("cp {}/../Madgraph/proc/proc_n3 {}/../Madgraph/proc_chi".format(pre_generate_path, pre_generate_path))
                if max(pow(data['N41'].iloc[self._generate_number-1], 2), pow(data['N42'].iloc[self._generate_number-1], 2), (pow(data['N43'].iloc[self._generate_number-1], 2) + pow(data['N44'].iloc[self._generate_number-1], 2)), pow(data['N45'].iloc[self._generate_number-1], 2)) == pow(data['N45'].iloc[self._generate_number-1], 2):
                    os.system("cp {}/../Madgraph/proc/proc_n4 {}/../Madgraph/proc_chi".format(pre_generate_path, pre_generate_path))
                if max(pow(data['N51'].iloc[self._generate_number-1], 2), pow(data['N52'].iloc[self._generate_number-1], 2), (pow(data['N53'].iloc[self._generate_number-1], 2) + pow(data['N54'].iloc[self._generate_number-1], 2)), pow(data['N55'].iloc[self._generate_number-1], 2)) == pow(data['N55'].iloc[self._generate_number-1], 2):
                    os.system("cp {}/../Madgraph/proc/proc_n5 {}/../Madgraph/proc_chi".format(pre_generate_path, pre_generate_path))


        def prepare_CheckMATE(self) -> None:
            '''
            修改自@张迪的代码，用于生成checkmate的输入文件，并获得其他checkmate的输入参数。
            其中一个重要的输入是截面数据，cs13chi_pb需要进行一系列判断再决定具体的数值。

            '''
            pre_ck_path = self._main_path + '../Externals/ck/'                                                              # 这是一个绝对路径，对prepare_CheckMATE来说，所有的其他路径都是相对于这个路径的
            os.chdir(pre_ck_path)
            os.system('rm -rf ck_input.dat')                                                                                # 删除旧的ck_input.dat文件
            Index, r_smodels, cs13chi_in, cs13smu_in, cs13chi_pb = ck_input(pre_ck_path)
            with open('ck_input.dat', 'w') as ck_input_file:
                ck_input_file.write("Index\tr_smodels\tcs13chi_in\tcs13smu_pb\tcs13chi_pb\n")                               # 写入ck_input.dat文件
                ck_input_file.write("{}\t{}\t{}\t{}\t{}\n".format(Index, r_smodels, cs13chi_in, cs13smu_in, cs13chi_pb))    # 写入ck_input.dat文件
            os.chdir(self._main_path)                                                                                       # 返回主目录

            def ck_input(self,pre_ck_path: str):
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


    def Get_MG5_info(self, mg5_name_: str, mg5_category_: str, mg5_run_card_: str) -> None:
        '''
        在执行MadGraph程序之前，首先要获得必要的信息。
        mg5_name: 要执行的MadGraph程序的名字，如：'gnmssm_chi'，来源于proc_chi的最后一行output gnmssm_chi，放置在../Externals/Madgrapg/下。
        mg5_category: 要执行的MadGraph程序的类别，目前为止有两种类别，'EW'(electroweakinos)和'SL'(sleptons)。
        mg5_run_card: 要执行的MadGraph程序的run_card.dat的名字，如：'run_chi.dat'，放置在../Externals/Madgrapg/下。  
        '''
        mg5_name(mg5_name_)
        mg5_category(mg5_category_)
        mg5_run_card(mg5_run_card_)

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

        def pass_():
            pass

    def mg5_Execution(self) -> None:
        '''
        启动MadGraph程序，并获取结果。
        '''
        os.chdir(self._MadGraph_path)
        if self._mg5_category == 'EW':
            os.system('rm -rf {}'.format(self._mg5_name))                                                                   # 删除上一次生成的文件夹
            os.system('./MG5_aMC_v2_6_4/bin/mg5_aMC proc_chi')                                                              # 启动MadGraph中生成相互作用过程的程序，产生“过程”文件，对应于mg5中的generate命令。这里的proc_chi是上一步生成的文件，如果需要改动这个文件的名字应该在上一步中改动。
        if self._mg5_category == 'SL':
            os.system('rm -rf {0}/RunWeb {0}/index.html {0}/crossx.html {0}/HTML/* {0}/Events/*'.format(self._mg5_name))    # 删除上一次生成的文件，与EW不同的是，为了节省时间，SL的过程文件在运行了prepare.py之后已经生成过一次，因此只删除“过程”文件夹中必要的部分即可。
        os.system('cp param_card.dat pythia8_card.dat {0}/Cards/'.format(self._mg5_name))                                   # 将param_card.dat和pythia8_card.dat复制到mg5_name/Cards/下。
        os.system('cp {1} {0}/Cards/run_card.dat'.format(self._mg5_name, self._mg5_run_card))                               # 将mg5_run_card.dat复制到mg5_name/Cards/下。
        os.system('cp madevent_interface.py {0}/bin/internal/'.format(self._mg5_name))                                      # 将madevent_interface.py复制到mg5_name/bin/internal/下。该文件为提前生成的文件，初始位置放在MadGraph_path下。
        os.system('./{0}/bin/generate_events -f'.format(self._mg5_name))                                                    # 启动MadGraph中生成事例的程序，产生“事例”文件夹，对应于mg5中的launch命令。这也是单个MadGraph程序的最后一步。输出结果保存在mg5_name/Events/run_01/下。


    def CheckMATE_info(self) -> None:
        pass
        

    