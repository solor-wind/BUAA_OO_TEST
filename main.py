from pathlib import Path
import json
from data_generator import generate_data
from checker import Checker
from loader import load_output_to_file
import shutil
from func_timeout import func_timeout, FunctionTimedOut

config = json.load(open('config.json',encoding='utf-8'))
test_num = int(config['test_num'])
del_temp_file = config['del_temp_file']
jar_path = config['jar_path']
set_clock = config['set_clock']
clock_time = float(config['clock_time'])

def process_function(case_id) -> str:
    global del_temp_file
    mkdir(f"workspace/{case_id}")
    generate_data(f"workspace/{case_id}/input.txt")
    if set_clock:
        try:
            func_timeout(clock_time, load_output_to_file, args=(f"workspace/{case_id}/output.txt", ))
        except FunctionTimedOut:
            return "超时！"
    else:
        load_output_to_file(f"workspace/{case_id}/output.txt")
    return Checker(f'workspace/{case_id}/input.txt', f"workspace/{case_id}/output.txt").check()


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