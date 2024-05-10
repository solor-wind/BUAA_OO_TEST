class Message:
    def __init__(self, id1, social_value, type0, person_id1, person_id2_or_tag_id, special_type = "ordinary",
                 special_character = None):
        self.id = id1
        self.social_value = social_value
        self.type = type0
        self.person_id1 = person_id1
        if type0 == 0:
            self.person_id2 = person_id2_or_tag_id
            self.tag_id = None
        elif type0 == 1:
            self.tag_id = person_id2_or_tag_id
            self.person_id2 = None
        self.special_type = None
        self.special_type = special_type
        self.special_character = special_character


