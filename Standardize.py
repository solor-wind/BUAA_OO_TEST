import re

from stack import Stack
from sympy import symbols, simplify, diff

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


def replace_expr(parametras_list, fun_name, myFun_dict) -> str:
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
    fun_expr = standardize_expr(fun_expr, myFun_dict)
    return '(' + fun_expr + ')'


def delLeadingZero(expr) -> str:
    expr = re.sub(r'(?<![0-9])0+(\d+)', r'\1', expr)
    return expr

def derivative(expr) -> str:     # 需要在标准化，去除前导零之后使用
    x = symbols('x')
    parametras = Stack()
    parametra = ""
    items = Stack()
    pos = 0
    while pos < expr.__len__():
        if expr[pos] == 'd':
            items.push("dx")
            parametras.push(parametra)
            parametra = ""
            pos = pos + 1
        elif expr[pos] == '(':
            if not items.top() == "dx":
                parametra = parametra + expr[pos]
            items.push(expr[pos])
        elif expr[pos] == ')':
            items.pop()
            if items.top() == "dx":
                parametra = diff(parametra, x)
                parametra = str(parametra)
                parametra = parametras.pop() + '(' + parametra + ')'
                items.pop()
            else:
                parametra = parametra + expr[pos]
        else:
            parametra = parametra + expr[pos]
        pos = pos + 1
    return parametra.replace("**", "^")

if __name__ == "__main__":
    # 测试字符串替换功能
    myFun_dict = {'h': [['x', 'y'], 'y^+2 *exp(x^+2)^+8* exp( 14)^2+-	-16*6*0'],
                  'f': [['z', 'y', 'x'], '+-15*15* -12++	z^+5*( +y ^+8)^+1 *z^+0+	-3* h (y^2,z^7)*-6']}
    expr = "-f((6*x^5),10,-16 ) *(  -+20)*x ^ 4"
    print(standardize_expr(expr, myFun_dict))

    # 测试去除前导零功能
    # str = "+exp(905077028)^1*	-20* -11*x ^07*f( 0	, x^+8)"
    # str = delLeadingZero(str)
    # print(str)

    # 测试求导功能
    # expr = "x*dx(exp(2*x^2))"
    # print(derivative(expr))