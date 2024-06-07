import random
import os
import json
import signal
import subprocess

import equivalent
from Standardize import standardize_expr, derivative


##############################--对于时间过长的处理--###########################

def handler(signum, frame):
    raise TimeoutError


##############################--全局变量的定义--##############################

config = json.load(open("config.json", encoding='utf-8'))
isgenerateFun = False  # 是否正在产生自定义函数

# test_num=1  #测试用例数
# term_limit=5    #项数上限
# factor_limit=5  #因子数上限
# floor=3   #括号嵌套层数上限

# deltaFactor=0.15    #求导因子概率
# expFunFactor=0.15    #指数函数因子概率
# myFunFactor=0.15    #自定义函数因子概率
# exprFactor=0.15    #表达式因子概率

# expFunFactor_exp=0.2    #指数函数因子后携带指数的概率
# exprFactor_exp=0.2  #表达式因子后携带指数的概率
# constFactor_zero=0.05    #常数因子中产0概率
# constFactor_big=0.05    #常数因子中产大数概率

# blank_prob=0.3   #空白符概率
# sign_prob=0.5    #多余正负号的概率
# zero_prob=0.1    #前导0概率

# automyFun=True  #是否自动生成自定义函数
# myFun_floor=1   #自定义函数因子中的表达式层数上限
# myFun_term_limit=3  #自定义函数因子中的项数上限
# myFun_factor_limit=3    #自定义函数因子中的因子数上限
myFun_name = []  # 函数名
myFun_parameter = []  # 参数
myFun_function = []  # 函数
myFun_dict = {}  # 函数名与其参数，表达式的映射字典

SetClock = True  # 是否设置时钟，若为windows建议在config将此选项关闭
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
    return string + str(random.randint(0, 8))  # 指数上限


##############################--不同因子的生成--##############################

def generate_delta(floor):  # 求导因子
    string = 'dx' + generate_blank() + '(' + generate_blank()
    if floor <= 1:
        if random.random() < 0.5:
            string = string + generate_constant()
        else:
            string = string + generate_power()
    else:
        string = string + generate_factor(floor)  # 方便求导因子内部更加复杂
    string = string + generate_blank() + ')'
    return string


def generate_expFun(floor):  # 指数函数因子
    string = 'exp' + generate_blank() + '(' + generate_blank() + generate_factor(floor - 1) + generate_blank() + ')'
    if random.random() < config["expFunFactor_exp"]:
        string = string + generate_blank() + generate_exp()
    return string


def generate_myFun(floor):  # 自定义函数因子
    if myFun_function.__len__() == 0:
        return generate_factor(floor)  # 没有自定义函数时重新产生因子
    key = random.randint(0, myFun_function.__len__() - 1)
    string = myFun_name[key] + generate_blank() + '(' + generate_blank() + generate_factor(floor - 1) + generate_blank()
    for i in range(1, myFun_parameter[key].__len__()):
        string = string + ',' + generate_blank() + generate_factor(floor - 1) + generate_blank()
    return string + ')'


def generate_exprF(floor):  # 表达式因子
    string = '(' + generate_blank() + generate_expr(floor - 1) + generate_blank() + ')'
    if random.random() < float(config["exprFactor_exp"]):
        string = string + generate_blank() + generate_exp()
    return string


def generate_constant():  # 常数因子
    constFactor_zero = config["constFactor_zero"]
    constFactor_big = config["constFactor_big"]
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
    return 'x' + generate_blank() + generate_exp()


##############################--表达式、项、因子、自定义函数的生成--##############################

def generate_fun():  # 产生自定义函数
    global myFun_name, myFun_parameter, myFun_function, isgenerateFun
    myFun_name = []  # 函数名
    myFun_parameter = []  # 参数
    myFun_function = []  # 函数
    isgenerateFun = True
    num = random.randint(0, 3)
    namelist = ['f', 'g', 'h']

    for i in range(0, num):
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

    isgenerateFun = False


def generate_factor(floor):  # 产生因子
    probability = random.random()
    control = int(config["floor"]) - floor + 1
    if isgenerateFun:
        deltaFactor = 0
    else:
        deltaFactor = float(config["deltaFactor"])
    expFunFactor = float(config["expFunFactor"])
    myFunFactor = float(config["myFunFactor"])
    exprFactor = float(config["exprFactor"])

    if floor <= 0:
        if random.random() < 0.5:
            return generate_constant()
        else:
            return generate_power()

    if probability < deltaFactor / control:
        return generate_delta(floor - 1)
    elif probability < (deltaFactor + expFunFactor) / control:
        string = generate_expFun(floor - 1)
        return string
    elif probability < (deltaFactor + myFunFactor + expFunFactor) / control:
        return generate_myFun(floor - 1)
    elif probability < (deltaFactor + myFunFactor + expFunFactor + exprFactor) / control:
        return generate_exprF(floor - 1)
    else:
        if random.random() < 0.5:
            return generate_constant()
        else:
            return generate_power()


