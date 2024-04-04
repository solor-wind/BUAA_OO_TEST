import re
import json

config = json.load(open('config.json', 'r'))

config = json.load(open('config.json', 'r'))


def analyze_input(inputfile: str) -> dict[int, list[int, int, float]] | str:
    """
    获取乘客信息

    输入为文件路径
    
    输出为字典，键为乘客id，值为[时间,起始楼层,目标楼层]
    
    格式错误返回字符串，表示具体原因
    """
    with open(inputfile) as f:
        lines = f.readlines()
    waiters = {}
    for i in range(len(lines)):
        line = lines[i]
        if 'RESET' in line:
            continue
        matcher = re.match(r'\[\s*(\d+\.\d+)\](\d+)-FROM-(\d+)-TO-(\d+)', line)
        try:
            waiters[int(matcher.group(2))] = [float(matcher.group(1)), int(matcher.group(3)), int(matcher.group(4))]
        except:
            waiters = '第' + str(i + 1) + '行输入格式错误'
            break
    return waiters


# 将输出拆分为每个电梯的行为
def analyze_output(outputfile: str) -> list | str:
    """
    获取输出信息

    输入为文件路径
    
    输出为列表，规范为课程组输出格式
    
    格式错误返回字符串，表示具体原因
    
    """
    with open(outputfile) as f:
        lines = f.readlines()
    actions = []
    for i in range(len(lines)):
        line = lines[i]
        # 对此解析
        # [ 4.6950]RESET_ACCEPT-1-8-0.3
        matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+).*', line)
        try:
            if matcher.group(2) in ['ARRIVE', 'OPEN', 'CLOSE', 'RECEIVE']:
                matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+)-(\d+)-(\d+)', line)
                actions.append(
                    [float(matcher.group(1)), matcher.group(2), int(matcher.group(3)), int(matcher.group(4))])
            elif matcher.group(2) in ['IN', 'OUT']:
                matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+)-(\d+)-(\d+)-(\d+)', line)
                actions.append([float(matcher.group(1)), matcher.group(2), int(matcher.group(3)), int(matcher.group(4)),
                                int(matcher.group(5))])
            elif matcher.group(2) == 'RESET_ACCEPT':
                matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+)-(\d+)-(\d+)-(\d+\.\d+)', line)
                actions.append([float(matcher.group(1)), matcher.group(2), int(matcher.group(3)), int(matcher.group(4)),
                                float(matcher.group(5))])
            elif matcher.group(2) in ['RESET_BEGIN', 'RESET_END']:
                matcher = re.match(r'\[\s*(\d+\.\d+)\]([A-Z_]+)-(\d+)', line)
                actions.append([float(matcher.group(1)), matcher.group(2), int(matcher.group(3))])
            else:
                return '第' + str(i + 1) + '行输出格式错误'
        except:
            return '第' + str(i + 1) + '行输出格式错误'
    return actions


class elevator:
    def __init__(self):
        self.capacity=int(config['capacity'])
        self.speed=float(config['move_time'])
        self.open_time=float(config['open_time'])
        self.close_time=float(config['close_time'])
        
        self.last_opentime=0
        self.last_closetime=1e-9
        self.last_arrivetime=0
        self.floor=int(config['default_floor'])
        self.passengers={}
        self.receiver={}

        self.reset = []
        self.reset_floor = 0


