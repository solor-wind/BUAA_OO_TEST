import random
import re
import subprocess
import json
import multiprocessing
from pathlib import Path
import shutil
import signal

config = json.load(open('config.json', 'r', encoding='utf-8'))


# "test_num":10,    #测试次数
# "time_limit":10,  #生成数据的时间限制
# "command_limit":10,   #生成数据的指令数量
# "fault_tolerance":0.01,   #容错率
# "deleteTempFile":true,   #是否删除临时文件
# "max_thread_num":10,  #最大线程数
# "elevator_num":6,  #电梯数量
# "default_floor":1,    #默认楼层
# "min_floor":1,    #最小楼层
# "max_floor":11,   #最大楼层
# "move_time":0.4,  #移动时间
# "open_time":0.2,  #开门时间
# "close_time":0.2, #关门时间
# "max_capacity":6  #最大容量
# "in_path": 获取输入程序路径
# "jar_path": 获取输出程序路径 !!!必须是绝对路径
# "set_clock" : 是否设置时钟(仅linux)
# "clock_time" : 时钟时间

def handler(signum, frame):
    raise TimeoutError


def generate_input(case_id):
    idlist = list(range(1, 101))
    for i in range(0, 10):
        idlist.append(random.randint(101, 999999999))
    random.shuffle(idlist)

    command_num = random.randint(1, int(config["command_limit"]))
    time_limit = float(config["time_limit"])
    ans = []
    waiters = [{} for i in range(0, int(config["elevator_num"]))]
    for i in range(0, command_num):
        thistime = random.random() * time_limit
        afrom = int(0)
        to = int(0)
        while afrom == to:
            afrom = random.randint(int(config["min_floor"]), int(config["max_floor"]))
            to = random.randint(int(config["min_floor"]), int(config["max_floor"]))
        elevator = random.randint(1, int(config["elevator_num"]))

        string = '[' + format(thistime, '.1f') + ']' + str(idlist[i]) + '-FROM-' + str(afrom) + '-TO-' + str(
            to) + '-BY-' + str(elevator)
        ans.append([thistime, string])
        waiters[elevator - 1][idlist[i]] = [afrom, to, thistime]

    # 按thistime从小到大排序
    ans.sort(key=lambda x: x[0])
    mkdir(f"workspace/{case_id}")
    f = open(f'./workspace/{case_id}/stdin.txt', 'w')
    for i in range(0, command_num):
        f.write(ans[i][1] + '\n')
    f.close()
    return waiters


def run(case_id):
    id = Path(f'./{case_id}')
    in_path = Path(config["in_path"])
    jar_path = Path(config["jar_path"])
    work_path = Path(f'./workspace/{id}')
    set_clock = config["set_clock"]
    clock_time = config["clock_time"]
    execute = in_path.name
    output_path = work_path / 'output.txt'
    shutil.copy(in_path, work_path)
    command = f"{execute} | java -jar {jar_path} > output.txt"
    if set_clock:
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(clock_time)
    try:
        subprocess.run(command, shell=True, cwd=work_path)
    except TimeoutError:
        print(f'{case_id}\t' + '数据点超时')
        return []
    if set_clock:
        signal.alarm(0)
    f = open(output_path, 'r')
    lines = f.readlines()
    f.close()
    return lines


