import json


class Classify:
    def __init__(self, raw_text):
        self.raw_text = raw_text.lower()
        self.json_data = json.load(open("res/policy_class_helper.json", 'r'))

    def get_policy_type(self):
        if "bajaj" in self.raw_text:
            return "Bajaj"
        elif "digit" in self.raw_text:
            return "digit"
        else:
            return "Unknown"

    def get_policy(self):
        for policy in self.json_data["policies"]:
            match_list = [True]
            for identifier in self.json_data["policies"][policy]['identifier']:
                match_list.append(identifier in self.raw_text)
            # print(policy,match_list)
            if len(set(match_list)) == 1:
                return policy

        return "Unknown"

