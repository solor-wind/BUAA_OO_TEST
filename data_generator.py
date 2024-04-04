import random
import json
from pathlib import Path

config = json.load(open('config.json'))
command_limit = config['command_limit']  # 一次输入的命令数量
time_limit = config['time_limit']  # 时间限制
reset_prob = config['reset_prob']  # 重置概率

class DataGenerator:
    # 使用方法: 调用get_inputs()方法获取生成的数据, 调用dump_inputs(file_path)方法将数据写入文件
    def __init__(self):
        global command_limit
        self.input_num = random.randint(1, command_limit)
        self.last_reset_time = [0, 0, 0, 0, 0, 0]
        self.time_list = []
        self.customerId_list = []
        self.inputs = []
        self.generate_data()

    def generate_data(self):
        global time_limit, reset_prob
        self.generate_time_list()
        self.generate_customerid_list()
        for i in range(self.input_num):
            if random.random() < reset_prob:
                temp_elevator_id_list = [1, 2, 3, 4, 5, 6]
                while True:
                    index = random.choice(range(0, len(temp_elevator_id_list)))
                    elevator_id = temp_elevator_id_list.pop(index)
                    if self.time_list[i] - self.last_reset_time[elevator_id - 1] < 3:  # 如果与上一次重置的间隔小于3s
                        if len(temp_elevator_id_list) == 0:
                            self.inputs.append(self.generate_request(i))
                            break
                        else:
                            continue
                    else:
                        self.inputs.append(self.generate_reset(elevator_id, i))
                        self.last_reset_time[elevator_id - 1] = self.time_list[i]
                        break
            else:
                self.inputs.append(self.generate_request(i))

    def generate_reset(self, elevatorId, index) -> str:
        capacity = random.randint(3, 8)
        move_time = random.choice([0.2, 0.3, 0.4, 0.5, 0.6])
        return f"[{self.time_list[index]}]RESET-Elevator-{elevatorId}-{capacity}-{move_time}"

    def generate_time_list(self):
        global time_limit
        self.time_list = [round(random.uniform(1, time_limit), 1) for _ in range(self.input_num)]
        self.time_list.sort()

    def generate_customerid_list(self):
        global command_limit
        self.customerId_list = random.sample(range(1, command_limit + 100), self.input_num)  # 缺陷：只能生成1到150的乘客id

    def generate_request(self, index) -> str:
        customerId = self.customerId_list[index]
        from_floor, to_floor = random.sample(range(1, 12), 2)
        return f"[{self.time_list[index]}]{customerId}-FROM-{from_floor}-TO-{to_floor}"

    def get_inputs(self):
        """
        获取生成的数据
        :return: 包含有输入数据的列表
        """

        return self.inputs

    def dump_inputs(self, file_path):
        """
        将生成的数据写入文件
        :param file_path: 输出文件路径
        :return: 无
        """
        target = Path(file_path)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w') as file:
            for input in self.inputs:
                file.write(input + '\n')


if __name__ == '__main__':
    dataGenerator = DataGenerator()
    print(dataGenerator.get_inputs())
    dataGenerator.dump_inputs('data/input.txt')
