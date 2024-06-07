from sympy import symbols, simplify
from Standardize import delLeadingZero

def expressions_are_equivalent(expr1, expr2):
    x = symbols('x')
    # 将表达式转换为 SymPy 的表达式
    sympy_expr1 = simplify(expr1)
    sympy_expr2 = simplify(expr2)

    # 使用 equals() 方法比较两个表达式是否相等
    return sympy_expr1.equals(sympy_expr2)


# 测试
if __name__ == "__main__":
    expr1 = input("请输入第一个表达式：")
    expr2 = input("请输入第二个表达式：")
    expr1 = delLeadingZero(expr1)
    expr2 = delLeadingZero(expr2)
    print(expressions_are_equivalent(expr1, expr2))
    # x = symbols('x')
    # sympy_expr1 = simplify(expr1)
    # print(sympy_expr1)
