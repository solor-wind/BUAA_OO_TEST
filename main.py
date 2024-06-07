import random
import signal
import json
import subprocess

import equivalent
from Standardize import standardize_expr


##############################--对于时间过长的处理--###########################

def handler(signum, frame):
    raise TimeoutError


##############################--全局变量的定义--##############################

config = json.load(open("config.json", encoding='utf-8'))
limit = 10  # 限制生成的基本单元数,每次更新

unit_up_limit = 10  # 基本单元数上限

# blank_prob=0.3   #空白符概率
# sign_prob=0.5    #多余正负号的概率
# zero_prob=0.1    #前导0概率

expFunFactor = 0.2  # 指数函数因子概率
# expFunFactor_exp=0.2    #指数函数因子后携带指数的概率
myFunFactor = 0  # 自定义函数因子概率
exprFactor = 0.2  # 表达式因子概率
constFactor = 0.3  # 常数因子概率
# constFactor_zero=0.05    #常数因子中产0概率
# constFactor_big=0.05    #常数因子中产大数概率
powerFunFactor = 0.3  # 幂函数因子概率

myFun_name = []  # 函数名
myFun_parameter = []  # 参数
myFun_function = []  # 函数
myFun_dict = {}  # 函数名-函数字典

SetClock = True # 是否设置时钟，若为windows建议将此选项关闭
ClockTime = 20  # 时钟时间


##############################--小函数--##############################
# 生成空白符、正负号、前导0、指数
def generate_blank():
    if random.random() < float(config["blank_prob"]):
        if random.random() < 0.8:
            return ' '
        else:
            return '\t'
    else:
        return ''


def generate_sign():
    if random.random() < float(config["sign_prob"]):
        return ''
    else:
        if random.random() > 0.5:
            return '+'
        else:
            return '-'


def generate_zero():
    if random.random() < float(config["zero_prob"]):
        return '0'
    else:
        return ''


def generate_exp():
    string = '^' + generate_blank()
    if random.random() > float(config["sign_prob"]):
        string = string + '+'
    string = string + generate_zero()
    return string + str(random.randint(0, 8))  # 指数上限？


##############################--不同因子的生成--##############################

def generate_constant():  # 常数因子
    global limit
    constFactor_zero = config["constFactor_zero"]
    constFactor_big = config["constFactor_big"]
    limit = limit - 1
    probability = random.random()
    tmp = 0
    if probability < constFactor_zero:
        return generate_sign() + '0'
    elif probability < constFactor_zero + constFactor_big:
        tmp = random.randint(-999999999, 999999999)
    else:
        tmp = random.randint(-20, 20)
    if tmp > 0:
        return generate_sign().replace('-', '+') + str(tmp)
    else:
        return str(tmp)


def generate_power():  # 幂函数因子
    global limit
    limit = limit - 1
    return 'x' + generate_blank() + generate_exp()


def generate_expFun(floor):  # 指数函数因子
    string = 'exp' + generate_blank() + '(' + generate_blank() + generate_factor(floor - 1) + generate_blank() + ')'
    if random.random() < config["expFunFactor_exp"]:
        string = string + generate_blank() + generate_exp()
    return string


def generate_myFun(floor):  # 自定义函数因子
    if myFun_name.__len__() == 0:
        return generate_factor(floor)  # 没有自定义函数时重新产生因子
    key = random.randint(0, myFun_function.__len__() - 1)
    string = myFun_name[key] + generate_blank() + '(' + generate_blank() + generate_factor(floor - 1) + generate_blank()
    # string=string+generate_factor(floor-1).replace('exp','a').replace('x',myFun_parameter[key][0]).replace('a','exp')
    # string=string+generate_blank()
    for i in range(1, myFun_parameter[key].__len__()):
        string = string + ',' + generate_blank() + generate_factor(floor - 1) + generate_blank()
        # string=string+generate_factor(floor-1).replace('exp','a').replace('x',myFun_parameter[key][i]).replace('a','exp')
        # string=string+generate_blank()+generate_blank()
    return string + ')'


##############################--表达式、项、因子、自定义函数的生成--##############################

