"""
This script shows you how to edit a .h5 (.hdf5) file of a dataset.
You can also modify the 'env_args' attribute to adapt an existing dataset to your own settings.

author: wangyan
"""
import h5py
import argparse
import numpy as np


def modify_env_args(dataset, **kwargs):
    """
    Modify the env_args of an H5 file
   
    Args:
    dataset: the .h5 format dataset
    kwargs: a dict with new env_args
    """
    with h5py.File(dataset, 'a') as file:
        try:
            data_group = file['data']
        except KeyError:
            raise KeyError("Group not found in the file.")
        try:
            data_group.attrs['env_args'] = \
                "{\n \"env_name\": \""+args.env+"\",\n \"env_version\": \"1.4.1\",\n \"type\": 1,\n \"env_kwargs\": {\n \"has_renderer\": false,\n \"has_offscreen_renderer\": true,\n \"ignore_done\": true,\n \"use_object_obs\": true,\n \"use_camera_obs\": true,\n \"control_freq\": 20,\n \"controller_configs\": {\n \"type\": \"OSC_POSE\",\n \"input_max\": 1,\n \"input_min\": -1,\n \"output_max\": [\n 0.05,\n 0.05,\n 0.05,\n 0.5,\n 0.5,\n 0.5\n ],\n \"output_min\": [\n -0.05,\n -0.05,\n -0.05,\n -0.5,\n -0.5,\n -0.5\n ],\n \"kp\": 150,\n \"damping\": 1,\n \"impedance_mode\": \"fixed\",\n \"kp_limits\": [\n 0,\n 300\n ],\n \"damping_limits\": [\n 0,\n 10\n ],\n \"position_limits\": null,\n \"orientation_limits\": null,\n \"uncouple_pos_ori\": true,\n \"control_delta\": true,\n \"interpolation\": null,\n \"ramp_ratio\": 0.2\n },\n \"robots\": [\n \""+kwargs["robot"]+"\"\n ],\n \"gripper_types\": \""+kwargs["gripper_types"]+"\",\n \"camera_depths\": true,\n \"camera_heights\": 84,\n \"camera_widths\": 84,\n \"render_gpu_device_id\": 0,\n \"reward_shaping\": false,\n \"camera_names\": [\n \"agentview\",\n \"robot0_eye_in_hand\"\n ]\n }\n}"

            print(data_group.attrs['env_args'])
        except KeyError:
            raise KeyError("Attribute not found in the file.")


def read_dataset(dataset):
    with h5py.File(dataset, 'r') as dataset:
        # 获取当前数据集的demo名称列表
        demo_names = list(dataset['data'].keys())

        # 遍历每个demo
        for demo_name in demo_names:
            data_names = list(dataset['data'][demo_name].keys())
            for data_name in data_names:
                print(np.asarray(dataset['data'][demo_name][data_name]))


def merge_datasets(src_datasets, dest_dataset):
    # 创建新的合并数据集文件
    with h5py.File(dest_dataset, 'w') as f_dest:
        first_dataset = src_datasets[0]
        with h5py.File(first_dataset, 'r') as first_src:
            # 创建目标文件中的 'data' 组，并复制属性等信息
            data_group = f_dest.create_group('data')
            data_group.attrs.update(first_src['data'].attrs)

        data_count = 1  # 记录合并后的 demo 编号
        # 遍历每个数据集
        for dataset_path in src_datasets:
            with h5py.File(dataset_path, 'r') as f_src:
                # 获取当前数据集的 demo 名称列表
                demo_names = list(f_src['data'].keys())

                # 遍历每个 demo
                for demo_name in demo_names:
                    # 生成新的 demo 名称，添加编号
                    new_demo_name = f'demo_{data_count}'
                    data_count += 1

                    # 如果新的 demo 分组还不存在，就创建它
                    if new_demo_name not in data_group:
                        data_group.create_group(new_demo_name)
                        data_group[new_demo_name].attrs.update(f_src[f'data/{demo_name}'].attrs)
                        # 复制数据到新的合并数据集中
                        for src_data_key in list(f_src[f'data/{demo_name}'].keys()):
                            f_src.copy(f_src[f'data/{demo_name}/{src_data_key}'], data_group[new_demo_name])

    print(f'数据集已成功合并并重新编号,共{data_count-1}条demonstrations,保存在 merged_dataset.h5 中')



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--option", type=str, help="option to execute on the dataset file")
    parser.add_argument("--dataset", type=str, help="base dataset to read or modify")
    parser.add_argument("--src_datasets", type=str, nargs='+', help="source datasets to merge from")
    parser.add_argument("--dest_dataset", type=str, help="destination dataset to merge into")
    parser.add_argument("--robot", type=str, default="Panda", help="robot to use")
    parser.add_argument("--gripper_types", type=str, default="PandaGripper", help="gripper type to use")
    parser.add_argument("--env", type=str, default="Coffee_D0", help="environment to use")

    args = parser.parse_args()

    if args.option == "modify":
        # Modify the env_args of an HDF5 file
        options = {}
        options["robot"] = args.robot
        options["gripper_types"] = args.gripper_types

        modify_env_args(args.dataset, **options)

    elif args.option == "read":
        read_dataset(args.dataset)

    elif args.option == "merge":
        merge_datasets(args.src_datasets, args.dest_dataset)
