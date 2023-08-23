
This is a code about editing the HRL-ROS dataset for future exploration.

-------------------------------------

Data published publicly online by Henry M. Clever 06/2018
Email: henryclever@gatech.edu

Each folder contains data from a particular subject. During data collection, the subject was asked to move a limb according to a pre-defined path. During movement, motion capture cameras were used to record assistive task-relevant joint locations including the head, chest, elbows, wrists, knees, and ankles. At the same time, a pressure sensing mat/blanket under the subject recorded data at 5Hz. The size of the mat is 27x64 taxels, where each taxel is 2.86cm square. This is about the size of a twin size bed. More information can be found in the following publication:

Clever, Henry M., Ariel Kapusta, Daehyung Park, Zackory Erickson, Yash Chitalia, and Charles C. Kemp. "Estimating 3D Human Pose on a Configurable Bed from a Single Pressure Image." arXiv preprint arXiv:1804.07873 (2018).
Available at: https://arxiv.org/pdf/1804.07873.pdf

The following folders contain participant data used in the network design set:
40E2J
WM9KJ
WFGW9
ZV7TE
FMNGQ
GRTJK
TX887

The following folders contain participant data used in leave-one-out-cross-validation:

TSQNA
RQCLC
A4G4Y
G55Q1
GF5Q3
WCNOM
WE2SZ
5LDJG
1YJAG
4ZZZQ

Each p-file within a folder corresponds to some particular path traversed by that subject. Refer to fig. 4 from the paper to understand movement paths from the data files:


RH1.p: Fig 4(a)
LH1.p: Fig 4(a)
RH2.p: Fig 4(b)
LH2.p: Fig 4(b)
RH3.p: Fig 4(c)
LH3.p: Fig 4(c)
RL_air.p: Fig 4(d)
LL_air.p: Fig 4(d)
RL.p: Fig 4(d), foot always in contact - subset of RL_air.p
LL.p: Fig 4(d), foot always in contact - subset of LL_air.p
RL_air_only.p: Fig 4(d), foot out of contact - subset of RL_air.p
LL_air_only.p: Fig 4(d), foot out of contact - subset of LL_air.p
RH_sitting.p: Fig 4(e)
LH_sitting.p: Fig 4(e)
RL_sitting.p: Fig 4(f)
LL_sitting.p: Fig 4(f)
head.p: not shown in fig
home.p: not shown in fig
head_sitting.p: not shown in fig
home_sitting.p: not shown in fig

To read this data on a computer, use python to unpickle the files. The following script (create_dataset.py) allows you to take multiple pickle files and combine them into a larger dataset. It also appends a skeleton model to the larger dataset with joint lengths and inverse kinematics. However, you'll have to do some editing to make the code mesh with the publicly released de-identified data. E.g., the subjects are listed in the code as 1,2,3....13,14,15 but not here.

The length of each pickle file is how many synchonized, labeled pressure mat images are sampled. E.g. if the length is 100 and it was sampled at 5Hz, it means the person moved for 20 seconds. After loading the pickle file in a python script, use the following command to index the pressure images and motion capture markers:
#p_map_raw, target_raw, _ = p_file[index]

Next, you'll want to do a transform on the motion capture data to make it with respect to the bottom left corner of the bed (or pressure mat, whatever have you). You'll have to download the create_dataset_lib.py library from the GT ros github or just get the world_to_mat function out of it. 
https://github.com/gt-ros-pkg/hrl-assistive/tree/indigo-devel/hrl_pose_estimation/src/hrl_pose_estimation

#[self.p_world_mat, self.R_world_mat] = load_pickle('[main folder]/mat_axes.p')
#from create_dataset_lib import CreateDatasetLib
#target_mat = CreateDatasetLib().world_to_mat(target_raw, self.p_world_mat, self.R_world_mat)

Lastly, convert the p_map_raw and the target_mat to numpy arrays and do what you need. 
p_map_raw is just a 2D array. The targets should come packaged in a 10x3 array, with 10 joints and x-y-z-Cartesian positions for each joint.