def check(waiters, actions) -> str:
    if type(waiters) == str:
        return waiters
    if type(actions) == str:
        return actions

    elevators = [elevator() for i in range(7)]
    received_waiters = {}
    tolerance = 0.02

    for i in range(0, len(actions)):
        action = actions[i]
        match action[1]:
            case 'RESET_ACCEPT':
                if elevators[action[2]].reset != []:
                    return '第' + str(i + 1) + '行电梯' + str(action[2]) + '还未结束上次重置'
                elevators[action[2]].reset.append(action)
                elevators[action[2]].reset_floor = 0
            case 'RESET_BEGIN':
                if elevators[action[2]].reset.__len__() != 1 or elevators[action[2]].reset[0][1] != 'RESET_ACCEPT':
                    return '第' + str(i + 1) + '行电梯' + str(action[2]) + '没收到重置信号'  # 描述不准确
                elif elevators[action[2]].passengers != {}:
                    return '第' + str(i + 1) + '行电梯' + str(action[2]) + '人还没出来就重置'
                elif elevators[action[2]].last_closetime < elevators[action[2]].last_opentime:
                    return '第' + str(i + 1) + '行电梯' + str(action[2]) + '还没关门就重置'
                elif elevators[action[2]].reset_floor > 2:  # 没有容错
                    return '第' + str(i + 1) + '行电梯' + str(action[2]) + '没在2次移动内重置'
                for p in elevators[action[2]].receiver:  # 取消分配
                    waiters[p] = elevators[action[2]].receiver[p]
                    received_waiters.pop(p)
                elevators[action[2]].receiver.clear()
                elevators[action[2]].reset.append(action)
            case 'RESET_END':
                if elevators[action[2]].reset.__len__()!=2 or not ('RESET_ACCEPT' in elevators[action[2]].reset[0] and 'RESET_BEGIN' in elevators[action[2]].reset[1]):
                    return '第'+str(i+1)+'行电梯'+str(action[2])+'重置的前提错误'   #描述不准确
                elif action[0]-elevators[action[2]].reset[0][0]>5+tolerance:  #没有容错
                    return '第'+str(i+1)+'行电梯'+str(action[2])+'重置accept到end时间过长'
                elif action[0]-elevators[action[2]].reset[1][0]<1.2-tolerance:    #有容错
                    return '第'+str(i+1)+'行电梯'+str(action[2])+'重置所用时间错误'
                elevators[action[2]].capacity=elevators[action[2]].reset[0][3]
                elevators[action[2]].speed=elevators[action[2]].reset[0][4]
                elevators[action[2]].reset=[]
                elevators[action[2]].reset_floor=0
            case 'RECEIVE':
                # 同一乘客被分配到多个电梯、多次输出receive
                if action[2] in received_waiters.keys():
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '乘客' + str(action[2]) + '被重复分配'
                elif action[2] not in waiters.keys():
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '乘客' + str(action[2]) + '不存在'
                elif elevators[action[3]].reset.__len__() == 2:
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '重置期间禁止receive乘客'
                received_waiters[action[2]] = waiters[action[2]]
                elevators[action[3]].receiver[action[2]] = waiters[action[2]]
                waiters.pop(action[2])
            case 'ARRIVE':
                if action[2]>11 or action[2]<1:
                    return '第'+str(i+1)+'行电梯'+str(action[3])+'飞天遁地'
                elif action[0]-elevators[action[3]].last_arrivetime<elevators[action[3]].speed-tolerance:    #有容错
                    return '第'+str(i+1)+'行电梯'+str(action[3])+'超速了'
                elif elevators[action[3]].last_opentime>elevators[action[3]].last_closetime:
                    return '第'+str(i+1)+'行电梯'+str(action[3])+'还没关门就移动'
                elif elevators[action[3]].passengers==[] and elevators[action[3]].receiver=={}:
                    return '第'+str(i+1)+'行电梯'+str(action[3])+'没人就移动'
                elif elevators[action[3]].reset.__len__()==2:
                    return '第'+str(i+1)+'行电梯'+str(action[3])+'重置期间禁止移动'
                elif abs(elevators[action[3]].floor-action[2])!=1:
                    return '第'+str(i+1)+'行电梯'+str(action[3])+'移动超过1层'
                elevators[action[3]].floor=action[2]
                elevators[action[3]].last_arrivetime=action[0]
                elevators[action[3]].reset_floor+=1
            case 'OPEN':
                if elevators[action[3]].reset.__len__() == 2:
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '重置期间禁止开关门'
                elif elevators[action[3]].floor != action[2]:
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '开门楼层与上次到达楼层不符'
                elif elevators[action[3]].last_opentime > elevators[action[3]].last_closetime:
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '还没关门就开门'
                elevators[action[3]].last_opentime = action[0]
            case 'CLOSE':
                if elevators[action[3]].reset.__len__() == 2:
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '重置期间禁止开关门'
                elif elevators[action[3]].floor != action[2]:
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '关门楼层与上次到达楼层不符'
                elif elevators[action[3]].last_opentime < elevators[action[3]].last_closetime:
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '还没开门就关门'
                elif action[0] - elevators[action[3]].last_opentime < elevators[action[3]].open_time + elevators[
                    action[3]].close_time - tolerance:  # 有容错
                    return '第' + str(i + 1) + '行电梯' + str(action[3]) + '开关门时间过短'
                elevators[action[3]].last_closetime = action[0]
            case 'IN':
                if elevators[action[4]].reset.__len__() == 2:
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '重置期间禁止进入'
                elif elevators[action[4]].floor != action[3]:
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '进入楼层与上次到达楼层不符'
                elif elevators[action[4]].last_opentime < elevators[action[4]].last_closetime:
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '还没开门就进入'
                elif elevators[action[4]].passengers.__len__() + 1 > elevators[action[4]].capacity:
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '超载'
                elif action[2] not in elevators[action[4]].receiver.keys():
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '乘客' + str(action[2]) + '未分配'
                elif received_waiters[action[2]][1] != action[3]:
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '乘客' + str(action[2]) + '不在此层上'
                elevators[action[4]].passengers[action[2]] = received_waiters[action[2]]
                # elevators[action[4]].receiver.pop(action[2])
                # received_waiters.pop(action[2])
            case 'OUT':
                if elevators[action[4]].reset.__len__() == 2:
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '重置期间禁止出去'
                elif elevators[action[4]].floor != action[3]:
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '出去楼层与上次到达楼层不符'
                elif elevators[action[4]].last_opentime < elevators[action[4]].last_closetime:
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '还没开门就出去'
                elif action[2] not in elevators[action[4]].passengers.keys():
                    return '第' + str(i + 1) + '行电梯' + str(action[4]) + '乘客' + str(action[2]) + '不在电梯里'
                if elevators[action[4]].passengers[action[2]][2] != action[3]:
                    waiters[action[2]] = elevators[action[4]].passengers[action[2]]
                    waiters[action[2]][1] = action[3]
                elevators[action[4]].receiver.pop(action[2])
                received_waiters.pop(action[2])
                elevators[action[4]].passengers.pop(action[2])
    for i in range(1, len(elevators)):
        if elevators[i].reset != []:
            return '电梯' + str(i) + '还未结束重置'
        if elevators[i].passengers != {}:
            return '电梯' + str(i) + '还有乘客'
        if elevators[i].last_opentime > elevators[i].last_closetime:
            return '电梯' + str(i) + '还没关门'
    if waiters != {}:
        return '还有乘客没送完'
    return 'Accepted!'
