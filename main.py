from pathlib import Path
import json
import os
import subprocess
from DataGenerator import data_generator
from history import Library
import shutil
from datetime import date,timedelta
import re

config = json.load(open('config.json',encoding='utf-8'))
test_num = int(config['test_num'])
del_temp_file = config['del_temp_file']
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
def process_function(case_id) -> str:
    library = Library()
    generator = data_generator(library)
    proc = subprocess.Popen(
        ['java','-jar', config['jar_path']],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    mkdir(f"workspace/{case_id}")
    f_in = open(f"workspace/{case_id}/input.txt", 'w', encoding='utf-8')
    f_out = open(f"workspace/{case_id}/output.txt", 'w', encoding='utf-8')

    for command in generator.init_command_list:
        f_in.write(command)
        proc.stdin.write(command)
        proc.stdin.flush()
    while True:
        input_command = generator.get_next_command()
        if input_command == "":
            break
        f_in.write(input_command)
        proc.stdin.write(input_command)
        proc.stdin.flush()
        output_command = []#proc.stdout.readline()
        output_command.append(proc.stdout.readline())
        if not('-' in output_command[0] or int(output_command[0])==0):
            for i in range(0,int(output_command[0])):
                output_command.append(proc.stdout.readline())
        for i in output_command:
            f_out.write(i)
            generator.add_command(i)
        if 'OPEN' in input_command:
            tmp_match = re.match('\[(\d{4})-(\d{2})-(\d{2})\].*', input_command)
            time = date(int(tmp_match.group(1)), int(tmp_match.group(2)), int(tmp_match.group(3)))
            library.update(time)
            if int(output_command[0])>0:
                for i in range(1,output_command.__len__()):
                    result=library.orgnize(True,output_command[i])
                    if result!='':
                        return result
            result=library.open_check()
            if result!='':
                return result
        elif 'CLOSE' in input_command:
            if int(output_command[0])>0:
                for i in range(1,output_command.__len__()):
                    result=library.orgnize(False,output_command[i])
                    if result!='':
                        return result
        else:
            result=library.action(input_command,output_command[0])
            if result != '':
                return result
    return "Accepted!"


def mkdir(path):
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    shutil.rmtree("workspace", ignore_errors=True)
    failed_list = []
    for i in range(test_num):
        result = process_function(i + 1)
        if del_temp_file and result == "Accepted!":
            shutil.rmtree(f"workspace/{i + 1}")
        elif result != "Accepted!":
            failed_list.append(i + 1)
        print(f"Case {i + 1}: {result}")
    if failed_list:
        print(f"Failed cases: {failed_list}")
    else:
        print("All cases passed!")