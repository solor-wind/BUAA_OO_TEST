import random
import numpy as np
import json
from cyaron import Graph
from pathlib import Path

config = json.load(open('config.json',encoding='utf-8'))

def generate_data(input_file:str)->None:
    """
    传入文件路径，将生成的数据写入文件
    相关参数在config.json中配置
    """
    command_num=random.randint(4,int(config['command_limit']))
    node_num1 = random.randint(2, int(config['node_limit']))#所有节点数
    node_num2=node_num1#稠密图节点数
    edge_num=int(0)
    if node_num1*(node_num1-1)/2<command_num/4:
        node_num2=node_num1
        edge_num=random.randint(max(1,int(node_num2*(node_num2-1)/6)),int(node_num2*(node_num2-1)/2))
    else:
        edge_num=int(command_num/4)
        node_num2=random.randint(int((edge_num*2)**0.5),node_num1)
    graph=Graph.graph(node_num2,edge_num,weight_limit=(1,200))
    node=set()
    str_node=[]
    str_edge=[]
    str_mr=[]
    ans=[]

    for edge in graph.iterate_edges():
        node.add(edge.start)
        str_edge.append('ar '+str(edge.start)+' '+str(edge.end)+' '+str(edge.weight)) 
        if random.random()<0.4:
            str_mr.append('mr '+str(edge.start)+' '+str(edge.end)+' '+str(random.randint(-200,100)))
        else:
            str_edge.append('ar ' + str(random.randint(1,node_num1)) + ' ' + str(random.randint(1,node_num1)) + ' ' + str(random.randint(1, 200)))
    #遍历集合node
    for i in node:
        str_node.append('ap '+str(i)+' OO'+str(i)+' '+str(random.randint(1,100)))
    ans.extend(str_node)
    ans.extend(str_edge)
    ans.extend(str_mr)
    #打乱顺序
    random.shuffle(ans)
    str_edge.extend(str_mr)
    random.shuffle(str_edge)
    ans.extend(str_edge)
    for i in range(node_num2,node_num1+1):
        ans.insert(random.randint(0,ans.__len__()-1),'ap '+str(i)+' OO'+str(i)+' '+str(random.randint(1,100)))

    command_num-=ans.__len__()


    while command_num>0:
        prob=random.random()
        if prob<0.2:
            if random.random()<0.5:
                #从node中随机选取一个元素
                tmp=np.random.choice(list(node),2)
                ans.insert(random.randint(0,ans.__len__()-1),'qv '+str(tmp[0])+' '+str(tmp[1]))
            else:
                ans.insert(random.randint(0,ans.__len__()-1),'qv '+str(random.randint(-0x80000000,0x7fffffff))+' '+str(random.randint(-0x80000000,0x7fffffff)))
        elif prob<0.4:
            if random.random()<0.5:
                tmp=np.random.choice(list(node),2)
                ans.insert(random.randint(0,ans.__len__()-1),'qci '+str(tmp[0])+' '+str(tmp[1]))
            else:
                ans.insert(random.randint(0,ans.__len__()-1),'qci '+str(random.randint(-0x80000000,0x7fffffff))+' '+str(random.randint(-0x80000000,0x7fffffff)))
        elif prob<0.7:
            ans.insert(random.randint(0,ans.__len__()-1),'qbs')
        else:
            ans.insert(random.randint(0,ans.__len__()-1),'qts')
        command_num-=1

    if random.random()<config['load_prob']:
        node_num3=node_num1
        if node_num1>300:
            node_num3=random.randint(1,300)
        edge_num3=random.randint(int(node_num3*(node_num3-1)/10),int(node_num3*(node_num3-1)/2))
        graph=Graph.graph(node_num1,edge_num3,weight_limit=(1,200))
        ans2=[]
        ans2.append('ln '+str(node_num3))
        for i in range(3):
            tmp_node=''
            for j in range(1,node_num3+1):
                tmp_node+=str(j)+' '
            ans2.append(tmp_node)
        for i in range(2,node_num3+1):
            tmp_edge=''
            for j in range(1,i):
                if random.random()<float(edge_num3)/(node_num3*(node_num3-1)/2):
                    tmp_edge+=str(random.randint(1,200))+' '
                else:
                    tmp_edge+='0 '
                # if graph.edges[j].count(i)>0:
                #     tmp_edge+=str(graph.edges[j][i].weight)+' '
                # else:
                #     tmp_edge+='0 '
            ans2.append(tmp_edge)
        ans2.extend(ans)
        ans=ans2
        command_num-=1

    with open(input_file,'w') as f:
        path = Path(input_file)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        for i in ans:
            f.write(i + "\n")

if __name__ == "__main__":
    generate_data('input.txt')