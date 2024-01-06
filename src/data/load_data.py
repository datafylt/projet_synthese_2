import os
import shutil

import yaml
import argparse
import pandas as pd


def read_params(config_path):
    """
    read parameters from the params.yaml file
    input: params.yaml location
    output: parameters as dictionary
    """
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config


def copy_raw_to_processed(src, dst):
    """
        Copy a folder from src to dst with more control.
        :param src: Source directory path.
        :param dst: Destination directory path.
        """
    if not os.path.exists(dst):
        os.makedirs(dst)

    for root, dirs, files in os.walk(src):
        # For each directory in the source, create a corresponding directory in the destination
        for dir in dirs:
            dir_to_create = os.path.join(dst, os.path.relpath(os.path.join(root, dir), src))
            os.makedirs(dir_to_create, exist_ok=True)

        # For each file in the source, copy it to the corresponding location in the destination
        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dst, os.path.relpath(src_file, src))
            shutil.copy2(src_file, dst_file)


def load_raw_data(config_path):
    """
    load data from external location(data/external) to the raw folder(data/raw) with train and teting dataset 
    input: config_path 
    output: save train file in data/raw folder 
    """
    config = read_params(config_path)
    external_data_ok_path = config["external_data_config"]["external_casting_ok_data_csv"]
    external_data_def_path = config["external_data_config"]["external_casting_def_data_csv"]
    raw_data_path = config["raw_data_config"]["raw_data"]
    copy_raw_to_processed(external_data_ok_path, raw_data_path + "/ok_front")
    copy_raw_to_processed(external_data_def_path, raw_data_path + "/def_front")


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config", default="params.yaml")
    parsed_args = args.parse_args()
    load_raw_data(config_path=parsed_args.config)
