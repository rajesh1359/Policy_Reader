import fitz
import re
import json

icici_Policy_Map = {
    'OD': [['damage'], []],
    'TP': [['liability', 'only'], ['damage']],
    'Package': [['package'], ['liability']]
}

policy_map = {
    "COMM_PKG_GOODS": "Goods Carrying Vehicles Package Policy",
    "COMM_PKG_PSG": "Passenger Carrying Vehicles Package Policy",
    "PVT_PKG": "Private Car Package Policy",
    "PVT_SOD": "Stand-Alone Own Damage Private Car Insurance Policy",
    "TW_PKG": "Two Wheeler Vehicles Package Policy",
    "TW_TP": "Two Wheeler Vehicles Liability Policy",
    "TW_SOD": "Stand-Alone Own Damage Two wheeler Insurance Policy",
    "MISC_TP": "Miscellaneous Vehicles Liability Policy",
}

class ICICI:
    def __init__(self,pdf_file):
        self.doc = fitz.Document(pdf_file)
        self.policy_version = None
        self.policy_type = None

    def get_POI(self, pattern):
        POI = None
        code = None
        agent_code = None
        for page in self.doc.pages():
            for line in page.get_text().splitlines():
                # page_text = page.get_text()

                m = re.match(pattern, line.lower())
                if m is not None:
                    POI = page
                    # print('found')
                    break
            if POI is not None:
                break
        return POI

    def get_policy_info(self):
        print(self.get_policy_type())
    def get_policy_type(self):
        policy_type_string = None
        vehicle_type = None
        policytype = None
        POI = self.get_POI('.*servicing\s*branch.*')
        s1 = (POI.search_for('Registration No'))[0]
        print(" ".join(POI.get_textbox([s1.x0, s1.y0, 9999, s1.y1]).split()))
        # print(POI.get_text())
        if POI is not None:

            for tp,st in policy_map.items():
                search1 = POI.search_for(st, hit_max=1)
                if search1:
                    return tp

                #print(tp)
                #return tp
                # s1 = search1[0]
                #policy_type_string = " ".join(POI.get_textbox([s1.x0, s1.y0, 9999, s1.y1]).split())
        # for line in POI.get_text().splitlines():
        #     policy_type_pattern = '.*auto\s*secure\s+(.*)'
        #     m = re.match(policy_type_pattern, line.lower())
        #
        #     #print(line)
        #     if m is not None:
        #         policy_type_string = m.groups()[0].strip().replace(u'\xa0', u' ')
        #         break
        #print('policy_type_string ',policy_type_string)
        # if policy_type_string is not None:
        #     for policy_type, attrib in Tata_Policy_Map.items():
        #         check_list_true = set([attr in policy_type_string.lower() for attr in attrib[0]])
        #         check_list_false = set([attr in policy_type_string.lower() for attr in attrib[1]])
        #         if not True in check_list_false and not False in check_list_true:
        #             # print('Policy Type is {0}'.format(policy_type))
        #             policytype = policy_type
        #             break
        #
        #     vehicle = None
        #     if 'commercial' in policy_type_string.lower():
        #         vehicle = 'Commercial'
        #     elif 'private' in policy_type_string.lower() and 'car'  in policy_type_string.lower():
        #         vehicle = 'Private Car'
        #     else:
        #         vehicle = 'UnKnown'
        #     self.policy_type = policytype
        #     self.vehicle_type = vehicle

        return policy_type_string

# file_name = r"E:\NewDownloads\DemoDownloads\tata policy\icici\Goods_Carrying_Commercial.pdf"
# obj = ICICI(pdf_file=file_name)
# print(obj.get_policy_type())