import re

from stack import Stack


def standardize_expr(expr, myFun_dict) -> str:         # 标准化表达式(去除函数，去除前导零)
    parametera = ""
    parameteras = Stack()
    item = Stack()
    pos = 0
    while pos < expr.__len__():
        if expr[pos] == 'f' or expr[pos] == 'g' or expr[pos] == 'h':
            item.push(expr[pos])
            parameteras.push(parametera)
            parametera = ""
        elif expr[pos] == '(':
            if not (item.top() == 'f' or item.top() == 'g' or item.top() == 'h'):
                parametera = parametera + expr[pos]
            item.push(expr[pos])
        elif expr[pos] == ')':
            item.pop()
            if item.top() == 'f' or item.top() == 'g' or item.top() == 'h':
                parameteras.push(parametera)
                parametera_num = myFun_dict[item.top()][0].__len__()
                parameteras_list = parameteras.popList(parametera_num)
                parameteras_list.reverse()
                string1 = replace_expr(parameteras_list, item.top(), myFun_dict)
                parametera = parameteras.pop() + string1
                item.pop()
            else:
                parametera = parametera + expr[pos]
        elif expr[pos] == ',':
            parameteras.push(parametera)
            parametera = ""
        else:
            parametera = parametera + expr[pos]
        pos = pos + 1
    return delLeadingZero(parametera)


def replace_expr(parametras_list, fun_name, myFun_dict) -> str:         # 进行前导零的替换
    vars_list = myFun_dict[fun_name][0]
    fun_expr = myFun_dict[fun_name][1]
    if 'x' in vars_list:
        x_index = vars_list.index('x')
        vars_list = [vars_list[x_index]] + vars_list[:x_index] + vars_list[x_index + 1:]
        parametras_list = [parametras_list[x_index]] + parametras_list[:x_index] + parametras_list[x_index + 1:]
    fun_expr = fun_expr.replace("exp", "#")
    i = 0
    while i < vars_list.__len__():
        toReplace = '(' + parametras_list[i] + ')'
        fun_expr = fun_expr.replace(vars_list[i], toReplace)
        i = i + 1
    fun_expr = fun_expr.replace("#", "exp")
    return '(' + fun_expr + ')'


def delLeadingZero(expr) -> str:
    expr = re.sub(r'(?<![0-9])0+(\d+)', r'\1', expr)
    return expr


if __name__ == "__main__":
    # 测试字符串替换功能
    # myFun_dict = {'f': [['x', 'y'], 'x+y'], 'g': [['x', 'y'], 'x-y'], 'h': [['x', 'y'], 'x*y']}
    # expr = "f(x, g(x, h(x, x)))"
    # print(standardize_expr(expr, myFun_dict))

    # 测试去除前导零功能
    str = "+exp(905077028)^1*	-20* -11*x ^07*f( 0	, x^+8)"
    str = delLeadingZero(str)
    print(str)
