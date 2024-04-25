import networkx as nx
from checker import Checker
import plotly.graph_objects as go


def draw_graph(input_index = 0):
    """
    截至至input_index的图形,绘制input.txt对应的图形（如果不指定行数，则绘制整个input.txt） /
    请确保input_index之前你的output.txt为正确
    :param input_index:
    :return:
    """
    checker = Checker("input.txt")
    if input_index == 0:
        input_index = len(checker.inputs)
    graph = checker.generate_graph(input_index)
    # 设置节点位置
    pos = nx.spring_layout(graph)
    # 创建节点的坐标列表和标签列表
    node_x = []
    node_y = []
    node_labels = []
    for node in graph.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_labels.append(str(node))  # 将节点的编号作为标签
    # 创建边的坐标列表
    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    # 创建绘图对象
    fig = go.Figure()
    # 绘制节点
    fig.add_trace(
        go.Scatter(x=node_x, y=node_y, mode='markers', marker=dict(size=10, color='LightSkyBlue'), hoverinfo='text',
                   text=node_labels))
    # 绘制边
    fig.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(color='LightGrey', width=1), hoverinfo='none'))
    # 设置图形布局
    fig.update_layout(title_text='Interactive Graph', showlegend=False, hovermode='closest',
                      margin=dict(b=20, l=5, r=5, t=40))
    # 显示图形
    fig.show()

if __name__ == '__main__':
    draw_graph(0)
