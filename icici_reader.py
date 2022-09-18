import fitz
import re
import json
import helper

icici_Policy_Map = {
    'OD': [['damage'], []],
    'TP': [['liability', 'only'], ['damage']],
    'Package': [['package'], ['liability']]
}

policy_map = {
    "COMM_PKG_GOODS": ["Goods Carrying Vehicles Package Policy"],
    "COMM_PKG_PSG": ["Passenger Carrying Vehicles Package Policy"],
    "PVT_PKG": ["Private Car Package Policy"],
    "PVT_SOD": ["Stand-Alone Own Damage Private Car Insurance Policy"],
    "TW_PKG": ["Two Wheeler Vehicles Package Policy"],
    "TW_TP": ["Two Wheeler Vehicles Liability Policy"],
    "TW_SOD": ["Stand-Alone Own Damage Two wheeler Insurance Policy"],
    "MISC_TP": ["Miscellaneous Vehicles Liability Policy"],
}


class ICICI:
    def __init__(self, pdf_file):
        self.doc = fitz.Document(pdf_file)
        self.policy_version = None
        self.policy_type = None
        self.main_page_table = self.get_main_page_table()

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
        '''
        This is the main function going be call in the master file.
        It will be used to assemble to information from various functions
        :return:
        '''
        policy_type = self.get_policy_type()
        print(policy_type)
        print(self.get_insured_name(policy_type))
        print(self.get_registration_no(policy_type))
        print(self.get_make_model(policy_type))
        print(self.get_insurance_period(policy_type))
        print(self.get_policy_number(policy_type))
        print("TP Amount is ", self.get_tp_amount(policy_type))
        print("OD Amount is ", self.get_od_amount(policy_type))
        print("Total Amount is ", self.get_total_amount(policy_type))
        print("Tax Amount is ", self.get_tax(policy_type))

    def get_policy_type(self):
        '''
        This function is to get the policy type based on the identifiers provided
         in dictionary POLICY_MAP.


        :return:
        '''
        policy_type_string = None

        # Getting page of interest
        POI = self.get_POI('.*servicing\s*branch.*')

        # Using a string to get definite location of the data located relative to it.

        if POI is not None:

            for tp, st in policy_map.items():
                for label in st:
                    search1 = POI.search_for(label, hit_max=1)
                    if search1:
                        return tp

        return policy_type_string

    def get_main_page_table(self):
        y_tolerance = 1  # Tolerance to start a new row

        # Getting page of interest
        words_rows = []
        POI = self.get_POI('.*sub:.*')
        if POI is not None:
            rect_1 = helper.get_xy(poi=POI, text='Vehicle Details')
            rect_2 = helper.get_xy(poi=POI, text='Chassis')

            words = POI.get_text("words", clip=[0, rect_1[0].y1, 9999, rect_2[0].y0])
            words_rows = helper.make_text_rows(words)
        return words_rows

    def get_value_from_main_table(self,key):
        main_table = self.main_page_table
        # print(main_table)
        lower_key = key.lower()
        for row in main_table:
            lower_row = row.lower()
            if lower_key in lower_row:
                remain_text = lower_row.replace(lower_key,"")
                return remain_text.strip().upper()
        return ""

    def get_insured_name(self, policy_type):

        if 'PVT' not in policy_type:
            return self.get_value_from_main_table("Name of Insured")

    def get_registration_no(self,policy_type):

        if 'PVT' not in policy_type:
            return self.get_value_from_main_table("Vehicle Registration No.")

    def get_make_model(self,policy_type):
        make = None
        model = None
        if 'PVT' not in policy_type:

            make_model = self.get_value_from_main_table("Vehicle Make / Model").strip()
            if len(make_model)!=0:
                division = make_model.split("/")
                if len(division)>1:
                    make = division[0].strip()
                    model = division[1].strip()
                else:
                    make = division[0].strip()
                    model = division[0].strip()
        return make,model

    def get_insurance_period(self,policy_type):
        start = None
        end = None
        if 'PVT' not in policy_type:

            insurance_period = self.get_value_from_main_table("Period of Insurance").strip()
            if len(insurance_period)!=0:
                division = insurance_period.split("TO")
                if len(division)>1:
                    start = division[0].strip()
                    end = division[1].strip()
                else:
                    start = division[0].strip()
                    end = division[0].strip()
        return start,end

    def get_policy_number(self,policy_type):
        if 'PVT' in policy_type:
            return None
        POI = self.get_POI('.*servicing\s*branch.*')
        key = 'policy no'
        s_temp1 = helper.get_xy(poi=POI, text='Policy No')
        s_temp2 = helper.get_xy(poi=POI, text='Servicing Branch')
        words = POI.get_text("words", clip=[s_temp1[0].x0, s_temp1[0].y0-2, 9999, s_temp2[0].y0])
        words_rows = helper.make_text_rows(words)
        for row in words_rows:
            lower_row  = row.lower()
            if key in lower_row:
                return lower_row[lower_row.index("no")+2:].replace(":","").strip()
        return None

    def get_tp_amount(self,policy_type):
        insurance_type = None
        if policy_type is None or 'PVT' in policy_type:
            return 0.0
        else:
            insurance_type = policy_type.split("_")[1]

        if insurance_type != "SOD":
            POI = self.get_POI('.*servicing\s*branch.*')
            tp_dict = helper.get_price(".*total\s*liability\s*premium.*", POI)

            if len(tp_dict.keys()) != 0:
                return max(tp_dict.values())
            else:
                return None
        else:
            return 0.0

    def get_od_amount(self, policy_type):
        insurance_type = None
        if policy_type is None or 'PVT' in policy_type:
            return 0.0
        else:
            insurance_type = policy_type.split("_")[1]

        if insurance_type == "TP":
            return 0.0
        POI = self.get_POI('.*servicing\s*branch.*')
        tp_dict = helper.get_price(".*total\s*own\s*damage\s*premium.*", POI)

        if len(tp_dict.keys()) != 0:
            return max(tp_dict.values())
        else:
            return None

    def get_tax(self,policy_type):
        insurance_type = None
        if policy_type is None or 'PVT' in policy_type:
            return 0.0
        else:
            insurance_type = policy_type.split("_")[1]

        POI = self.get_POI('.*servicing\s*branch.*')
        tp_dict = helper.get_price(".*total\s*tax\s*payable.*", POI)

        if len(tp_dict.keys()) != 0:
            return max(tp_dict.values())
        else:
            return None
    def get_total_amount(self, policy_type):
        insurance_type = None
        if policy_type is None or 'PVT' in policy_type:
            return 0.0
        else:
            insurance_type = policy_type.split("_")[1]

        POI = self.get_POI('.*servicing\s*branch.*')
        tp_dict = helper.get_price(".*total\s*premium\s*payable.*", POI)

        if len(tp_dict.keys()) != 0:
            return max(tp_dict.values())
        else:
            return None
# file_name = r"E:\NewDownloads\DemoDownloads\tata policy\icici\Goods_Carrying_Commercial.pdf"
# obj = ICICI(pdf_file=file_name)
# print(obj.get_policy_type())
