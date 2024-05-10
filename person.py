from collections import deque
class Person:
    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age
        self.tags = {}
        self.social_value = 0
        self.money = 0
        self.messages = deque()

    def add_tag(self, tag):
        self.tags[tag.tag_id] = tag

    def add_person_to_tag(self, person, tag_id):
        self.tags[tag_id].add_person(person)

    def del_tag(self, tag_id):
        self.tags.pop(tag_id)

    def del_person_from_tag(self, person_id, tag_id):
        self.tags[tag_id].del_person(person_id)

    def add_social_value(self, value):
        self.social_value += value

    def add_message(self, message):
        self.messages.appendleft(message)

    def get_received_message(self) -> str:
        received_messages = []
        for i in range(min(5, len(self.messages))):
            received_messages.append(self.messages[i])
        result_str = ""
        if not received_messages:
            return "None"
        for message in received_messages:
            if message.special_type == 'ordinary':
                result_str += f"Ordinary message: {message.id}"
            elif message.special_type == 'notice':
                result_str += f"notice: {message.special_character}"
            elif message.special_type == 'red_envelope':
                result_str += f"RedEnvelope: {message.special_character}"
            elif message.special_type == 'emoji':
                result_str += f"Emoji: {message.special_character}"
            result_str += "; "
        result_str = result_str[:-2]
        return result_str

    def clean_notices(self):
        to_del_messages = []
        for message in self.messages:
            if message.special_type == 'notice':
                to_del_messages.append(message)
        for message in to_del_messages:
            self.messages.remove(message)

    def add_social_value(self, num):
        self.social_value += num

    def add_money(self, num):
        self.money += num