import networkx as nx
from loader import file_load
from person import Person
from tag import Tag
from message import Message


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
        self.exception = {"pinf": 0, "epi": 0, "rnf": 0, "er": 0, "anf": 0, "eti": 0, "pnf": 0, "tinf": 0,
                          "einf": 0, "eei": 0, "emi": 0, "minf": 0}
        self.id2Person = {}
        self.pinfId2Num = {}
        self.epiId2Num = {}
        self.rnfId2Num = {}
        self.erId2Num = {}
        self.anfId2Num = {}
        self.etiId2Num = {}
        self.pnfId2Num = {}
        self.tinfId2Num = {}
        self.einfId2Num = {}
        self.eeiId2Num = {}
        self.emiId2Num = {}
        self.minfId2Num = {}
        self.graph = nx.Graph()
        self.id2Message = {}
        self.emojiId2Heat = {}

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
                elif order[0] == 'add_tag' or order[0] == 'at':
                    check_func = self.check_add_tag
                elif order[0] == 'del_tag' or order[0] == 'dt':
                    check_func = self.check_del_tag
                elif order[0] == 'add_to_tag' or order[0] == 'att':
                    check_func = self.check_add_to_tag
                elif order[0] == 'del_from_tag' or order[0] == 'dft':
                    check_func = self.check_del_from_tag
                elif order[0] == 'query_tag_value_sum' or order[0] == 'qtvs':
                    check_func = self.check_query_tag_value_sum
                elif order[0] == 'query_tag_age_var' or order[0] == 'qtav':
                    check_func = self.check_query_tag_age_var
                elif order[0] == 'query_best_acquaintance' or order[0] == 'qba':
                    check_func = self.check_query_best_acquaintance
                elif order[0] == 'query_couple_sum' or order[0] == 'qcs':
                    check_func = self.check_query_couple_sum
                elif order[0] == 'query_shortest_path' or order[0] == 'qsp':
                    check_func = self.check_query_shortest_path
                elif order[0] == 'add_message' or order[0] == 'am':
                    check_func = self.check_add_message
                elif order[0] == 'send_message' or order[0] == 'sm':
                    check_func = self.check_send_message
                elif order[0] == 'query_social_value' or order[0] == 'qsv':
                    check_func = self.check_query_social_value
                elif order[0] == 'query_received_messages' or order[0] == 'qrm':
                    check_func = self.check_query_received_messages
                elif order[0] == 'add_red_envelope_message' or order[0] == 'arem':
                    check_func = self.check_add_red_envelope_message
                elif order[0] == 'add_notice_message' or order[0] == 'anm':
                    check_func = self.check_add_notice_message
                elif order[0] == 'clean_notices' or order[0] == 'cn':
                    check_func = self.check_clean_notices
                elif order[0] == 'add_emoji_message' or order[0] == 'aem':
                    check_func = self.check_add_emoji_message
                elif order[0] == 'store_emoji_id' or order[0] == 'sei':
                    check_func = self.check_store_emoji_id
                elif order[0] == 'query_popularity' or order[0] == 'qp':
                    check_func = self.check_query_popularity
                elif order[0] == 'delete_cold_emoji' or order[0] == 'dce':
                    check_func = self.check_delete_cold_emoji
                elif order[0] == 'query_money' or order[0] == 'qm':
                    check_func = self.check_query_money
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
                for tag in self.id2Person[id1].tags.values():
                    if id2 in tag.persons.keys():
                        tag.del_person(id2)
                for tag in self.id2Person[id2].tags.values():
                    if id1 in tag.persons.keys():
                        tag.del_person(id1)
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
        return str(sum(nx.triangles(self.graph).values()) // 3)

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

    def check_add_tag(self, order) -> str:
        id1 = int(order[1])
        tag_id = int(order[2])
        if id1 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        person1 = self.id2Person[id1]
        if tag_id in person1.tags.keys():
            self.exception["eti"] += 1
            if tag_id in self.etiId2Num.keys():
                self.etiId2Num[tag_id] += 1
            else:
                self.etiId2Num[tag_id] = 1
            return f"eti-{self.exception['eti']}, {tag_id}-{self.etiId2Num[tag_id]}"
        person1.add_tag(Tag(tag_id))
        return "Ok"

    def check_del_tag(self, order) -> str:
        id1 = int(order[1])
        tag_id = int(order[2])
        if id1 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        person1 = self.id2Person[id1]
        if tag_id not in person1.tags.keys():
            self.exception["tinf"] += 1
            if tag_id in self.tinfId2Num.keys():
                self.tinfId2Num[tag_id] += 1
            else:
                self.tinfId2Num[tag_id] = 1
            return f"tinf-{self.exception['tinf']}, {tag_id}-{self.tinfId2Num[tag_id]}"
        person1.del_tag(tag_id)
        return "Ok"

    def check_add_to_tag(self, order) -> str:
        id1 = int(order[1])
        id2 = int(order[2])
        tag_id = int(order[3])
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
            self.exception["rnf"] += 1
            id1 = min(int(order[1]), int(order[2]))
            id2 = max(int(order[1]), int(order[2]))
            if id1 in self.rnfId2Num.keys():
                self.rnfId2Num[id1] += 1
            else:
                self.rnfId2Num[id1] = 1
            if id2 in self.rnfId2Num.keys():
                self.rnfId2Num[id2] += 1
            else:
                self.rnfId2Num[id2] = 1
            return f"rnf-{self.exception['rnf']}, {id1}-{self.rnfId2Num[id1]}, {id2}-{self.rnfId2Num[id2]}"
        person2 = self.id2Person[id2]
        if tag_id not in person2.tags.keys():
            self.exception["tinf"] += 1
            if tag_id in self.tinfId2Num.keys():
                self.tinfId2Num[tag_id] += 1
            else:
                self.tinfId2Num[tag_id] = 1
            return f"tinf-{self.exception['tinf']}, {tag_id}-{self.tinfId2Num[tag_id]}"
        if id1 in person2.tags[tag_id].persons.keys():
            self.exception["epi"] += 1
            if id1 in self.epiId2Num.keys():
                self.epiId2Num[id1] += 1
            else:
                self.epiId2Num[id1] = 1
            return f"epi-{self.exception['epi']}, {id1}-{self.epiId2Num[id1]}"
        if person2.tags[tag_id].get_size() <= 1111:
            person2.add_person_to_tag(self.id2Person[id1], tag_id)
        return "Ok"

    def check_del_from_tag(self, order) -> str:
        id1 = int(order[1])
        id2 = int(order[2])
        tag_id = int(order[3])
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
        person2 = self.id2Person[id2]
        if tag_id not in person2.tags.keys():
            self.exception["tinf"] += 1
            if tag_id in self.tinfId2Num.keys():
                self.tinfId2Num[tag_id] += 1
            else:
                self.tinfId2Num[tag_id] = 1
            return f"tinf-{self.exception['tinf']}, {tag_id}-{self.tinfId2Num[tag_id]}"
        if id1 not in person2.tags[tag_id].persons.keys():
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        person2.del_person_from_tag(id1, tag_id)
        return "Ok"

    def check_query_tag_value_sum(self, order) -> str:
        id1 = int(order[1])
        tag_id = int(order[2])
        if id1 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        elif tag_id not in self.id2Person[id1].tags.keys():
            self.exception["tinf"] += 1
            if tag_id in self.tinfId2Num.keys():
                self.tinfId2Num[tag_id] += 1
            else:
                self.tinfId2Num[tag_id] = 1
            return f"tinf-{self.exception['tinf']}, {tag_id}-{self.tinfId2Num[tag_id]}"
        nodes = self.id2Person[id1].tags[tag_id].persons.keys()
        subgraph = self.graph.subgraph(nodes)
        result = sum(self.graph[u][v]['weight'] for u, v in subgraph.edges)
        return str(result * 2)

    def check_query_tag_age_var(self, order) -> str:
        id1 = int(order[1])
        tag_id = int(order[2])
        if id1 not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        elif tag_id not in self.id2Person[id1].tags.keys():
            self.exception["tinf"] += 1
            if tag_id in self.tinfId2Num.keys():
                self.tinfId2Num[tag_id] += 1
            else:
                self.tinfId2Num[tag_id] = 1
            return f"tinf-{self.exception['tinf']}, {tag_id}-{self.tinfId2Num[tag_id]}"
        result = self.id2Person[id1].tags[tag_id].get_age_var()
        return str(result)

    def check_query_best_acquaintance(self, order, cal_exceptions=True) -> str:
        id1 = int(order[1])
        if id1 not in self.id2Person.keys():
            if not cal_exceptions:
                return ""
            self.exception["pinf"] += 1
            if id1 in self.pinfId2Num.keys():
                self.pinfId2Num[id1] += 1
            else:
                self.pinfId2Num[id1] = 1
            return f"pinf-{self.exception['pinf']}, {id1}-{self.pinfId2Num[id1]}"
        elif not list(self.graph.neighbors(id1)):
            if not cal_exceptions:
                return ""
            self.exception["anf"] += 1
            if id1 in self.anfId2Num.keys():
                self.anfId2Num[id1] += 1
            else:
                self.anfId2Num[id1] = 1
            return f"anf-{self.exception['anf']}, {id1}-{self.anfId2Num[id1]}"
        neighbors = list(self.graph.neighbors(id1))
        max_weight = float("-inf")
        max_weight_node = None
        for neighbor in neighbors:
            weight = self.graph[id1][neighbor].get('weight')
            if weight > max_weight or (weight == max_weight and neighbor < max_weight_node):
                max_weight = weight
                max_weight_node = neighbor
        return str(max_weight_node)

    def check_query_couple_sum(self, order) -> str:
        result = 0
        for node in self.graph.nodes:
            best_node = self.check_query_best_acquaintance(["", node], False)
            if best_node:
                best_best_node = self.check_query_best_acquaintance(["", best_node], False)
                if best_best_node and int(best_best_node) == node:
                    result += 1
        return str(int(result / 2))

    def check_query_shortest_path(self, order) -> str:
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
        elif not nx.has_path(self.graph, id1, id2):
            id1 = min(int(order[1]), int(order[2]))
            id2 = max(int(order[1]), int(order[2]))
            self.exception["pnf"] += 1
            if id1 in self.pnfId2Num.keys():
                self.pnfId2Num[id1] += 1
            else:
                self.pnfId2Num[id1] = 1
            if id2 in self.pnfId2Num.keys():
                self.pnfId2Num[id2] += 1
            else:
                self.pnfId2Num[id2] = 1
            return f"pnf-{self.exception['pnf']}, {id1}-{self.pnfId2Num[id1]}, {id2}-{self.pnfId2Num[id2]}"
        if id1 == id2:
            return str(0)
        return str(nx.shortest_path_length(self.graph, source=id1, target=id2) - 1)

    def check_add_message(self, order) -> str:
        messageId = int(order[1])
        social_value = int(order[2])
        type0 = int(order[3])
        person_id1 = int(order[4])
        person_id2_or_tag_id = int(order[5])
        if type0 == 0 and ((person_id1 not in self.id2Person.keys()) or (
                person_id2_or_tag_id not in self.id2Person.keys())):
            return "The person with this number does not exist"
        if type0 == 1 and person_id1 not in self.id2Person.keys():
            return "The person with this number does not exist"
        person1 = self.id2Person[person_id1]
        if type0 == 1 and person_id2_or_tag_id not in person1.tags.keys():
            return "Tag does not exist"
        if messageId in self.id2Message.keys():
            self.exception["emi"] += 1
            if messageId in self.emiId2Num.keys():
                self.emiId2Num[messageId] += 1
            else:
                self.emiId2Num[messageId] = 1
            return f"emi-{self.exception['emi']}, {messageId}-{self.emiId2Num[messageId]}"
        if type0 == 0 and person_id2_or_tag_id == person_id1:
            self.exception["epi"] += 1
            if person_id1 in self.epiId2Num.keys():
                self.epiId2Num[person_id1] += 1
            else:
                self.epiId2Num[person_id1] = 1
            return f"epi-{self.exception['epi']}, {person_id1}-{self.epiId2Num[person_id1]}"
        self.id2Message[messageId] = Message(messageId, social_value, type0, person_id1, person_id2_or_tag_id)
        return "Ok"

    def check_send_message(self, order) -> str:
        messageId = int(order[1])
        if messageId not in self.id2Message.keys():
            self.exception["minf"] += 1
            if messageId in self.minfId2Num.keys():
                self.minfId2Num[messageId] += 1
            else:
                self.minfId2Num[messageId] = 1
            return f"minf-{self.exception['minf']}, {messageId}-{self.minfId2Num[messageId]}"
        message = self.id2Message[messageId]
        if message.type == 0 and not self.graph.has_edge(message.person_id1, message.person_id2):
            self.exception["rnf"] += 1
            id1 = min(message.person_id1, message.person_id2)
            id2 = max(message.person_id1, message.person_id2)
            if id1 in self.rnfId2Num.keys():
                self.rnfId2Num[id1] += 1
            else:
                self.rnfId2Num[id1] = 1
            if id2 in self.rnfId2Num.keys():
                self.rnfId2Num[id2] += 1
            else:
                self.rnfId2Num[id2] = 1
            return f"rnf-{self.exception['rnf']}, {id1}-{self.rnfId2Num[id1]}, {id2}-{self.rnfId2Num[id2]}"
        person1 = self.id2Person[message.person_id1]
        if message.type == 1 and message.tag_id not in person1.tags.keys():
            self.exception["tinf"] += 1
            if message.tag_id in self.tinfId2Num.keys():
                self.tinfId2Num[message.tag_id] += 1
            else:
                self.tinfId2Num[message.tag_id] = 1
            return f"tinf-{self.exception['tinf']}, {message.tag_id}-{self.tinfId2Num[message.tag_id]}"
        if message.type == 0:
            person2 = self.id2Person[message.person_id2]
            del self.id2Message[messageId]
            person2.add_message(message)
            person1.add_social_value(message.social_value)
            person2.add_social_value(message.social_value)
            if message.special_type == 'red_envelope':
                person1.add_money(-int(message.special_character))
                person2.add_money(int(message.special_character))
            elif message.special_type == 'emoji':
                self.emojiId2Heat[int(message.special_character)] += 1
        elif message.type == 1:
            tag = person1.tags[message.tag_id]
            del self.id2Message[messageId]
            person1.add_social_value(message.social_value)
            for person in tag.persons.values():
                person.add_social_value(message.social_value)
            if message.special_type == 'red_envelope':
                money = 0
                if tag.get_size() > 0:
                    money = int(message.special_character) // tag.get_size()
                for person in tag.persons.values():
                    person.add_money(money)
                person1.add_money(-tag.get_size() * money)
            elif message.special_type == 'emoji':
                self.emojiId2Heat[int(message.special_character)] += 1
        return "Ok"

    def check_query_social_value(self, order) -> str:
        person_id = int(order[1])
        if person_id not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if person_id in self.pinfId2Num.keys():
                self.pinfId2Num[person_id] += 1
            else:
                self.pinfId2Num[person_id] = 1
            return f"pinf-{self.exception['pinf']}, {person_id}-{self.pinfId2Num[person_id]}"
        return str(self.id2Person[person_id].social_value)

    def check_query_received_messages(self, order) -> str:
        person_id = int(order[1])
        if person_id not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if person_id in self.pinfId2Num.keys():
                self.pinfId2Num[person_id] += 1
            else:
                self.pinfId2Num[person_id] = 1
            return f"pinf-{self.exception['pinf']}, {person_id}-{self.pinfId2Num[person_id]}"
        person = self.id2Person[person_id]
        return person.get_received_message()

    def check_add_red_envelope_message(self, order) -> str:
        messageId = int(order[1])
        money = int(order[2])
        type0 = int(order[3])
        person_id1 = int(order[4])
        person_id2_or_tag_id = int(order[5])
        if type0 == 0 and ((person_id1 not in self.id2Person.keys()) or (
                person_id2_or_tag_id not in self.id2Person.keys())):
            return "The person with this number does not exist"
        if type0 == 1 and person_id1 not in self.id2Person.keys():
            return "The person with this number does not exist"
        person1 = self.id2Person[person_id1]
        if type0 == 1 and person_id2_or_tag_id not in person1.tags.keys():
            return "Tag does not exist"
        if messageId in self.id2Message.keys():
            self.exception["emi"] += 1
            if messageId in self.emiId2Num.keys():
                self.emiId2Num[messageId] += 1
            else:
                self.emiId2Num[messageId] = 1
            return f"emi-{self.exception['emi']}, {messageId}-{self.emiId2Num[messageId]}"
        if type0 == 0 and person_id2_or_tag_id == person_id1:
            self.exception["epi"] += 1
            if person_id1 in self.epiId2Num.keys():
                self.epiId2Num[person_id1] += 1
            else:
                self.epiId2Num[person_id1] = 1
            return f"epi-{self.exception['epi']}, {person_id1}-{self.epiId2Num[person_id1]}"
        self.id2Message[messageId] = Message(messageId, 5 * money, type0, person_id1, person_id2_or_tag_id,
                                             'red_envelope', str(money))
        return "Ok"

    def check_add_notice_message(self, order):
        messageId = int(order[1])
        string = str(order[2])
        type0 = int(order[3])
        person_id1 = int(order[4])
        person_id2_or_tag_id = int(order[5])
        if type0 == 0 and (person_id1 not in self.id2Person.keys()) or (
                person_id2_or_tag_id not in self.id2Person.keys()):
            return "The person with this number does not exist"
        if type0 == 1 and person_id1 not in self.id2Person.keys():
            return "The person with this number does not exist"
        person1 = self.id2Person[person_id1]
        if type0 == 1 and person_id2_or_tag_id not in person1.tags.keys():
            return "Tag does not exist"
        if messageId in self.id2Message.keys():
            self.exception["emi"] += 1
            if messageId in self.emiId2Num.keys():
                self.emiId2Num[messageId] += 1
            else:
                self.emiId2Num[messageId] = 1
            return f"emi-{self.exception['emi']}, {messageId}-{self.emiId2Num[messageId]}"
        if type0 == 0 and person_id2_or_tag_id == person_id1:
            self.exception["epi"] += 1
            if person_id1 in self.epiId2Num.keys():
                self.epiId2Num[person_id1] += 1
            else:
                self.epiId2Num[person_id1] = 1
            return f"epi-{self.exception['epi']}, {person_id1}-{self.epiId2Num[person_id1]}"
        self.id2Message[messageId] = Message(messageId, len(string), type0, person_id1, person_id2_or_tag_id, 'notice',
                                             string)
        return "Ok"

    def check_clean_notices(self, order):
        person_id = int(order[1])
        if person_id not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if person_id in self.pinfId2Num.keys():
                self.pinfId2Num[person_id] += 1
            else:
                self.pinfId2Num[person_id] = 1
            return f"pinf-{self.exception['pinf']}, {person_id}-{self.pinfId2Num[person_id]}"
        person = self.id2Person[person_id]
        person.clean_notices()
        return "Ok"

    def check_add_emoji_message(self, order):
        messageId = int(order[1])
        emojiNumber = int(order[2])
        type0 = int(order[3])
        person_id1 = int(order[4])
        person_id2_or_tag_id = int(order[5])
        if type0 == 0 and ((person_id1 not in self.id2Person.keys()) or (
                person_id2_or_tag_id not in self.id2Person.keys())):
            return "The person with this number does not exist"
        if type0 == 1 and person_id1 not in self.id2Person.keys():
            return "The person with this number does not exist"
        person1 = self.id2Person[person_id1]
        if type0 == 1 and person_id2_or_tag_id not in person1.tags.keys():
            return "Tag does not exist"
        if messageId in self.id2Message.keys():
            self.exception["emi"] += 1
            if messageId in self.emiId2Num.keys():
                self.emiId2Num[messageId] += 1
            else:
                self.emiId2Num[messageId] = 1
            return f"emi-{self.exception['emi']}, {messageId}-{self.emiId2Num[messageId]}"
        if emojiNumber not in self.emojiId2Heat.keys():
            self.exception['einf'] += 1
            if emojiNumber in self.einfId2Num.keys():
                self.einfId2Num[emojiNumber] += 1
            else:
                self.einfId2Num[emojiNumber] = 1
            return f"einf-{self.exception['einf']}, {emojiNumber}-{self.einfId2Num[emojiNumber]}"
        if type0 == 0 and person_id2_or_tag_id == person_id1:
            self.exception["epi"] += 1
            if person_id1 in self.epiId2Num.keys():
                self.epiId2Num[person_id1] += 1
            else:
                self.epiId2Num[person_id1] = 1
            return f"epi-{self.exception['epi']}, {person_id1}-{self.epiId2Num[person_id1]}"
        self.id2Message[messageId] = Message(messageId, emojiNumber, type0, person_id1, person_id2_or_tag_id, 'emoji',
                                             str(emojiNumber))
        return "Ok"

    def check_store_emoji_id(self, order):
        emoji_id = int(order[1])
        if emoji_id in self.emojiId2Heat.keys():
            self.exception["eei"] += 1
            if emoji_id in self.eeiId2Num.keys():
                self.eeiId2Num[emoji_id] += 1
            else:
                self.eeiId2Num[emoji_id] = 1
            return f"eei-{self.exception['eei']}, {emoji_id}-{self.eeiId2Num[emoji_id]}"
        self.emojiId2Heat[emoji_id] = 0
        return "Ok"

    def check_query_popularity(self, order):
        emoji_id = int(order[1])
        if emoji_id not in self.emojiId2Heat.keys():
            self.exception["einf"] += 1
            if emoji_id in self.einfId2Num.keys():
                self.einfId2Num[emoji_id] += 1
            else:
                self.einfId2Num[emoji_id] = 1
            return f"einf-{self.exception['einf']}, {emoji_id}-{self.einfId2Num[emoji_id]}"
        return str(self.emojiId2Heat[emoji_id])

    def check_delete_cold_emoji(self, order):
        limit = int(order[1])
        message_id_to_del = []
        for emoji_id in list(self.emojiId2Heat.keys()):
            if self.emojiId2Heat[emoji_id] <= limit:
                del self.emojiId2Heat[emoji_id]
                for message in self.id2Message.values():
                    if message.special_type == 'emoji' and int(message.special_character) == emoji_id:
                        message_id_to_del.append(message.id)
        for message_id in message_id_to_del:
            del self.id2Message[message_id]
        return str(len(self.emojiId2Heat))

    def check_query_money(self, order):
        person_id = int(order[1])
        if person_id not in self.id2Person.keys():
            self.exception["pinf"] += 1
            if person_id in self.pinfId2Num.keys():
                self.pinfId2Num[person_id] += 1
            else:
                self.pinfId2Num[person_id] = 1
            return f"pinf-{self.exception['pinf']}, {person_id}-{self.pinfId2Num[person_id]}"
        return str(self.id2Person[person_id].money)

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
