import json
import os
import subprocess
from pathlib import Path

config = json.load(open('config.json',encoding='utf-8'))
jar_path = config['jar_path']


def file_load(file_path) -> list:
    """
    从指定路径加载txt文件的内容
    :param file_path: txt文件路径
    :return: 含有txt文件内容的一个列表(去除空行)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'文件{file_path}不存在')
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line.strip()]


def load_output_to_file(file_path) -> None:
    """
    加载output.txt文件的内容到指定路径
    """
    path = Path(file_path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    command = "type " + path.parent.__str__() + "\\input.txt" + " | java -jar " + jar_path + " > " + file_path
    subprocess.run(command, shell=True)
