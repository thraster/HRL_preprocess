import pickle as pkl
import numpy as np
import os
import pandas as pd
import cv2 as cv
import open3d as o3d
import scipy.io

def load_pickle(filename):
    try:
        p = open(filename, 'rb')
    except IOError:
        print("hrl_lib.util: Pickle file cannot be opened.")
        return None
    try:
        picklelicious = pkl.load(p, encoding='latin1')
    except ValueError:
        print('util.load_pickle failed once, trying again')
        p.close()
        p = open(filename, 'rb')
        picklelicious = pkl.load(p, encoding='latin1')

    p.close()
    return picklelicious



# def load_pickle(filename):
#     '''
#     Load a pickle with latin1 encoding.

#     Parameters
#     ----------
#     filename : str
#         Normalized file path of the the file that needs to be loaded.

#     Returns
#     -------
#     obj : unpickled object
#         The returned object after loading the pickle file.

#     '''
#     with open(filename, 'rb') as f:
        
#         obj = pkl.load(f, encoding='latin1')
#         f.seek(0)
#     return obj

def all_files(my_dir):
    """
    Create a list of all files and directories inside a specified directory.

    Parameters
    ----------
    my_dir : str
        Normalized string of the input directory.

        
    Returns
    -------
    all_fn : list
        List of noramlized file paths containng names of all files in that
        directory.
    all_dirs : list
        List of dirnames.

    """
    all_fn = []
    all_dirs = []

    for root, dirname, filenames in os.walk(my_dir):
        all_fn.append(filenames)
        path = root
    return path, filenames

