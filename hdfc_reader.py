import fitz
import re
import json

icici_Policy_Map = {
    'OD': [['damage'], []],
    'TP': [['liability', 'only'], ['damage']],
    'Package': [['package'], ['liability']]
}

Policy_accrpnym = {
    "TW": "Two Wheeler",
    "TP": "TP",
    "PVT": "Private Car",
    "PKG": "Package",
    "SOD": "OD"
}

policy_map = {
    "COMM_PKG_GOODS": ["Goods Carrying Vehicles Package Policy"],
    "COMM_PKG_PSG": ["Passenger Carrying Vehicles Package Policy"],
    "PVT_PKG": ["Private Car Package"],
    "PVT_SOD": ["Private Car Standalone OD Only"],
    "TW_PKG": ["Two Wheeler Comprehensive Policy"],
    "TW_TP": ["Two Wheeler Multiyear Liability", "Two Wheeler Liability"],
    "TW_SOD": ["Two Wheeler Policy Standalone OD Only"]
}


class HDFC:
    def __init__(self, pdf_file):
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

        data_dict = {
            'A': None,
            'B': None,
            'C': None,
            'D': None,
            'E': None,
            'F': None,
            'G': None,
            'H': None,
            'I': None,
            'J': None,
            'K': None,
            'L': None,
            'M': None,
            'N': None,
            'O': None,
            'P': None,
            'Q': None,
            'R': "",
            'S': "",
            'T': None,
            'U': None,
            'V': None,
            'W': None,
            'X': None
        }
        policy_type = self.get_policy_type()
        print(policy_type)
        # if policy_type=="TW_TP":
        name = self.get_insurer_name()
        policy_num = self.get_policy_number()
        issue_date = self.get_policy_issue_date()
        reg_num = self.get_registration_number()
        make = self.get_make()
        model = self.get_model()
        expiry_date = self.get_expiry()
        tp_amount = self.get_tp_amount(policy_type)
        fnl_amount = self.get_final_amount()
        net_amount = self.get_net_amount(policy_type)
        od_amount = self.get_od_amount(policy_type)
        pay_out_key = "O"
        if 'SOD' in policy_type:
            pay_out_key = "N"
        data_dict['A'] = issue_date
        data_dict['B'] = name
        data_dict['C'] = reg_num
        data_dict['D'] = policy_num
        data_dict['E'] = expiry_date
        data_dict['F'] = 'NA'
        data_dict['G'] = Policy_accrpnym[policy_type.split("_")[0]]
        data_dict['H'] = policy_type.split("_")[1]
        data_dict['I'] = 'HDFC ERGO'
        data_dict['J'] = make
        data_dict['K'] = model
        data_dict['L'] = float(fnl_amount)
        data_dict['M'] = float(tp_amount)
        data_dict['N'] = float(od_amount)
        data_dict['O'] = float(net_amount)
        data_dict['P'] = data_dict[pay_out_key]
        data_dict['Q'] = self.get_code()

        self.doc.close()
        return data_dict

    def get_xy(self, poi, text, clip=None):
        if clip is not None:
            s1 = poi.search_for(text, clip=clip)
        else:
            s1 = poi.search_for(text)
        if len(s1) != 0:
            return s1
        else:
            return None

    def get_policy_type(self):

        policy_type_string = None
        vehicle_type = None
        policytype = None
        POI = self.get_POI('.*proposal\s*no.*')
        # s1 = (POI.search_for('Registration No'))[0]
        # print(" ".join(POI.get_textbox([s1.x0, s1.y0, 9999, s1.y1]).split()))
        # print(POI.get_text())
        if POI is not None:

            for tp, st in policy_map.items():
                for label in st:
                    search1 = POI.search_for(label, hit_max=1)
                    if search1:
                        return tp

                # print(tp)
                # return tp
                # s1 = search1[0]
                # policy_type_string = " ".join(POI.get_textbox([s1.x0, s1.y0, 9999, s1.y1]).split())
        # for line in POI.get_text().splitlines():
        #     policy_type_pattern = '.*auto\s*secure\s+(.*)'
        #     m = re.match(policy_type_pattern, line.lower())
        #
        #     #print(line)
        #     if m is not None:
        #         policy_type_string = m.groups()[0].strip().replace(u'\xa0', u' ')
        #         break
        # print('policy_type_string ',policy_type_string)
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

    def get_insurer_name(self):

        POI = self.get_POI('.*proposal\s*no.*')
        s1 = self.get_xy(poi=POI, text='Vehicle Details')
        s2 = self.get_xy(poi=POI, text='Email ID')
        text_list = []
        if not len(s1) == 0 or not len(s2) == 0:
            text_list = POI.get_textbox([0, s1[0].y0, s2[0].x0, s2[0].y0]).split("\n")
        else:
            print("Could not get textbox for name")
        pattern = "^[A-Za-z]+.*"

        for line in text_list:
            if re.match(pattern, line.strip()) is not None:
                return line.strip()
        return None

    def get_policy_number(self):

        POI = self.get_POI('.*policy details.*')
        s1 = self.get_xy(poi=POI, text='Policy No.')
        text_box_content = ""
        text_box_content = POI.get_textbox([s1[0].x0, s1[0].y0 - 5, 9999, s1[0].y1 + 5])
        text_box_content = text_box_content.replace("Policy No.", "").strip()
        only_one_line = False
        if re.match("^\d+\s+.*\d$", text_box_content) is not None:
            only_one_line = True
        if only_one_line:
            return "".join(text_box_content.split())
        else:
            return "".join(text_box_content.split("\n")[0].split())

    def get_policy_issue_date(self):

        POI = self.get_POI('.*policy details.*')
        s1 = self.get_xy(poi=POI, text='Issuance Date')
        text_box_content = ""
        text_box_content = POI.get_textbox([s1[0].x0, s1[0].y0 - 3, 9999, s1[0].y1 + 3])
        text_box_content = text_box_content.replace("Issuance Date", "").strip()
        only_one_line = False
        if re.match("^\d{1,2}/\d{1,2}/\d{4}", text_box_content) is not None:
            only_one_line = True
        if only_one_line:
            return "".join(text_box_content.split())
        else:
            return "".join(text_box_content.split("\n")[0].split())

    def get_registration_number(self):
        POI = self.get_POI('.*policy details.*')

        s_temp1 = self.get_xy(poi=POI, text='Vehicle Details')
        s_temp2 = self.get_xy(poi=POI, text='Email ID')
        s_temp3 = self.get_xy(poi=POI, text='Policy No.')

        s1 = self.get_xy(poi=POI, text='Registration No',
                         clip=[s_temp2[0].x0, s_temp1[0].y1, s_temp3[0].x0, s_temp2[0].y1])
        text_box_content = POI.get_textbox([s1[0].x0, s1[0].y0 - 3, s_temp3[0].x0, s1[0].y1 + 3])
        text_box_content = text_box_content.replace("Registration No", "").strip()
        only_one_line = False
        if not "\n" in text_box_content:
            only_one_line = True
        if only_one_line:
            return "".join(text_box_content.split())
        else:
            return "".join(text_box_content.split("\n")[0].split())

    def get_make(self):
        POI = self.get_POI('.*policy details.*')

        s_temp1 = self.get_xy(poi=POI, text='Vehicle Details')
        s_temp2 = self.get_xy(poi=POI, text='Email ID')
        s_temp3 = self.get_xy(poi=POI, text='Policy No.')

        s1 = self.get_xy(poi=POI, text='Make',
                         clip=[s_temp2[0].x0, s_temp1[0].y1, s_temp3[0].x0, s_temp2[0].y1])
        # print(s1)
        text_box_content = POI.get_textbox([s1[0].x0, s1[0].y0 - 3, 9999, s1[0].y1 + 10])
        # print(text_box_content)
        text_box_content = text_box_content.replace("Make", "").strip()
        only_one_line = False
        if not "\n" in text_box_content:
            only_one_line = True
        if only_one_line:
            return "".join(text_box_content.split())
        else:
            return "".join(text_box_content.split("\n")[0].split())

    def get_model(self):
        POI = self.get_POI('.*policy details.*')

        s_temp1 = self.get_xy(poi=POI, text='Vehicle Details')
        s_temp2 = self.get_xy(poi=POI, text='Email ID')
        s_temp3 = self.get_xy(poi=POI, text='Policy No.')

        s1 = self.get_xy(poi=POI, text='Model',
                         clip=[s_temp2[0].x0, s_temp1[0].y1, s_temp3[0].x0, s_temp2[0].y1])
        text_box_content = POI.get_textbox([s1[0].x0, s1[0].y0 - 3, s_temp3[0].x0, s1[0].y1])
        text_box_content = text_box_content.replace("Model - Variant", "").strip()
        text_box_content = text_box_content.replace("Model", "").strip()
        only_one_line = False
        if not "\n" in text_box_content:
            only_one_line = True
        if only_one_line:
            return "".join(text_box_content.split())
        else:
            return "".join(text_box_content.split("\n")[0].split())

    def get_expiry(self):
        POI = self.get_POI('.*policy details.*')

        s_temp1 = self.get_xy(poi=POI, text='Policy Details')
        s_temp2 = self.get_xy(poi=POI, text='Issuance Date')
        s_temp3 = self.get_xy(poi=POI, text='Policy No.')

        # s1 = self.get_xy(poi=POI, text='Model',
        # clip=[s_temp2[0].x0, s_temp3[0].y1, s_temp2[0].x0, s_temp2[0].y1])
        text_box_content = POI.get_textbox([s_temp2[0].x0, s_temp3[0].y1 - 3, 9999, s_temp2[0].y1])
        # print(text_box_content)
        pattern = ".*To(.*)Midnight.*"

        for line in text_box_content.split('\n'):
            # print(line)
            m = re.match(pattern, line)
            if m is not None:
                return m.groups()[0]
        return None

    def get_price(self, pattern, page):
        Own_Damage_Dict = {}
        mode = 'Title'
        # pattern = '.*own\s*damage\s*premium.*'
        valuepattern = '[+-]?([0-9]*[.])?[0-9]+'
        currentTitle = None
        blocks = page.get_text("blocks")
        blocktextlist = []
        # blocks= POI.get_text("blocks",flags = fitz.fitz.TEXT_PRESERVE_LIGATURES | fitz.fitz.TEXT_PRESERVE_WHITESPACE)
        blocks.sort(key=lambda b: (b[3], b[0]))
        start_append = False
        for bl in blocks:
            # if 'premium' in bl[4].lower():
            # print(bl[4].lower())
            if not start_append:
                m = re.match('.*premium\s*details.*', bl[4].lower())
                if m is not None:
                    start_append = True
            if start_append and '<image' not in bl[4]:
                blocktextlist.extend(bl[4].replace(u'\xa0', u' ').strip().split("\n"))
        # print(blocktextlist)
        for line in blocktextlist:
            if mode == 'Title':
                m = re.match(pattern, line.lower())
                if m is not None:
                    currentTitle = line
                    mode = 'value'
            if mode == 'value':
                m = re.match(valuepattern, line.lower())
                if m is not None:
                    currentvalue = float(line.replace(',', ''))
                    key = currentTitle.strip().replace(u'\xa0', u' ')
                    while key in Own_Damage_Dict.keys():
                        key = key + "_"
                    Own_Damage_Dict[key] = currentvalue
                    mode = 'Title'
                else:
                    currentTitle = line
        return Own_Damage_Dict

    def get_od_amount(self, policy_type):
        insurance_type = None
        if policy_type is None:
            return 0.0
        else:
            insurance_type = policy_type.split("_")[1]

        if insurance_type == "TP":
            return 0.0
        POI = self.get_POI('.*policy details.*')
        tp_dict = self.get_price(".*net\s*own\s*damage\s*premium.*", POI)

        if len(tp_dict.keys()) != 0:
            return max(tp_dict.values())
        else:
            return None

    def get_tp_amount(self, policy_type):
        insurance_type = None
        if policy_type is None:
            return 0.0
        else:
            insurance_type = policy_type.split("_")[1]

        if insurance_type != "SOD":
            POI = self.get_POI('.*policy details.*')
            tp_dict = self.get_price(".*basic\s*third\s*party\s*liability.*", POI)

            if len(tp_dict.keys()) != 0:
                return max(tp_dict.values())
            else:
                return None
        else:
            return 0.0

    def get_final_amount(self):
        POI = self.get_POI('.*policy details.*')
        tp_dict = self.get_price(".*total\s*premium.*", POI)

        if len(tp_dict.keys()) != 0:
            return max(tp_dict.values())
        else:
            return None

    def get_net_amount(self, policy_type):
        POI = self.get_POI('.*policy details.*')
        net_amount_pattern = {
            "PVT_PKG": ".*total\s*package\s*premium.*",
            "PVT_SOD": ".*total\s*premium.*",
            "TW_TP": ".*net\s*liability\s*premium.*",
            "TW_PKG": ".*total\s*package\s*premium.*",
            "TW_SOD": ".*total\s*premium.*",
        }
        if policy_type in net_amount_pattern.keys():
            tp_dict = self.get_price(net_amount_pattern[policy_type], POI)
        else:
            print("Warning: Could not find net amount for the policy. You will see sero value")
            return 0.0

        if len(tp_dict.keys()) != 0:
            if "SOD" in policy_type:
                return min(tp_dict.values())
            return max(tp_dict.values())
        else:
            return None

    def get_code(self):
        POI = self.get_POI('.*proposal\s*no.*')
        s1 = self.get_xy(poi=POI, text='BROKER')
        text_box_content = None
        text_box_content = POI.get_textbox([s1[0].x0, s1[0].y0 - 3, 9999, s1[0].y1 + 3])
        text_box_content = text_box_content.upper()
        if 'BROKER CODE' in text_box_content:
            text_box_content = text_box_content[:text_box_content.index("BROKER CODE")]
        text_box_content = text_box_content.replace("BROKER NAME", "").strip()
        text_box_content = text_box_content.replace("BROKER :", "").strip()
        text_box_content = text_box_content.replace("BROKER :", "").strip()

        text_box_content = text_box_content.replace(":", "").strip()

        return text_box_content
