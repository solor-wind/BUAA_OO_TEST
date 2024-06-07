import os
import subprocess

subprocess.run(["javac","-d","C:\\Users\\gpf\\projects\\java_learner\\bin","-cp","C:\\Users\\gpf\\projects\\java_learner\\hw1","C:\\Users\\gpf\\projects\\java_learner\\hw1\\MainClass.java"])

#读入文件
flag=0
line=1
with open('C:\\Users\\gpf\\Desktop\\oo.in', 'r') as in1:
    with open('C:\\Users\\gpf\\Desktop\\oo.out', 'r') as in2:
        line1 = in1.readline()
        line2 = in2.readline()
        while line1 and line2:
            ans1=subprocess.run(["java","-cp","C:\\Users\\gpf\\projects\\java_learner\\bin","MainClass"], input=line1, encoding="utf8", stdout=subprocess.PIPE)
            ans2=subprocess.run(["java","-cp","C:\\Users\\gpf\\projects\\java_learner\\bin","MainClass"], input=line2, encoding="utf8", stdout=subprocess.PIPE)
            if ans1.stdout!=ans2.stdout:
                print("wrong in line"+line)
                flag=1
                break
            line2 = in2.readline()
            line1 = in1.readline()
            line=line+1
if flag==0:
    print("all right")
'''

with open('C:\\Users\\gpf\\Desktop\\oo.in', 'r') as in1:
    with open('C:\\Users\\gpf\\Desktop\\oo.out', 'w') as in2:
        line1 = in1.readline()
        while line1:
            ans1=subprocess.run(["java","-cp","C:\\Users\\gpf\\projects\\java_learner\\bin","MainClass"], input=line1, encoding="utf8", stdout=subprocess.PIPE)
            in2.write(ans1.stdout)
            line1 = in1.readline()'''