def generate_fun():  # 产生自定义函数
    global myFun_name, myFun_parameter, myFun_function, myFunFactor, limit, constFactor, powerFunFactor
    myFun_name = []  # 函数名
    myFun_parameter = []  # 参数
    myFun_function = []  # 函数
    tmp_myFun = myFunFactor
    myFunFactor = 0  # 自定义函数因子概率调成0，不能再生成自定义函数
    constFactor += tmp_myFun / 2
    powerFunFactor += tmp_myFun / 2
    num = random.randint(0, 3)
    namelist = ['f', 'g', 'h']
    for i in range(0, num):
        limit = config["myFun_unit_limit"]
        myFun_name.append(random.choice(namelist))
        namelist.remove(myFun_name[i])

        canshu_num = random.randint(1, 3)
        canshulist = ['x', 'y', 'z']
        tmp_canshu = []
        for j in range(0, canshu_num):
            tmp_canshu.append(random.choice(canshulist))
            canshulist.remove(tmp_canshu[j])
        myFun_parameter.append(tmp_canshu)

        tmp_function = generate_expr(config["myFun_floor"])
        # 随机替换参数
        pos = 0
        j = 0
        while pos < tmp_function.__len__():
            if tmp_function[pos] == 'x' and (pos + 1 == tmp_function.__len__() or tmp_function[pos + 1] != 'p'):
                tmp_list = list(tmp_function)
                tmp_list[pos] = myFun_parameter[i][j]
                tmp_function = ''.join(tmp_list)
                j += 1
                if j == canshu_num:
                    break
            pos += 1
        while pos < tmp_function.__len__():
            if tmp_function[pos] == 'x' and (pos + 1 == tmp_function.__len__() or tmp_function[pos + 1] != 'p'):
                tmp_list = list(tmp_function)
                tmp_list[pos] = random.choice(myFun_parameter[i])
                tmp_function = ''.join(tmp_list)
            pos += 1
        myFun_function.append(tmp_function)
    myFunFactor = tmp_myFun
    constFactor -= tmp_myFun / 2
    powerFunFactor -= tmp_myFun / 2


def generate_factor(floor):  # 产生因子
    global expFunFactor, myFunFactor, constFactor, powerFunFactor, limit
    # expFunFactor=float(config["expFunFactor"])
    # myFunFactor=config["myFunFactor"]
    # constFactor=config["constFactor"]
    # powerFunFactor=config["powerFunFactor"]
    probability = random.random()
    if floor <= 0:
        if constFactor + powerFunFactor == 0:
            return '0'
        elif probability < constFactor / (constFactor + powerFunFactor):
            return generate_constant()
        else:
            return generate_power()
    if probability < expFunFactor:
        tmp_limit = limit - limit / 2
        limit /= 2  ########
        string = generate_expFun(floor - 1)
        limit += tmp_limit
        return string
    elif probability < myFunFactor + expFunFactor:
        return generate_myFun(floor - 1)
    elif probability < myFunFactor + expFunFactor + exprFactor:
        tmp_limit = limit - limit / 2
        limit /= 2  ########
        string = '(' + generate_expr(floor - 1) + ')'
        limit += tmp_limit
        return string
    elif probability < myFunFactor + expFunFactor + exprFactor + constFactor:
        return generate_constant()
    else:
        return generate_power()


def generate_term(floor):  # 产生项
    global limit
    string = generate_sign() + generate_blank() + generate_factor(floor)
    tmp_limit = int(limit / (int(config["floor"]) - floor + 1) / 2)  # limit会变########
    for i in range(0, tmp_limit - 1):
        string = string + generate_blank() + '*' + generate_blank() + generate_factor(floor)
        if limit <= tmp_limit / 3 * 2:
            break
    return string


def generate_expr(floor):  # 产生表达式
    global limit
    string = ''
    string = string + generate_blank() + generate_sign() + generate_blank() \
             + generate_term(floor) + generate_blank()
    tmp_limit = int(limit / (int(config["floor"]) - floor + 1))  # limit会变########
    for i in range(0, tmp_limit - 1):
        if random.random() > 0.5:
            string = string + '+'
        else:
            string = string + '-'
        string = string + generate_blank() + generate_term(floor) + generate_blank()
        if limit <= 0:
            break
    return string


