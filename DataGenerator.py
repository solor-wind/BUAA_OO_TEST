from Checker import Library, Person
import json
import random
from datetime import datetime, timedelta

config = json.load(open('config.json', 'r'))
b_date = config['begin_date']
e_date = config['end_date']
max_num_of_days_with_command = int(config['max_num_of_days_with_command'])
command_num = int(config['basic_command_num'])
num_identifier = int(config['max_num_of_book_identifier'])
num_book = int(config['max_num_of_book_for_each_identifier'])
num_person = int(config['max_num_of_person'])
query_prob = float(config['query_prob'])
borrow_prob = float(config['borrow_prob'])
order_prob = float(config['order_prob'])
return_prob = float(config['return_prob'])
pick_1_prob = float(config['pick_1_prob'])
pick_2_prob = float(config['pick_2_prob'])


def split_list_randomly(lst, n):
    groups = [[] for _ in range(n)]
    random.shuffle(lst)
    for item in lst:
        random.choice(groups).append(item)
    return groups


def generate_books_specified(identifier) -> dict:
    global num_identifier, num_book
    identifiers_num = random.randint(1, num_identifier)
    identifiers = random.sample(range(1, round(identifiers_num + 10)), identifiers_num)
    books = [f"{identifier}-{number:04}" for number in identifiers]
    nums = random.choices(range(1, num_book), k=len(books))
    return dict(zip(books, nums))