def check(lines, waiters, case_id) -> bool:
    index_line = 0
    index_time = 1
    index_command = 2
    index_floor = 3
    index_elevator = 4
    index_passenger = 5

    info = [[], [], [], [], [], []]  # 电梯i的第几行、时间、指令、楼层、电梯id(、乘客id)
    for i in range(0, len(lines)):
        line = [i + 1]
        matcher = re.match(r'\[\s+(\d+\.\d+)\]([A-Z]*)-(\d+)-(\d+)-?(.*)', lines[i])
        try:
            line.append(float(matcher.group(1)))
            line.append(matcher.group(2))
            if matcher.group(5) != '':
                line.append(int(matcher.group(4)))
                line.append(int(matcher.group(5)))
                line.append(int(matcher.group(3)))
            else:
                line.append(int(matcher.group(3)))
                line.append(int(matcher.group(4)))
            info[line[index_elevator] - 1].append(line)
        except:
            print(f'{case_id}\t' + '第' + str(i + 1) + '行格式错误')
            return False
        if line[index_command] not in ['ARRIVE', 'OPEN', 'CLOSE', 'IN', 'OUT']:
            print(f'{case_id}\t' + '第' + str(i + 1) + '行指令错误')
            return False

    for i in range(0, 6):  # 电梯数量
        passenger = {}  # 电梯内的人
        waiter = waiters[i]  # 等待的人
        last_arrive_time = 0  # 上次到达的时间
        last_arrive_floor = int(config["default_floor"])  # 上次到达的楼层
        last_open_time = 0  # 上次开门的时间
        last_close_time = 1e-9  # 上次关门的时间
        for j in range(0, info[i].__len__()):
            commond = info[i][j][index_command]
            if commond == 'ARRIVE':
                arrive_floor = info[i][j][index_floor]
                if abs(arrive_floor - last_arrive_floor) != 1 or arrive_floor < 1 or arrive_floor > 11:
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '楼层错误')
                    return False
                if info[i][j][index_time] - last_arrive_time < float(config["move_time"]) - float(
                        config["fault_tolerance"]):
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '到达时间错误')
                    return False
                if last_close_time < last_open_time:
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '只有关门后才能移动')
                    return False
                last_arrive_time = info[i][j][index_time]
                last_arrive_floor = arrive_floor
            elif commond == 'OPEN':
                if last_arrive_floor != info[i][j][index_floor]:
                    print(
                        f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '还没到这个楼层')
                    return False
                if last_close_time < last_open_time:
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(
                        i + 1) + '只有关门后才能开门')
                    return False
                last_open_time = info[i][j][index_time]
            elif commond == 'CLOSE':
                if last_arrive_floor != info[i][j][index_floor]:
                    print(
                        f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '还没到这个楼层')
                    return False
                if last_close_time > last_open_time:
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(
                        i + 1) + '只有开门后才能关门')
                    return False
                if info[i][j][index_time] - last_open_time < float(config["open_time"]) + float(
                        config["close_time"]) - float(config["fault_tolerance"]):
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '关门时间错误')
                    return False
                last_close_time = info[i][j][index_time]
            elif commond == 'IN':
                if last_arrive_floor != info[i][j][index_floor]:
                    print(
                        f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '还没到这个楼层')
                    return False
                if last_close_time > last_open_time:
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '门还没开')
                    return False
                if passenger.__len__() >= int(config["max_capacity"]):
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '超载了')
                    return False
                if info[i][j][index_passenger] not in waiter.keys():  # 可能有错
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '不运送此人')
                    return False
                if info[i][j][index_floor] != waiter[info[i][j][index_passenger]][0]:
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(
                        i + 1) + '：正确的人，但不在此层上')
                    return False
                # if info[i][j][index_time] < waiter[info[i][j][index_passenger]][2] - float(config["fault_tolerance"]):
                #     print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(
                #         i + 1) + '：正确的人，但人还没到')
                #     return False
                passenger[info[i][j][index_passenger]] = waiter[info[i][j][index_passenger]]
                waiter.pop(info[i][j][index_passenger])
            elif commond == 'OUT':
                if last_arrive_floor != info[i][j][index_floor]:
                    print(
                        f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '还没到这个楼层')
                    return False
                if last_close_time > last_open_time:
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(i + 1) + '门还没开')
                    return False
                if info[i][j][index_passenger] not in passenger.keys():
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(
                        i + 1) + '走出了不存在的人')
                    return False
                if info[i][j][index_floor] != passenger[info[i][j][index_passenger]][1]:
                    print(f'{case_id}\t' + '第' + str(info[i][j][index_line]) + '行电梯' + str(
                        i + 1) + '：正确的人，但不在此层下')
                    return False
                passenger.pop(info[i][j][index_passenger])
        if last_close_time < last_open_time:
            print(f'{case_id}\t' + '电梯' + str(i + 1) + '记得要关门')
            return False
        if passenger.__len__() > 0:
            print(f'{case_id}\t' + '电梯' + str(i + 1) + '里的乘客还没出来')
            return False
        if waiter.__len__() > 0:
            print(f'{case_id}\t' + '电梯' + str(i + 1) + '还没运送完乘客')
            return False
    print(f'{case_id}\t' + 'Accepted!')
    return True


def mkdir(path):
    if not Path(path).exists():
        Path(path).mkdir()


def process_function(case_id):
    global AllAccepted
    waiters = generate_input(case_id)
    ans = run(case_id)
    if not ans:
        return False
    accept = check(ans, waiters, case_id)
    if config["deleteTempFile"] and accept:
        shutil.rmtree(f'./workspace/{case_id}')
    return accept


if __name__ == "__main__":
    shutil.rmtree('workspace', ignore_errors=True)
    mkdir('workspace')
    test_num = int(config["test_num"])
    max_process = int(config["max_thread_num"])
    results = []
    AllAccepted = True
    pool = multiprocessing.Pool(processes=max_process)
    for i in range(1, test_num + 1):
        result = pool.apply_async(process_function, (i,))
        results.append(result)
    pool.close()
    pool.join()
    for result in results:
        if not result.get():
            AllAccepted = False
            break
    if AllAccepted:
        print("All Accepted!")
    else:
        print("Some Wrong Answer!")
