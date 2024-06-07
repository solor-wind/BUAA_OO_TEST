import random
import os

limit=10    #限制生成的基本单元数

def generate_unit(floor):
    global limit
    
    string=''
    exp=0
    para=0
    if random.random() >0.8 and floor >0:
        tmp=limit
        string=string+'('
        string=string+generate_expr(floor-1)
        string=string+')^'
        exp=random.randint(0, 8)
        if random.random() > 0.5:
            string=string+'+'
        string=string+str(exp)
        tmp=tmp-limit
        limit=limit-tmp*abs(exp-1)
        return string
    
    exp=random.randint(0, 8)
    if random.random() > 0.1:   #系数产0概率
        if random.random() > 0.95:
            para=random.randint(-999999999, 999999999)
        else :
            para=random.randint(-20, 20)
    else:
        para=random.randint(-1,1)
    if random.random() > 0.5:
        if(para>0):
            string=string+'+'
    string=string+str(para)+'*x^'    #缺点，产生的项必定含有'*x^'
    if random.random() > 0.5:
        string=string+'+'
    string=string+str(exp)
    limit=limit-1
    return string

def generate_term(floor):
    global limit
    string=''
    if random.random() > 0.5:
        if random.random() > 0.5:
            string=string+'+'
        else:
            string=string+'-'
    uplimit=random.randint(1,5)
    for i in range(0,uplimit):
        string=string+generate_unit(floor)
        if limit<0 :
            break
        if i!=uplimit-1:
            string=string+'*'
    return string

def generate_expr(floor):
    global limit
    string=''
    if random.random() > 0.5:
        if random.random() > 0.5:
            string=string+'+'
        else:
            string=string+'-'
    uplimit=random.randint(1,10)
    for i in range(0,uplimit):
        string=string+generate_term(floor)
        if limit<0 :
            break
        if i!=uplimit-1:
            if random.random() > 0.5:
                string=string+'+'
            else:
                string=string+'-'
    return string

if __name__ == "__main__":
    num=int(input("请输入生成的测试用例数："))
    Limit=int(input("请输入生成的基本单元数上限："))
    floor=int(input("请输入括号嵌套层数上限："))
    for i in range(0,num):
        limit=random.randint(0,Limit)
        tmp=generate_expr(floor)
        ans=''
        for j in range(0,tmp.__len__()):
            if (tmp[j]>'9' or tmp[j]<'0') and random.random()<0.3:  #生成空白符概率
                if random.random()<0.1: #生成制表符概率
                    ans=ans+'\t'
                else:
                    ans=ans+' '
            ans=ans+tmp[j]
        print(ans)
    os.system("pause")