def generate_basic_date() -> list:
    global command_num, b_date, e_date, max_num_of_days_with_command
    begin_date = datetime.strptime(b_date, "%Y-%m-%d")
    end_date = datetime.strptime(e_date, "%Y-%m-%d")
    delta = end_date - begin_date
    num_of_days_with_command = random.randint(max_num_of_days_with_command // 2, max_num_of_days_with_command)
    random_days = random.sample(range(delta.days), num_of_days_with_command)
    dates_with_commands = [str((begin_date + timedelta(days=day)).date()) for day in random_days]
    return sorted(dates_with_commands)


class data_generator:
    def __init__(self, library):
        self.index = 0
        self.library = library
        self.commands = []
        self.init_command_list = []  # 初始化图书信息的命令里列表
        self.date2commands = {}
        self.generate_books()
        self.generate_persons()
        self.generate_basic_commands()
        pass
        self.open_flag = True
        self.close_flag = False
        self.end_flag = False
        self.date = list(self.date2commands.keys())[0]

    def generate_books(self):
        prob = random.random()
        if prob < 0.5:
            type_num = 3
        elif prob < 0.75:
            type_num = 2
        else:
            type_num = 1
        types = random.sample(['A', 'B', 'C'], type_num)
        self.commands.append(f"{type_num}\n")
        temp_commands = []
        for type in types:
            books = generate_books_specified(type)
            for book, num in books.items():
                temp_commands.append(f"{book} {num}\n")
                self.library.add_book(book, num)
        random.shuffle(temp_commands)
        self.commands.extend(temp_commands)
        self.init_command_list = [str(len(temp_commands)) + '\n'] + temp_commands

    def generate_persons(self):
        global num_person
        temp_ids = random.sample(range(1, 99999999), random.randint(num_person // 2, num_person))
        ids = [f"{temp_id:08}" for temp_id in temp_ids]
        for id in ids:
            self.library.persons[id] = Person(id)

    def generate_basic_commands(self):
        global command_num, query_prob, borrow_prob, order_prob
        dates = generate_basic_date()
        t_command_num = random.randint(max(command_num // 2, 1), command_num)
        tmp_commands = []
        for i in range(t_command_num):
            prob = random.random()
            if prob < query_prob:
                tmp_commands.append(self.generate_query())
            elif prob < query_prob + borrow_prob:
                tmp_commands.append(self.generate_borrow())
            else:
                tmp_commands.append(self.generate_order())
        tmp_commands = split_list_randomly(tmp_commands, len(dates))
        for date in dates:
            self.date2commands[date] = tmp_commands.pop(0)

    def generate_query(self) -> str:
        person_id = random.choice(list(self.library.persons.keys()))
        book = random.choice(list(self.library.bs.keys()))
        return f"{person_id} queried {book}\n"

    def generate_borrow(self) -> str:
        person_id = random.choice(list(self.library.persons.keys()))
        book = random.choice(list(self.library.bs.keys()))
        return f"{person_id} borrowed {book}\n"

    def generate_order(self) -> str:
        person_id = random.choice(list(self.library.persons.keys()))
        book = random.choice(list(self.library.bs.keys()))
        return f"{person_id} ordered {book}\n"

    def generate_pick(self, person_id, book_id):
        return f"{person_id} picked {book_id}\n"

    def generate_return(self, person_id, book_id):
        return f"{person_id} returned {book_id}\n"

    def add_command(self, output=""):
        """
        将输出结果导入数据生成器
        :param output: 生成的字符串
        :return:
        """
        global e_date, pick_1_prob, pick_2_prob, return_prob
        if 'accept' in output:
            date_str = output.split(" ")[0].strip("\n")
            book_id = output.split(" ")[-1].strip("\n")
            person_id = output.split(" ")[2].strip("\n")
            date = datetime.strptime(date_str, "[%Y-%m-%d]")
            date_str = str(date.date())
            end_date = datetime.strptime(e_date, "%Y-%m-%d")
            if 'borrowed' in output or "picked" in output:
                if random.random() < return_prob:
                    self.end_date = end_date.date().__str__()
                    delta = end_date - date
                    next_date_str = str((date + timedelta(days=random.randint(0, delta.days))).date())
                    command = self.generate_return(person_id, book_id)
                    if next_date_str == date_str:
                        insert_place = random.randint(self.index, len(self.date2commands[date_str]))
                        self.date2commands[date_str].insert(insert_place, command)
                    elif next_date_str in self.date2commands:
                        insert_place = random.randint(0, len(self.date2commands[next_date_str]))
                        self.date2commands[next_date_str].insert(insert_place, command)
                    else:
                        self.date2commands[next_date_str] = [command]
                        self.date2commands = dict(sorted(self.date2commands.items()))
            if 'ordered' in output:
                prob = random.random()
                if prob < pick_2_prob:  # 生成两条pick
                    command = self.generate_pick(person_id, book_id)
                    for i in range(2):
                        next_date_str = str((date + timedelta(days=random.randint(0, min(12, (end_date - date).days)))).date())
                        if next_date_str == date_str:
                            insert_place = random.randint(self.index, len(self.date2commands[date_str]))
                            self.date2commands[date_str].insert(insert_place, command)
                        elif next_date_str in self.date2commands:
                            insert_place = random.randint(0, len(self.date2commands[next_date_str]))
                            self.date2commands[next_date_str].insert(insert_place, command)
                        else:
                            self.date2commands[next_date_str] = [command]
                            self.date2commands = dict(sorted(self.date2commands.items()))
                elif prob < pick_1_prob + pick_2_prob:  # 生成一条pick
                    command = self.generate_pick(person_id, book_id)
                    next_date_str = str((date + timedelta(days=random.randint(0, min(12, (end_date - date).days)))).date())
                    if next_date_str == date_str:
                        insert_place = random.randint(self.index, len(self.date2commands[date_str]))
                        self.date2commands[date_str].insert(insert_place, command)
                    elif next_date_str in self.date2commands:
                        insert_place = random.randint(0, len(self.date2commands[next_date_str]))
                        self.date2commands[next_date_str].insert(insert_place, command)
                    else:
                        self.date2commands[next_date_str] = [command]
                        self.date2commands = dict(sorted(self.date2commands.items()))

    def get_next_command(self) -> str:
        """
        获取下一个命令
        :return: 下一个命令
        """
        if self.index == len(self.date2commands[self.date]):
            self.close_flag = True
        if self.end_flag:
            return ""
        if self.close_flag:
            self.close_flag = False
            command = f"[{self.date}] CLOSE\n"
            i = list(self.date2commands.keys()).index(self.date)
            if i + 1 == len(self.date2commands):
                self.end_flag = True
            else:
                self.date = list(self.date2commands.keys())[i + 1]
                self.index = 0
                self.open_flag = True
        elif self.open_flag:
            self.open_flag = False
            command = f"[{self.date}] OPEN\n"
            if not self.date2commands[self.date]:
                self.close_flag = True
        else:
            command = f"[{self.date}] {self.date2commands[self.date][self.index]}"
            self.index += 1
        self.commands.append(command)
        return command


if __name__ == '__main__':
    library = Library()
    generator = data_generator(library)
    for command in generator.init_command_list:
        print(command, end="")
    while True:
        input_command = generator.get_next_command()
        if input_command == "":
            print("数据生成完毕")
            break
        print(input_command, end="")
        output_command = input("输出结果为:")
        generator.add_command(output_command)
