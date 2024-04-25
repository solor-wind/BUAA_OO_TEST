import networkx as nx
from loader import file_load
from person import Person


class Checker:
    def __init__(self, in_path, out_path=None):
        """
        初始化Checker类
        :param in_path: 输入文件路径
        :param out_path: 输出文件路径
        """
        self.inputs = file_load(in_path)
        if out_path is not None:
            self.outputs = file_load(out_path)
        self.exception = {"pinf": 0, "epi": 0, "rnf": 0, "er": 0}
        self.id2Person = {}
        self.pinfId2Num = {}
        self.epiId2Num = {}
        self.rnfId2Num = {}
        self.erId2Num = {}
        self.graph = nx.Graph()

    def check(self, check_output=True) -> str:
        """
        检查输入输出文件是否符合要求
        :param check_output: 是否检查输出文件
        :return: 描述检查结果的字符串
        """
        input_index = 0
        output_index = 0
        while input_index < len(self.inputs):
            order = self.inputs[input_index].split()
            if order[0] != 'load_network' and order[0] != 'ln':
                if check_output and output_index == len(self.outputs):
                    return f"输出文件行数过少，输入第{input_index + 1}行，输出第{output_index}行后缺失"
                if order[0] == 'add_person' or order[0] == 'ap':
                    check_func = self.check_add_person
                elif order[0] == 'add_relation' or order[0] == 'ar':
                    check_func = self.check_add_relation
                elif order[0] == 'modify_relation' or order[0] == 'mr':
                    check_func = self.check_modify_relation
                elif order[0] == 'query_value' or order[0] == 'qv':
                    check_func = self.check_query_value
                elif order[0] == 'query_circle' or order[0] == 'qci':
                    check_func = self.check_query_circle
                elif order[0] == 'query_block_sum' or order[0] == 'qbs':
                    check_func = self.check_query_block_sum
                elif order[0] == 'query_triple_sum' or order[0] == 'qts':
                    check_func = self.check_query_triple_sum
                elif order[0] == 'load_network' or order[0] == 'ln':
                    check_func = self.check_load_network
                else:
                    return f"第{input_index + 1}行输入格式错误"
                ans = check_func(order)
                if check_output and self.outputs[output_index].strip() != ans:
                    return f"输入第{input_index + 1}行\t输出第{output_index + 1}行错误\t正确结果应为{ans}"
                input_index += 1
            else:
                if order[0] == 'load_network' or order[0] == 'ln':
                    ans = self.check_load_network(order, self.inputs, input_index)
                    if check_output and self.outputs[output_index].strip() != ans:
                        return f"输入第{input_index + 1}行\t输出第{output_index + 1}行错误\t正确结果应为{ans}"
                    input_index += 3 + int(order[1])
            if check_output:
                output_index += 1
        if check_output and output_index != len(self.outputs):
            return f"输出文件行数过多，应为{output_index}行"
        if check_output:
            return "Accepted!"

    def check_add_person(self, order) -> str:
        id = int(order[1])
        if id in self.id2Person.keys():
            self.exception["epi"] += 1
            if id in self.epiId2Num.keys():
                self.epiId2Num[id] += 1
            else:
                self.epiId2Num[id] = 1
            return f"epi-{self.exception['epi']}, {order[1]}-{self.epiId2Num[id]}"
        else:
            self.graph.add_node(id)
            self.id2Person[id] = Person(int(order[1]), order[2], int(order[3]))
            return "Ok"

    def check_add_relation(self, order) -> str:
        id1 = int(order[1])
        id2 = int(order[2])
        if id1 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        elif id2 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id2 in self.pinfId2Num.keys():
                self.pinfId2Num[id2] += 1
            else:
                self.pinfId2Num[id2] = 1
            return f"pinf-{self.exception['pinf']}, {id2}-{self.pinfId2Num[id2]}"
        elif self.graph.has_edge(id1, id2) or id1 == id2:
            id1 = min(int(order[1]), int(order[2]))
            id2 = max(int(order[1]), int(order[2]))
            self.exception["er"] += 1
            if id1 in self.erId2Num.keys():
                self.erId2Num[id1] += 1
            else:
                self.erId2Num[id1] = 1
            if id1 != id2:
                if id2 in self.erId2Num.keys():
                    self.erId2Num[id2] += 1
                else:
                    self.erId2Num[id2] = 1
            return f"er-{self.exception['er']}, {id1}-{self.erId2Num[id1]}, {id2}-{self.erId2Num[id2]}"
        else:
            self.graph.add_edge(id1, id2, weight=int(order[3]))
            return "Ok"

    def check_modify_relation(self, order) -> str:
        id1 = int(order[1])
        id2 = int(order[2])
        if id1 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        elif id2 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id2 in self.pinfId2Num.keys():
                self.pinfId2Num[id2] += 1
            else:
                self.pinfId2Num[id2] = 1
            return f"pinf-{self.exception['pinf']}, {id2}-{self.pinfId2Num[id2]}"
        elif id1 == id2:
            self.exception["epi"] += 1
            if id1 in self.epiId2Num.keys():
                self.epiId2Num[id1] += 1
            else:
                self.epiId2Num[id1] = 1
            return f"epi-{self.exception['epi']}, {id1}-{self.epiId2Num[id1]}"
        elif not self.graph.has_edge(id1, id2):
            id1 = min(int(order[1]), int(order[2]))
            id2 = max(int(order[1]), int(order[2]))
            self.exception["rnf"] += 1
            if id1 in self.rnfId2Num.keys():
                self.rnfId2Num[id1] += 1
            else:
                self.rnfId2Num[id1] = 1
            if id2 in self.rnfId2Num.keys():
                self.rnfId2Num[id2] += 1
            else:
                self.rnfId2Num[id2] = 1
            return f"rnf-{self.exception['rnf']}, {id1}-{self.rnfId2Num[id1]}, {id2}-{self.rnfId2Num[id2]}"
        else:
            if self.graph[id1][id2]['weight'] + int(order[3]) <= 0:
                self.graph.remove_edge(id1, id2)
            else:
                self.graph[id1][id2]['weight'] += int(order[3])
            return "Ok"

    def check_query_value(self, order) -> str:
        id1 = int(order[1])
        id2 = int(order[2])
        if id1 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        elif id2 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id2 in self.pinfId2Num.keys():
                self.pinfId2Num[id2] += 1
            else:
                self.pinfId2Num[id2] = 1
            return f"pinf-{self.exception['pinf']}, {id2}-{self.pinfId2Num[id2]}"
        elif not self.graph.has_edge(id1, id2) and id1 != id2:
            id1 = min(int(order[1]), int(order[2]))
            id2 = max(int(order[1]), int(order[2]))
            self.exception["rnf"] += 1
            if id1 in self.rnfId2Num.keys():
                self.rnfId2Num[id1] += 1
            else:
                self.rnfId2Num[id1] = 1
            if id2 in self.rnfId2Num.keys():
                self.rnfId2Num[id2] += 1
            else:
                self.rnfId2Num[id2] = 1
            return f"rnf-{self.exception['rnf']}, {id1}-{self.rnfId2Num[id1]}, {id2}-{self.rnfId2Num[id2]}"
        elif id1 == id2:
            return "0"
        else:
            return str(self.graph[id1][id2]['weight'])

    def check_query_circle(self, order) -> str:
        id1 = int(order[1])
        id2 = int(order[2])
        if id1 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        elif id2 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id2 in self.pinfId2Num.keys():
                self.pinfId2Num[id2] += 1
            else:
                self.pinfId2Num[id2] = 1
            return f"pinf-{self.exception['pinf']}, {id2}-{self.pinfId2Num[id2]}"
        else:
            if nx.has_path(self.graph, id1, id2):
                return "true"
            else:
                return "false"

    def check_query_block_sum(self, order) -> str:
        return str(nx.number_connected_components(self.graph))

    def check_query_triple_sum(self, order) -> str:
        cliques = nx.enumerate_all_cliques(self.graph)
        count = 0
        for clique in cliques:
            if len(clique) == 3:
                count += 1
        return str(count)

    def check_load_network(self, order, inputs, input_index) -> str:
        num = int(order[1])
        id_list = inputs[input_index + 1].split()
        name_list = inputs[input_index + 2].split()
        age_list = inputs[input_index + 3].split()
        for i in range(num):
            self.id2Person[int(id_list[i])] = Person(int(id_list[i]), name_list[i], int(age_list[i]))
            self.graph.add_node(int(id_list[i]))
        for i in range(0, num):
            weights = inputs[input_index + 3 + i].split()
            id1 = int(id_list[i])
            for j in range(0, i):
                id2 = int(id_list[j])
                if weights[j] != '0':
                    self.graph.add_edge(id1, id2, weight=int(weights[j]))
        return "Ok"

    def generate_graph(self, input_index) -> nx.Graph:
        """
        生成图，需要保证1~input_index行不出现指令格式错误
        :param input_index: 截至到input_index行，生成图
        :return: 生成的图
        """
        self.inputs = self.inputs[:input_index]
        self.check(False)
        return self.graph


if __name__ == '__main__':
    print(Checker('input.txt', 'output.txt').check())
