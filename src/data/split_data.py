import argparse
import os
import shutil
import random

import pandas as pd
from load_data import read_params


def split_and_copy_folder(ratio, src, dst_10_percent, dst_90_percent):
    """
    Split a folder of images into two sets, one with 10% and one with 90% of the images.
    :param src: Source directory path containing images.
    :param dst_10_percent: Destination directory path for 10% of the images.
    :param dst_90_percent: Destination directory path for 90% of the images.
    """
    # List all files in the source directory
    files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]

    # Shuffle the file list
    random.shuffle(files)

    # Calculate the split index for 10%
    split_index = int(ratio * len(files))

    # Split the files into two lists
    files_test_split = files[:split_index]
    files_train_spit = files[split_index:]

    # Function to copy files
    def copy_files(file_list, destination):
        if not os.path.exists(destination):
            os.makedirs(destination)
        for file in file_list:
            shutil.copy2(os.path.join(src, file), os.path.join(destination, file))

    # Copy the files to the respective directories
    copy_files(files_test_split, dst_10_percent)
    copy_files(files_train_spit, dst_90_percent)


def split_and_saved_data(config_path):
    """
    split the train dataset(data/raw) and save it in the data/processed folder
    input: config path 
    output: save splitted files in output folder
    """
    config = read_params(config_path)
    raw_data_path = config["raw_data_config"]["raw_data"]
    test_data_path = config["processed_data_config"]["test_casting_data"]
    train_data_path = config["processed_data_config"]["train_casting_data"]
    split_ratio = config["raw_data_config"]["train_test_split_ratio"]
    split_and_copy_folder(split_ratio, raw_data_path + "/def_front", test_data_path + "/def_front", train_data_path + "/def_front")
    split_and_copy_folder(split_ratio, raw_data_path+"/ok_front", test_data_path + "/ok_front", train_data_path + "/ok_front")

    
if __name__=="__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    split_and_saved_data(config_path=parsed_args.config)