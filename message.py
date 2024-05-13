class Message:
    def __init__(self, id1, social_value, type0, person1, person2_or_tag, special_type="ordinary",
                 special_character=None):
        self.id = id1
        self.social_value = social_value
        self.type = type0
        self.person1 = person1
        if type0 == 0:
            self.person2 = person2_or_tag
            self.tag = None
        elif type0 == 1:
            self.tag = person2_or_tag
            self.person_id2 = None
        self.special_type = None
        self.special_type = special_type
        self.special_character = special_character
