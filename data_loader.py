import subprocess
from pathlib import Path
import json
import shutil

config = json.load(open('config.json', 'r', encoding='utf-8'))
in_path = Path(config['in_path'])
jar_path = Path(config['jar_path'])


def load_outputs_to_workspace(workspace_path):
    """
    将exe文件复制到workspace_path, 并执行命令，将输出重定向到output.txt
    :param workspace_path: 输出路径
    :return:
    """
    global in_path, jar_path
    target = Path(workspace_path)
    if not target.exists():
        target.mkdir(parents=True, exist_ok=True)
    shutil.copy(in_path, workspace_path)  # 将exe复制到workspace_path
    execute = in_path.name
    command = f'{execute} | java -jar {jar_path} > output.txt'
    subprocess.run(command, shell=True, cwd=workspace_path)


if __name__ == '__main__':
    load_outputs_to_workspace('workspace/1')