class read_data():

    def __init__(self, pfile_root_path) -> None:
        pass
        '''
        输入一个subject的data的目录，把他的所有.p文件数据保存进一个字典
        '''
        self.root_dir = pfile_root_path           # 存储一个subject的根目录
        self.subject_name = pfile_root_path[-5:]  # 存储该subject的名字
        self.error_files = []                     # 保存.p文件加载时出错的文件名
        self.dat = {}                             # 申明用于存储该subject所有数据的字典
        '''
        字典的组织格式：dict['filename']['current_frame']----['pressure_map']
                                                         |
                                                         ---['skeleton_annotations']
                                                         |
                                                         ---['other']
        '''

    # 加载.p文件，存储进self.dat中
    def load_files(self):
        '''
        把一个subject的所有.p文件读进一个字典储存

        字典的组织格式：dict['filename']['current_frame']---['pressure_map']
                                                        |
                                                        ---['skeleton_annotations']
                                                        |
                                                        ---['other']
        '''
        
        path, filenames = all_files(self.root_dir)
        print(f"files: {filenames}")
        print(f"file nums = {len(filenames)}")
        self.dat = dict({el:{} for el in filenames})
        for file in filenames:
            print(f"processing {file}...")
            try:
                p_file = load_pickle(path+'\\'+file)
                self.dat[file] = dict({i:{} for i in range(len(p_file))})
                for i in range(len(p_file)):
                    # i = str(i)
                    # self.dat[file][i] = 
                    self.dat[file][i]['pressure_map'] = p_file[i][0]
                    self.dat[file][i]['skeleton_annotations'] = p_file[i][1]
                    self.dat[file][i]['other'] = p_file[i][2]
            except:
                # 加载.p文件时不知道为什么某些.p文件会出错， 所以加入了这段代码...
                # 用于存储出错的.p文件名，并跳过、处理下一个.p文件
                self.error_files.append(self.subject_name + '_' + file) # 存储出错的文件名
                print(f"encountered with errors when processing {file}, proceed to next .p file.")
                pass

        print('\n')
        print(f"---------------------subject {path} loaded in self.dat!--------------------")
        print('\n')


    # 展示self.dat文件的信息
    def data_info(self, pose = 'head.p', frame = 0):
        '''
        展示该subject的数据信息
        '''
        print(f"该数据类来自: {self.root_dir}")
        print(f"一级目录(subject采集的姿势)的键: \n{list(self.dat.keys())}")
        print(f"二级目录(某姿势下采集的帧数，默认为head.p)的键: \n{list(self.dat[pose].keys())[-1]}")
        print(f"三级目录(每一帧采集的数据类型)的键: \n{list(self.dat[pose][frame].keys())}")




    # 可视化数据
    def data_viz(self, pose_type = 'head.p', frame = 0, data_type = 0):
        '''
        pose_type - 加载好的不同姿势下采集的文件保存在同一个字典中，选择指定的姿势
        frame - 选择这个姿势下第n帧下的数据
        data_type - 有三个类型的数据，分别为pressure map, skeleton annotations 和 other, 对应0, 1, 2 
        '''
        if data_type == 0:
            print(f'visualizing pressure map of file {pose_type}, frame {frame}...')
            img = np.array(self.dat[pose_type][frame]['pressure_map']).reshape(64,27)
            cv.imshow('pressure map', img)
            cv.waitKey(0)
            cv.destroyAllWindows()

        elif data_type == 1:
            print(f'visualizing 3D skeleton annotations of file {pose_type}, frame {frame}...')

            # （10，3）的3D关节点数组
            nodes_3d = self.dat[pose_type][frame]['skeleton_annotations']

            # 创建一个Open3D点云对象
            pcd = o3d.geometry.PointCloud()

            # 设置点云数据
            pcd.points = o3d.utility.Vector3dVector(nodes_3d)

            # 创建可视化窗口
            o3d.visualization.draw_geometries([pcd])

        else:
            print(f"data_type should choose from 0 or 1, instead of {data_type}! ")
            pass


    # 把.p文件输出为pressure map和skeleton annotation
    def data_to_file(self, path):
        '''
        subject_name----pose_name------pressure_map\ 001.png, 002.png, ...
                                    |
                                    ------skeleton_annotation\ 001.mat, 002.mat, ...
        '''
        subject_dir = os.path.join(path, self.subject_name)

        for key in self.dat.keys():
            pose = os.path.join(subject_dir, key[:-2])
            images = os.path.join(pose, 'pressure_map')
            labels = os.path.join(pose, 'skeleton_annotations')

            # Create directories for pressure_map and skeleton_annotation
            os.makedirs(images, exist_ok=True)
            os.makedirs(labels, exist_ok=True)
            print(f"current pose: {key}, save to...")
            print(images)
            print(labels)
            for frame in self.dat[key].keys():
                pressure_map_path = os.path.join(images, f'{frame}.png')
                skeleton_annotations_path = os.path.join(labels,  f'{frame}.mat')
                
                
                # print(np.array(self.dat[key][frame]['pressure_map']).reshape(64,27))
                # print(self.dat[key][frame]['skeleton_annotations'])
                  # Save pressure_map as .png
                pressure_map_array = np.array(self.dat[key][frame]['pressure_map']).reshape(64, 27)
                cv.imwrite(pressure_map_path, pressure_map_array)

                # Save skeleton_annotations as .mat
                annotations_dict = {'data': self.dat[key][frame]['skeleton_annotations']}
                scipy.io.savemat(skeleton_annotations_path, annotations_dict)

    # 对self.dat中的pressure map进行预处理
    def data_preprocess(self, model = 0):
        '''
        将pressure map进行预处理
        '''
        for key in self.dat.keys():
            for frame in self.dat[key].keys():
                img = np.array(self.dat[key][frame]['pressure_map']).reshape(64,27).astype(np.uint8)
                if model == 0:
                    # 直方图均衡
                    img_equalized = cv.equalizeHist(img)

                    # 中值滤波
                    img_out = cv.medianBlur(img_equalized, 3)  # 使用3x3的中值滤波窗口

                elif model == 1:
                    # 中值滤波
                    img_filtered = cv.medianBlur(img, 3)  # 使用3x3的中值滤波窗口

                    # 直方图均衡
                    img_out = cv.equalizeHist(img_filtered)
                else:
                    pass

                # 将预处理后的图像保存回字典
                self.dat[key][frame]['pressure_map'] = tuple(img_out.reshape(-1))


if __name__ == "__main__":

    # s1 = read_data("F:\dataset\pressure_mat_pose_data\subject_GF5Q3")
    # s1.load_files()
    # s1.data_info()
    

    # s1.data_preprocess(1)
    # s1.data_viz()
    # s1.data_to_file("F:\\dataset\\pressure_mat_pose_data\\dataset")








    def traverse():
        errors = []
        subjects = []
        for root, dirnames, filenames in os.walk(f'F:\dataset\pressure_mat_pose_data'):
            # print(root)
            # print(filenames)
            # print(dirnames)
            for dirname in dirnames:
                if 'subject_' in dirname:
                    print(dirname)
                    subjects.append(root+'\\'+dirname)
            break
        print(subjects)

        i = 0
        for subject in subjects:
            s = read_data(subject)
            s.load_files()
            s.data_to_file(r'F:\dataset\pressure_mat_pose_data\dataset')
            if s.error_files != []:
                errors.append(s.error_files)


        print(f"total subjects = {len(subjects)}, loading errors = {i}")
        # print(error_folder)
        print(subjects)
        print(f".p files encountered errors when loading:\n {errors}")


    traverse()