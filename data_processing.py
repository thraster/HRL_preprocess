# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 14:38:05 2020

@author: BTLab
"""

# Separate the real data into different files
# Data separated by patients
# Each patient has 48 frames
# Belongs to one of 8 poses
# Directory structure needs to be like the following:
    # Real data
    # | Patient ID
    # | | Pose Type
    # | | | Pressure file
    # | | | 

import pickle as pkl
import numpy as np
import os
import pandas as pd


def load_pickle(filename):
    '''
    Load a pickle with latin1 encoding.

    Parameters
    ----------
    filename : str
        Normalized file path of the the file that needs to be loaded.

    Returns
    -------
    obj : unpickled object
        The returned object after loading the pickle file.

    '''
    with open(filename, 'rb') as f:
        obj = pkl.load(f, encoding='latin1')
    return obj


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
        if dirname:
            all_dirs = dirname
        for file in filenames:
            all_fn.append(os.path.join(root, file))
    return all_fn, all_dirs


def mkdir(dirname):
    """
    Make a directory if it does not exist.

    Parameters
    ----------
    dirname : str
        Normalized string of directory location.

    Returns
    -------
    None.

    """
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    return None


class BodiesAtRestReal():
    
    def __init__(self, root_dir, new_dir):
        self.root_dir = root_dir
        self.new_dir = new_dir
        self.dat = {}
        self.dataframe = pd.DataFrame()
    
    def load_files(self):
        # First get all the files
        print("loading files...")
        filenames, dirnames = all_files(self.root_dir)
        # Make a dict with keys as the name of the subject
        self.dat = dict({el:{} for el in dirnames})
        # For each file if the dirname is part of the filename then load the
        # pickle in that key
        print(f"file nums = {len(filenames)}")
        for file in filenames:
            for d in dirnames:
                if d in file:
                    # There are three kinds of files, prescribed, select, info
                    if 'prescribed' in file:
                        self.dat[d]['prescribed'] = load_pickle(file)
                    elif 'p_select' in file:
                        self.dat[d]['p_select'] = load_pickle(file)
                    else:
                        self.dat[d]['participant_info'] = load_pickle(file)
    
    # Function combine all the data in a pd.DataFrame
    def make_dataframe(self):
        # Data frame needs the following columns:
            # FileName (location of the file)
            # Pose Label
            # Gender
            # Height
            # Weight
            # Point Clouds
            # Corners
            # Anything else
        # Go through each subject        
        for sub in self.dat.keys():
            # For each subject get the participant info
            # The participant info has the following information
            # Make array of height, weight, and sex equal to number of samples
            sub_h = [self.dat[sub]['participant_info']['height_in'] for _
                     in range(len(self.dat[sub]['participant_info']['prescribed_pose_type']))]
            sub_w = [self.dat[sub]['participant_info']['weight_lbs'] for _
                     in range(len(self.dat[sub]['participant_info']['prescribed_pose_type']))]
            sub_g = [self.dat[sub]['participant_info']['gender'] for _
                     in range(len(self.dat[sub]['participant_info']['prescribed_pose_type']))]
            sub_id = [sub for _ in range(len(self.dat[sub]['participant_info']['prescribed_pose_type']))]
            
            # Make new directories for the subject
            sub_dir = os.path.join(self.new_dir, sub)
            mkdir(sub_dir)
            pres_dir = os.path.join(sub_dir, 'pressure')
            img_dir = os.path.join(sub_dir, 'RGB')
            depth_dir = os.path.join(sub_dir, 'depth')
            mkdir(pres_dir)
            mkdir(img_dir)
            mkdir(depth_dir)
            
            # Initialize list to hold all file names
            all_img_fn = []
            all_depth_fn = []
            all_pres_fn = []

            for idx in range(len(self.dat[sub]['prescribed']['images'])):
                fn = self.make_filename(idx)
                img_fn = os.path.join(img_dir, fn)
                pres_fn = os.path.join(pres_dir, fn)
                depth_fn = os.path.join(depth_dir, fn)
                
                # Save the arrays
                np.save(img_fn, self.dat[sub]['prescribed']['RGB'][idx])
                np.save(pres_fn, self.dat[sub]['prescribed']['images'][idx])
                np.save(depth_fn, self.dat[sub]['prescribed']['depth'][idx])
                
                # Append the filenames to all_filenames
                all_img_fn.append(img_fn)
                all_pres_fn.append(pres_fn)
                all_depth_fn.append(depth_fn)
            
            # Append to temp dataframe
            df = pd.DataFrame()
            df['height'] = sub_h
            df['weight'] = sub_w
            df['gender'] = sub_g
            df['sub_id'] = sub_id
            df['img_fn'] = all_img_fn
            df['prs_fn'] = all_pres_fn
            df['dep_fn'] = all_depth_fn
            df['pcloud'] = self.dat[sub]['prescribed']['pc']
            df['corner'] = self.dat[sub]['prescribed']['pmat_corners']
            df['label'] = self.dat[sub]['prescribed']['pose_type']
            
            # Append temp dataframe to the actual dataframe
            self.dataframe = self.dataframe.append(df)
        
        metadata_fn = os.path.join(self.new_dir, 'metadata.csv')
        
        self.dataframe.to_csv(metadata_fn)
            
    def make_filename(self, idx):
        if idx < 10:
            fn = '00' + str(idx)
        elif idx < 100:
            fn = '0' + str(idx)
        else:
            fn = str(idx)
        return fn
    
    def make_metadata_csv(self):
        self.dat = pd.DataFrame.from_dict(self.dat)
        
    def refactor_data(self):
        print("refactor_data...")
        self.load_files()
        self.make_dataframe()
        
        
if __name__ == '__main__':
    spam = BodiesAtRestReal(r"D:\workspace\python_ws\bodies-at-rest-master\data_BR\real",
                            r"D:\workspace\python_ws\Pose_classification-master\src\Real_Data")
    print("reading data now...")
    spam.refactor_data()