##############################--主函数--##############################

if __name__ == "__main__":
    config = json.load(open("config.json", encoding='utf-8'))
    test_num = int(config["test_num"])  # 测试用例数
    unit_low_limit = int(config["unit_low_limit"])  # 基本单元数下限
    unit_up_limit = int(config["unit_up_limit"])  # 基本单元数上限
    floor = int(config["floor"])  # 括号嵌套层数上限
    automyFun = bool(config["automyFun"])  # 是否自动生成自定义函数

    expFunFactor = float(config["expFunFactor"])
    myFunFactor = float(config["myFunFactor"])
    constFactor = float(config["constFactor"])
    powerFunFactor = float(config["powerFunFactor"])

    jarPath = config["jarPath"]

    SetClock = bool(config["SetClock"])
    ClockTime = int(config["ClockTime"])

    inputs = []
    standardize_inputs = []
    passed = True

    # if SetClock:
    #     signal.signal(signal.SIGALRM, handler)

    with (open("testcases.txt", "w") as f_testcases, open("extended.txt", "w") as f_extended):
        for inputs_index in range(0, test_num):
            f_testcases.write(str(inputs_index + 1) + "\n")
            if automyFun:
                generate_fun()
            else:
                myFun_name = config["myFun_name"]
                myFun_parameter = config["myFun_parameter"]
                myFun_function = config["myFun_function"]
            myFun_dict = {key: value for key, value in zip(myFun_name, zip(myFun_parameter, myFun_function))}
            f_testcases.write('\t' + str(myFun_name.__len__()) + "\n")
            inputs.append(str(myFun_name.__len__()) + "\n")
            for j in range(0, myFun_name.__len__()):
                tmp_function = myFun_name[j] + generate_blank() + '(' + generate_blank()
                tmp_function = tmp_function + ','.join(myFun_parameter[j])
                tmp_function = tmp_function + generate_blank() + ')' + generate_blank() + '=' + generate_blank() + \
                               myFun_function[j]
                f_testcases.write('\t' + tmp_function + "\n")
                inputs.append(tmp_function + "\n")
            limit = random.randint(unit_low_limit, unit_up_limit)
            NotStandardizedExpr = generate_expr(floor)
            StandardizedExpr = standardize_expr(NotStandardizedExpr, myFun_dict)
            f_extended.write(StandardizedExpr + "\n")
            standardize_inputs.append(StandardizedExpr)
            f_testcases.write('\t' + NotStandardizedExpr + "\n")
            inputs.append(NotStandardizedExpr + "\n")
    inputs_index = 0
    standardize_inputs_index = 0
    passed = True
    with open("result.txt", "w") as result_file:
        while (inputs_index < len(inputs)):
            proc = subprocess.Popen(['java', '-jar', jarPath, '>result.txt'], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            num = int(inputs[inputs_index])
            for j in range(inputs_index, inputs_index + num + 2):
                proc.stdin.write(inputs[j])
            proc.stdin.flush()
            # if SetClock:
            #     signal.alarm(ClockTime)
            try:
                output, error = output, error = proc.communicate()
                if not equivalent.expressions_are_equivalent(standardize_inputs[standardize_inputs_index], output):
                    print("第", standardize_inputs_index + 1, "个测试用例不通过, 您的输出为", output)
                    passed = False
                else:
                    print("第", standardize_inputs_index + 1, "个测试用例AC")
                # if SetClock:
                #     signal.alarm(0)
            except TimeoutError:
                print("第", standardize_inputs_index + 1, "个测试用例超时,已为您跳过")
            except OverflowError or MemoryError:
                print("数据过大， 已为您跳过第",  standardize_inputs_index + 1,  "条数据点")
            except Exception as e:
                print("第", standardize_inputs_index + 1, "个测试用例不通过, 您的输出为", output)
                passed = False
            standardize_inputs_index = standardize_inputs_index + 1
            inputs_index = inputs_index + num + 2
            result_file.write(output)
    if passed:
        print("您已通过全部测试样例")
