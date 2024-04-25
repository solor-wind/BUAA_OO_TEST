import os


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
