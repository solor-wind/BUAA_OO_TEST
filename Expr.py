import random
import subprocess
import pathlib
from os import system
import time
import sys

def checkMain(**kwargs):
    def pre_handle(s):
        out = ""
        num_temp = ""
        for c in s:
            if c.isdigit():
                num_temp += c
                continue
            if num_temp != "":
                num_temp = num_temp.lstrip("0")
                out += num_temp if num_temp != "" else "0"
            num_temp = ""
            if c == '^':
                out += '**'
            else:
                out += c
        if num_temp != "":
            num_temp = num_temp.lstrip("0")
            out += num_temp if num_temp != "" else "0"
        return out

    fin = kwargs.get("fin")
    fout = kwargs.get("fout")

    stdin = fin.read()
    stdout = fout.read()

    if '(' in stdout or ')' in stdout:
        return False, "Has '(' or ')' in your answer!"

    length = len(stdout)
    raw_output = stdout
    stdin = pre_handle(stdin)
    stdout = pre_handle(stdout)

    for _ in range(1000):
        x = random.randint(-1000, 1000)
        try:
            if eval(stdin) != eval(stdout):
                return False, f"Wrong Answer When x = {x}"
        except Exception as e:
            return False, f"Checker Error When x = {x} For {repr(e)}"
    return True, f"Answer length: {length}\n\033[33m{raw_output}\033[0m"


def genNumber(low=-10, high=10):
    result = random.randint(low, high)
    if -1 <= result <= 1:
        result = random.randint(low, high)
    if random.random() > 0.8:
        zero = random.randint(1, 2)
    else:
        zero = 0
    return f"{'-' if result < 0 else ''}{'0' * zero}{abs(result)}"


def genPower():
    s = "x"
    if random.random() > 0.3:
        s += "^" + genNumber(low=0, high=6)
    return s


def genFractor(allow_nest=True):
    if random.random() > 0.7 and allow_nest:
        s = "(" + genExpr(step = 2, allow_nest=False) + ")"
        if random.random() > 0.5:
            s += "^" + genNumber(low=0, high=6)
        return s
    if random.random() > 0.6:
        return genPower()
    return genNumber()


def genTerm(step=random.randint(1, 4), allow_nest=True):
    negate = random.random() > 0.4
    if negate:
        s = "-"
    elif random.random() > 0.6:
        s = "+"
    else:
        s = ""
    
    s += "*".join([genFractor(allow_nest=allow_nest) for _ in range(step)])

    return s


def genExpr(step=random.randint(1, 4), allow_nest=True):
    negate = random.random() > 0.4
    if negate:
        s = "-"
    elif random.random() > 0.6:
        s = "+"
    else:
        s = ""
    
    s += "#".join([genTerm(allow_nest=allow_nest) for _ in range(step)])
    while "#" in s:
        s = s.replace("#", "+" if random.random() > 0.5 else "-", 1)

    s_ = ""
    for c in s:
        if c in "+-()x^" and random.random() > 0.9:
            s_ += " \t"[random.random() > 0.3]
        s_ += c

    return s_


if __name__ == "__main__":
    test_n = int(input())
    fp = pathlib.Path("storage").open("a")
    #system("clear")
    for i in range(test_n):
        s = genExpr()
        while (len(s) > 200):
            s = genExpr()
        print(title := f"===== #{i+1} / {test_n} =====")
        print("\033[36m" + s + "\033[0m")
        pathlib.Path("input").write_text(s)
        fp.write(f"#{i} `{s}`\n")
        subprocess.Popen(
            args=["java", "MainClass", "-cp", "."],
            stdin=pathlib.Path("input").open("r"),
            stdout=pathlib.Path("output").open("w"),
            cwd="build"
        ).wait()
        ret, msg = checkMain(fin=pathlib.Path("input").open("r"), fout=pathlib.Path("output").open("r"))
        if ret:
            print(f"\033[32;7mAccepted!\033[0m {msg}")
        else:
            print(f"\033[31;7mFailed!\033[0m {msg}")
            input()
        # print(len(title) * "=")
        if (i % 5 == 4):
            sys.stdout.flush()
            input()
            #system("clear")
    fp.close()
