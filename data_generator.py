import random
import numpy as np
import json
from cyaron import Graph
from pathlib import Path

config = json.load(open('config.json', encoding='utf-8'))


def generate_data(input_file: str) -> None:
    """
    传入文件路径，将生成的数据写入文件
    相关参数在config.json中配置
    """
    command_num = random.randint(4, int(config['command_limit']))
    node_num = random.randint(2, int(config['node_limit']))  # 所有节点数
    isload = random.random()
    if isload < config['load_prob']:
        command_num -= 1
    graph_command_num = int(command_num * config['graph_prop'])
    tag_command_num = int(command_num * config['tag_prop'])
    message_command_num = int(command_num * config['message_prop'])
    query_command_num = command_num - graph_command_num - tag_command_num

    # 先建立图(1/4)
    # 一半的指令用于生产稠密图，另一半用于加剩下的节点、修改节点、随机加边
    dense_node_num = int((1 + (1 + 4 * graph_command_num) ** 0.5) / 2)  # 稠密图节点数
    edge_num = dense_node_num * (dense_node_num - 1) / 2
    dense_node_num += 1
    graph = Graph.graph(dense_node_num, edge_num, weight_limit=(1, 200))

    # 先建立稠密图
    node = set()
    edge = set()
    str_node = []
    str_edge = []
    ans = []
    for tmpedge in graph.iterate_edges():
        node.add(tmpedge.start)
        str_edge.append('ar ' + str(tmpedge.start) + ' ' + str(tmpedge.end) + ' ' + str(tmpedge.weight))
        edge.add((tmpedge.start, tmpedge.end))
    for i in node:
        str_node.append('ap ' + str(i) + ' OO' + str(i) + ' ' + str(random.randint(1, 200)))
    for i in range(dense_node_num, node_num):  # 外围的稀疏点
        tmpnode = get_int()
        str_node.append('ap ' + str(tmpnode) + ' OO' + str(i) + ' ' + str(random.randint(1, 200)))
        node.add(tmpnode)
    ans.extend(str_node)
    ans.extend(str_edge)

    # 随机插点、插边、改边
    node = list(node)
    edge = list(edge)
    graph_command_num -= ans.__len__()
    while graph_command_num > 0:
        prob = random.random()
        tmpstr = ''
        if prob < 0.2:  # 加点
            if random.random() < 0.5:  # 加入已有的点
                tmpstr = 'ap ' + str(np.random.choice(node)) + ' OO_plus' + ' ' + str(random.randint(1, 200))
            else:
                node.append(get_int())
                tmpstr = 'ap ' + str(node[-1]) + ' OO_random' + ' ' + str(random.randint(1, 200))
        elif prob < 0.7:  # 加边
            if random.random() < 0.8:  # 已有的点之间
                edge.append((np.random.choice(node), np.random.choice(node)))
                tmpstr = 'ar ' + str(edge[-1][0]) + ' ' + str(edge[-1][1]) + ' ' + str(
                    random.randint(1, 200))
            else:
                tmpstr = 'ar ' + str(get_int()) + ' ' + str(get_int()) + ' ' + str(random.randint(1, 200))
        else:  # 改边
            if random.random() < 0.8:  # 已有的边
                tmppos = random.randint(0, edge.__len__() - 1)
                tmpstr = 'mr ' + str(edge[tmppos][0]) + ' ' + str(edge[tmppos][1]) + ' ' + str(
                    random.randint(-200, 100))
            else:
                tmpstr = 'mr ' + str(get_int()) + ' ' + str(get_int()) + ' ' + str(random.randint(-200, 100))
        ans.insert(random.randint(0, ans.__len__() - 1), tmpstr)
        graph_command_num -= 1

    # 再插入tag(2/4)
    tag = []
    str_at = []
    str_att = []
    # 一半的指令用于建立稠密的子图
    dense_tag_num = tag_command_num / 2
    tag_command_num -= dense_tag_num
    while True:
        tag_id = random.randint(1, graph.edges.__len__() - 1)
        str_at.append('at ' + str(tag_id) + ' ' + str(tag_id))
        dense_tag_num -= 1
        tag.append(tag_id)
        for i in range(0, graph.edges[tag_id].__len__() - 1):
            for j in range(0, tag.__len__() - 1):
                str_att.append('att ' + str(graph.edges[tag_id][0]) + ' ' + str(tag[j]) + ' ' + str(tag_id))
                dense_tag_num -= 1
                if dense_tag_num <= 0:
                    break
            if dense_tag_num <= 0:
                break
        if dense_tag_num <= 0:
            break
    ans.extend(str_at)
    ans.extend(str_att)

    # 另一半用于随机添加和删除tag
    while tag_command_num > 0:
        prob = random.random()
        if prob < 0.3:  # 随机at
            if random.random() < 0.8:  # 向已有节点加入tag
                tmp_tag = np.random.choice(node)
                ans.insert(random.randint(0, ans.__len__() - 1), 'at ' + str(tmp_tag) + ' ' + str(tmp_tag))
                tag.append(tmp_tag)
            else:
                ans.insert(random.randint(0, ans.__len__() - 1), 'at ' + str(get_int()) + ' ' + str(get_int()))
        elif prob < 0.7:  # 随机att
            if random.random() < 0.8:  # 向已有tag加人
                tmp_tag = np.random.choice(tag)
                ans.insert(random.randint(0, ans.__len__() - 1),
                           'att ' + str(np.random.choice(node)) + ' ' + str(tmp_tag) + ' ' + str(tmp_tag))
            else:
                ans.insert(random.randint(0, ans.__len__() - 1),
                           'att ' + str(get_int()) + ' ' + str(get_int()) + ' ' + str(get_int()))
        elif prob < 0.8:  # 随机dt
            if random.random() < 0.5:  # 删除已有tag
                tmp_tag = np.random.choice(tag)
                ans.insert(random.randint(0, ans.__len__() - 1), 'dt ' + str(tmp_tag) + ' ' + str(tmp_tag))
            else:
                ans.insert(random.randint(0, ans.__len__() - 1), 'dt ' + str(get_int()) + ' ' + str(get_int()))
        else:  # 随机dft
            if random.random() < 0.5:  # 删除已有tag
                tmp_tag = np.random.choice(tag)
                ans.insert(random.randint(0, ans.__len__() - 1),
                           'dft ' + str(np.random.choice(node)) + ' ' + str(tmp_tag) + ' ' + str(tmp_tag))
            else:
                ans.insert(random.randint(0, ans.__len__() - 1),
                           'dft ' + str(get_int()) + ' ' + str(get_int()) + ' ' + str(get_int()))
        tag_command_num -= 1

    # 然后插入message(3/4)
    # sei;am,arem,anm,aem;sm;cn,dce
    message = set()
    str_am = []
    red = set()
    emoji = []
    # 先加足够的消息
    am_command_num = message_command_num * 2 / 3
    message_command_num -= am_command_num
    while am_command_num > 0:
        prob = random.random()
        id = get_int()
        tag_id = random.choice(tag)
        edge_id = random.randint(0, edge.__len__() - 1)
        while id in message:
            id = get_int()
        message.add(id)
        if emoji.__len__() == 0 or prob < 0.2:
            emoji_id = 0
            if emoji.__len__() == 0 or random.random() < 0.8:
                emoji_id = random.randint(-1000, 1000)
            else:
                emoji_id = random.choice(emoji)
            emoji.append(emoji_id)
            str_am.append('sei ' + str(emoji_id))
            if random.random() < 0.5:
                str_am.append('aem ' + str(id) + ' ' + str(emoji_id) + ' 0 ' + str(edge[edge_id][0]) + ' ' + str(
                    edge[edge_id][1]))
            else:
                str_am.append('aem ' + str(id) + ' ' + str(emoji_id) + ' 1 ' + str(tag_id) + ' ' + str(tag_id))
            am_command_num -= 1
        elif prob < 0.4:  # am
            if random.random() < 0.5:
                str_am.append('am ' + str(id) + ' ' + str(random.randint(-1000, 1000)) + ' 0 ' + str(
                    edge[edge_id][0]) + ' ' + str(edge[edge_id][1]))
            else:
                str_am.append(
                    'am ' + str(id) + ' ' + str(random.randint(-1000, 1000)) + ' 1 ' + str(tag_id) + ' ' + str(tag_id))
        elif prob < 0.6:  # arem
            if random.random() < 0.5:
                str_am.append(
                    'arem ' + str(id) + ' ' + str(random.randint(0, 200)) + ' 0 ' + str(edge[edge_id][0]) + ' ' + str(
                        edge[edge_id][1]))
                red.add(edge[edge_id][0])
                red.add(edge[edge_id][1])
            else:
                str_am.append(
                    'arem ' + str(id) + ' ' + str(random.randint(0, 200)) + ' 1 ' + str(tag_id) + ' ' + str(tag_id))
                red.add(tag_id)
                if tag_id < graph.edges.__len__() and tag_id >= 0:
                    for j in range(graph.edges[tag_id].__len__()):
                        if j >= 10:
                            break
                        red.add(graph.edges[tag_id][j].end)
        elif prob < 0.8:  # anm
            if random.random() < 0.5:
                str_am.append(
                    'anm ' + str(id) + ' wtfOO' + str(id) + ' 0 ' + str(edge[edge_id][0]) + ' ' + str(edge[edge_id][1]))
            else:
                str_am.append('anm ' + str(id) + ' wtfOO' + str(id) + ' 1 ' + str(tag_id) + ' ' + str(tag_id))
        am_command_num -= 1

    # 再发送、清除消息，随机添加消息
    message = list(message)
    red = list(red)
    while message_command_num > 0:
        prob = random.random()
        if prob < 0.5:
            str_am.insert(random.randint(int(str_am.__len__() / 2), str_am.__len__() - 1),
                          'sm ' + str(random.choice(message)))
        elif prob < 0.6:
            str_am.insert(random.randint(int(str_am.__len__() / 2), str_am.__len__() - 1),
                          'cn ' + str(random.choice(node)))
        elif prob < 0.8:
            str_am.insert(random.randint(int(str_am.__len__() / 2), str_am.__len__() - 1),
                          'dce ' + str(random.randint(1, 30)))
        elif prob < 0.95:
            if random.random() < 0.5:
                str_am.append('am ' + str(get_int()) + ' ' + str(random.randint(-1000, 1000)) + ' 0 ' + str(
                    get_int()) + ' ' + str(get_int()))
            else:
                str_am.append('am ' + str(get_int()) + ' ' + str(random.randint(-1000, 1000)) + ' 1 ' + str(
                    get_int()) + ' ' + str(get_int()))
        else:
            if random.random() < 0.5:
                str_am.append(
                    'aem ' + str(get_int()) + ' ' + str(random.randint(-1000, 1000)) + ' 0 ' + str(
                        get_int()) + ' ' + str(get_int()))
            else:
                str_am.append(
                    'aem ' + str(get_int()) + ' ' + str(random.randint(-1000, 1000)) + ' 1 ' + str(
                        get_int()) + ' ' + str(get_int()))
        message_command_num -= 1
    ans.extend(str_am)

    # 接着插入查询(4/4)
    if emoji.__len__() == 0:
        emoji.append(1)
    while query_command_num > 0:
        prob = random.random()
        if prob < 0.05:  # qv
            if random.random() < 0.5:
                # 从node中随机选取一个元素
                tmp = np.random.choice(list(node), 2)
                ans.insert(random.randint(0, ans.__len__() - 1), 'qv ' + str(tmp[0]) + ' ' + str(tmp[1]))
            else:
                ans.insert(random.randint(0, ans.__len__() - 1), 'qv ' + str(get_int()) + ' ' + str(get_int()))
        elif prob < 0.1:  # qci
            if random.random() < 0.5:
                tmp = np.random.choice(list(node), 2)
                ans.insert(random.randint(0, ans.__len__() - 1), 'qci ' + str(tmp[0]) + ' ' + str(tmp[1]))
            else:
                ans.insert(random.randint(0, ans.__len__() - 1), 'qci ' + str(get_int()) + ' ' + str(get_int()))
        elif prob < 0.15:  # qbs
            ans.insert(random.randint(0, ans.__len__() - 1), 'qbs')
        elif prob < 0.25:  # qts
            ans.insert(random.randint(0, ans.__len__() - 1), 'qts')
        elif prob < 0.3:  # qba
            if random.random() < 0.8:
                ans.insert(random.randint(0, ans.__len__() - 1), 'qba ' + str(np.random.choice(node)))
            else:
                ans.insert(random.randint(0, ans.__len__() - 1), 'qba ' + str(get_int()))
        elif prob < 0.35:  # qcs
            ans.insert(random.randint(0, ans.__len__() - 1), 'qcs')
        elif prob < 0.45:  # qsp
            if random.random() < 0.8:
                ans.insert(random.randint(0, ans.__len__() - 1),
                           'qsp ' + str(np.random.choice(node)) + ' ' + str(np.random.choice(node)))
            else:
                ans.insert(random.randint(0, ans.__len__() - 1), 'qsp ' + str(get_int()) + ' ' + str(get_int()))
        elif prob < 0.55:  # qtvs
            if random.random() < 0.8:
                ans.insert(random.randint(0, ans.__len__() - 1),
                           'qtvs ' + str(np.random.choice(tag)) + ' ' + str(np.random.choice(tag)))
            else:
                ans.insert(random.randint(0, ans.__len__() - 1), 'qtvs ' + str(get_int()) + ' ' + str(get_int()))
        elif prob < 0.6:  # qtav
            if random.random() < 0.8:
                ans.insert(random.randint(0, ans.__len__() - 1),
                           'qtav ' + str(np.random.choice(tag)) + ' ' + str(np.random.choice(tag)))
            else:
                ans.insert(random.randint(0, ans.__len__() - 1), 'qtav ' + str(get_int()) + ' ' + str(get_int()))
        elif prob < 0.7:  # qsv
            if random.random() < 0.8:
                ans.insert(random.randint(int(ans.__len__() / 2), ans.__len__() - 1),
                           'qsv ' + str(np.random.choice(node)))
            else:
                ans.insert(random.randint(int(ans.__len__() / 2), ans.__len__() - 1), 'qsv ' + str(get_int()))
        elif prob < 0.8:  # qrm
            if random.random() < 0.8:
                ans.insert(random.randint(int(ans.__len__() / 2), ans.__len__() - 1),
                           'qrm ' + str(np.random.choice(node)))
            else:
                ans.insert(random.randint(int(ans.__len__() / 2), ans.__len__() - 1), 'qrm ' + str(get_int()))
        elif prob < 0.9:  # qp
            if random.random() < 0.8:
                ans.insert(random.randint(int(ans.__len__() / 2), ans.__len__() - 1),
                           'qp ' + str(np.random.choice(emoji)))
            else:
                ans.insert(random.randint(int(ans.__len__() / 2), ans.__len__() - 1), 'qp ' + str(get_int()))
        else:  # qm
            if red.__len__() > 0 and random.random() < 0.8:
                ans.insert(random.randint(int(ans.__len__() / 2), ans.__len__() - 1),
                           'qm ' + str(np.random.choice(red)))
            else:
                ans.insert(random.randint(int(ans.__len__() / 2), ans.__len__() - 1), 'qm ' + str(get_int()))
        query_command_num -= 1

    # 最后生成load_network(3.5/3)
    if isload < config['load_prob']:
        load_node_num = random.randint(1, min(100, node_num, node.__len__()))
        load_edge_num = random.randint(int(load_node_num * (load_node_num - 1) / 20),
                                       int(load_node_num * (load_node_num - 1) / 2))

        ans2 = []
        ans2.append('ln ' + str(load_node_num))
        load_node = random.sample(node, load_node_num)

        str_load_node = ''
        for i in range(0, load_node_num):
            str_load_node += str(load_node[i]) + ' '
        ans2.append(str_load_node)

        str_load_node = ''
        for i in range(0, load_node_num):
            str_load_node += 'OO_load_' + str(load_node[i]) + ' '
        ans2.append(str_load_node)

        str_load_node = ''
        for i in range(0, load_node_num):
            str_load_node += str(random.randint(1, 200)) + ' '
        ans2.append(str_load_node)

        for i in range(2, load_node_num + 1):
            str_load_edge = ''
            for j in range(1, i):
                if random.random() < float(load_edge_num) / (load_node_num * (load_node_num - 1) / 2):
                    str_load_edge += str(random.randint(1, 200)) + ' '
                else:
                    str_load_edge += '0 '
            ans2.append(str_load_edge)
        ans2.extend(ans)
        ans = ans2

    with open(input_file, 'w') as f:
        path = Path(input_file)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        for i in ans:
            f.write(i + "\n")


def get_int():
    return random.randint(-0x80000000, 0x7ffffff)


if __name__ == "__main__":
    generate_data('input.txt')
