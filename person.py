class Person:
    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age
        self.tags = {}

    def add_tag(self, tag):
        self.tags[tag.tag_id] = tag

    def add_person_to_tag(self, person, tag_id):
        self.tags[tag_id].add_person(person)

    def del_tag(self, tag_id):
        self.tags.pop(tag_id)

    def del_person_from_tag(self, person_id, tag_id):
        self.tags[tag_id].del_person(person_id)
