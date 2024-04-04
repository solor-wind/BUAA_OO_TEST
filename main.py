import multiprocessing
from func_timeout import func_timeout, FunctionTimedOut
from checker import analyze_output, analyze_input, check
import json
from data_generator import DataGenerator
from pathlib import Path
from data_loader import load_outputs_to_workspace
import shutil

config = json.load(open('config.json', 'r', encoding='utf-8'))
delete_temp_files = config['delete_temp_files']
test_num = config['test_num']
max_thread_num = config['max_thread_num']
set_clock = config['set_clock']
clock_time = config['clock_time']
my_input = config['my_input']


def mkdir(path):
    path = Path(path)
    if not path.exists():
        path.mkdir()


def process_function(case_id) -> bool:
    global delete_temp_files, my_input
    accept = False
    if my_input:
        pass                     # 自定义输入在这里填写
    else:
        DataGenerator().dump_inputs(f'workspace/{case_id}/stdin.txt')
    waiters = analyze_input(f'workspace/{case_id}/stdin.txt')
    load_outputs_to_workspace(f'workspace/{case_id}')
    actions = analyze_output(f'workspace/{case_id}/output.txt')
    result = check(waiters, actions)
    if result == 'Accepted!':
        accept = True
        if delete_temp_files:
            shutil.rmtree(f'workspace/{case_id}')
    print(f"{case_id} : {result}")
    return accept


def process_function_with_time_limit(case_id) -> bool:
    global clock_time
    try:
        return func_timeout(clock_time, process_function, args=(case_id,))
    except FunctionTimedOut:
        print(f"{case_id} : 超时!")
        return False


if __name__ == "__main__":
    shutil.rmtree('workspace', ignore_errors=True)
    mkdir('workspace')
    results = []
    allAccepted = True
    if set_clock:
        target_function = process_function_with_time_limit
    else:
        target_function = process_function
    pool = multiprocessing.Pool(processes=max_thread_num)
    for i in range(1, test_num + 1):
        results.append(pool.apply_async(target_function, args=(i,)))
    pool.close()
    pool.join()
    for res in results:
        if not res.get():
            allAccepted = False
            break
    if allAccepted:
        print("All Accepted!")
    else:
        print("Some cases failed!")
