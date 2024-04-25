import random
import numpy as np
import json
from cyaron import Graph

config = json.load(open('config.json'))

def generate_data(input_file:str)->None:
    """
    传入文件路径，将生成的数据写入文件
    相关参数在config.json中配置
    """
    node_num=edge_num=command_num=random.randint(1,int(config['command_limit']))
    while node_num+edge_num>=command_num/3*2 and node_num+edge_num<=command_num/3:
        node_num=random.randint(1,int(config['node_limit']))
        edge_num=random.randint(node_num-1,node_num*(node_num-1)/2)
    graph=Graph.graph(node_num,edge_num,weight_limit=(1,200))
    node=set()
    str_node=[]
    str_edge=[]
    str_mr=[]
    ans=[]

    for edge in graph.iterate_edges():
        node.add(edge.start)
        str_edge.append('ar '+str(edge.start)+' '+str(edge.end)+' '+str(edge.weight)) 
        if random.random()<0.5:
            str_mr.append('mr '+str(edge.start)+' '+str(edge.end)+' '+str(random.randint(-200,200)))   
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

    with open(input_file,'w') as f:
        for i in ans:
            f.write(i+'\n')

if __name__ == "__main__":
    generate_data('input.txt')