def generate_term(floor):  # 产生项
    string = generate_sign() + generate_blank() + generate_factor(floor)
    if isgenerateFun:
        factor_limit = int(config["myFun_factor_limit"]) / (int(config["myFun_floor"]) - floor + 1)
    else:
        factor_limit = int(config["factor_limit"]) / (int(config["floor"]) - floor + 1)
    for i in range(0, int(factor_limit - 1)):
        string = string + generate_blank() + '*' + generate_blank() + generate_factor(floor)
    return string


def generate_expr(floor):  # 产生表达式
    string = generate_blank() + generate_sign() + generate_blank() + generate_term(floor) + generate_blank()
    if isgenerateFun:
        term_limit = int(config["myFun_term_limit"]) / (int(config["myFun_floor"]) - floor + 1)
    else:
        term_limit = int(config["term_limit"]) / (int(config["floor"]) - floor + 1)
    for i in range(0, int(term_limit - 1)):
        if random.random() > 0.5:
            string = string + '+'
        else:
            string = string + '-'
        string = string + generate_blank() + generate_term(floor) + generate_blank()
    return string


##############################--主函数--##############################

if __name__ == "__main__":
    config = json.load(open("config.json", encoding='utf-8'))
    test_num = int(config["test_num"])  # 测试用例数
    floor = int(config["floor"])  # 括号嵌套层数上限
    automyFun = bool(config["automyFun"])  # 是否自动生成自定义函数

    jarPath = config["jarPath"]

    SetClock = bool(config["SetClock"])
    ClockTime = int(config["ClockTime"])

    inputs = []
    standardize_inputs = []
    passed = True

    if SetClock:
        signal.signal(signal.SIGALRM, handler)

    with (open("testcases.txt", "w") as f_testcases, open("extended.txt", "w") as f_extended):
        for i in range(0, test_num):
            f_testcases.write(str(i + 1) + "\n")
            if automyFun:
                generate_fun()
            else:
                myFun_name = config["myFun_name"]
                myFun_parameter = config["myFun_parameter"]
                myFun_function = config["myFun_function"]
            myFun_dict = dict(zip(myFun_name, zip(myFun_parameter, myFun_function)))
            f_testcases.write('\t' + str(myFun_name.__len__()) + "\n")
            inputs.append(str(myFun_name.__len__()) + "\n")
            for j in range(0, myFun_name.__len__()):
                tmp_function = myFun_name[j] + generate_blank() + '(' + generate_blank()
                tmp_function = tmp_function + ','.join(myFun_parameter[j])
                tmp_function = tmp_function + generate_blank() + ')' + generate_blank() + '=' + generate_blank() + \
                               myFun_function[j]
                f_testcases.write('\t' + tmp_function + "\n")
                inputs.append(tmp_function + "\n")
            NotStandardizedExpr = generate_expr(floor)
            StandardizedExpr = standardize_expr(NotStandardizedExpr, myFun_dict)
            StandardizedExpr = derivative(StandardizedExpr)
            f_extended.write(StandardizedExpr + "\n")
            standardize_inputs.append(StandardizedExpr)
            f_testcases.write('\t' + NotStandardizedExpr + "\n")
            inputs.append(NotStandardizedExpr + "\n")
    inputs_index = 0
    standardize_inputs_index = 0
    with open("result.txt", "w") as result_file:
        while (inputs_index < len(inputs)):
            proc = subprocess.Popen(['/mnt/c/Program Files/Common Files/Oracle/Java/javapath/java.exe', '-jar', jarPath, '>result.txt'], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, text=True)
            num = int(inputs[inputs_index])
            for j in range(inputs_index, inputs_index + num + 2):
                proc.stdin.write(inputs[j])
            proc.stdin.flush()
            if SetClock:
                signal.alarm(ClockTime)
            try:
                output, error = output, error = proc.communicate()
                if not equivalent.expressions_are_equivalent(standardize_inputs[standardize_inputs_index], output):
                    print("第", standardize_inputs_index + 1, "个测试用例不通过, 您的输出为", output)
                    passed = False
                else:
                    print("第", standardize_inputs_index + 1, "个测试用例AC")
                if SetClock:
                    signal.alarm(0)
            except TimeoutError:
                print("第", standardize_inputs_index + 1, "个测试用例超时,已为您跳过")
            except OverflowError or MemoryError:
                print("数据过大， 已为您跳过第", standardize_inputs_index + 1, "条数据点")
            except SyntaxError:
                print("出现未知错误，已为您跳过该数据")
            except Exception as e:
                print("第", standardize_inputs_index + 1, "个测试用例不通过, 您的输出为", output)
                print("也有可能是其它错误")
                passed = False
            standardize_inputs_index = standardize_inputs_index + 1
            inputs_index = inputs_index + num + 2
            if not output.endswith("\n"):
                output += '\n'
            result_file.write(output)
    if passed:
        print("您已通过全部测试样例")
