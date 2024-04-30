class Tag:
    def __init__(self, tag_id):
        self.tag_id = tag_id
        self.persons = {}

    def add_person(self, person):
        self.persons[person.id] = person

    def get_age_mean(self):
        if not self.persons:
            return 0
        return sum([person.age for person in self.persons.values()]) // len(self.persons)

    def get_age_var(self):
        if not self.persons:
            return 0
        mean = self.get_age_mean()
        return sum([(person.age - mean) ** 2 for person in self.persons.values()]) // len(self.persons)

    def del_person(self, person_id):
        self.persons.pop(person_id)

    def get_size(self):
        return len(self.persons)

