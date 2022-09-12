import re

Acronym_Map_BJ = {'BAJAJ': 'BAJAJ', 'TW': 'TWO WHEELER', 'PC': 'Private Car', 'COMM': "Passenger Carrying", 'TP': 'TP',
                  'PKG': 'Package', 'OD':'OD'}

INSURANCE_TYPE_OLD = {
    'BAJAJ_TW': ['transcript', 'two', 'wheeler'],
    'BAJAJ_PC': ['transcript', 'private', 'car'],
    'BAJAJ_COMM': ['transcript', 'commercial', 'vehicle', 'policy']
}
INSURANCE_TYPE_NEW = {
    'BAJAJ_TW': ['two', 'wheeler'],
    'BAJAJ_PC': ['private', 'car'],
    'BAJAJ_COMM': ['commercial', 'vehicle', 'policy']
}

POLICY_MAP = {
    'OLD': INSURANCE_TYPE_OLD,
    'NEW': INSURANCE_TYPE_NEW
}

OLD_VS_NEW = {
    'TW': ['TP'],
    'PC': ['TP'],
    'COMM': ['TP']
}


class BajajPolicy:
    def __init__(self, raw_data,file_path,logger):
        logger.setPlainText('Converting format for Bajaj')
        self.raw_data = raw_data
        self.raw_text = self._get_all_page_data()
        # print(self.raw_text)
        self.policy_version = self.checkifnew()
        self.insurance_type = self.get_insurance_type()
        print(self.checkifnew())
        print(self.get_insurance_type())
        self.get_all_policy_details()

    def checkifnew(self):
        if 'facebook' in self.raw_text:
            return 'NEW'
        return 'OLD'

    def _get_all_page_data(self):
        tmp_txt = ""
        for page in self.raw_data.pages:
            tmp_txt = tmp_txt + "\n" + self.get_good_text(page.extract_text(x_tolerance=1))
        return tmp_txt

    def get_good_text(self, xx):
        GoodTExt = ""
        for x in xx.split('\n'):
            if x != '' and x != '(cid:3)':  # merely to compact the output
                abc = re.findall(r'\(cid\:\d+\)', x)
                if len(abc) > 0:
                    for cid in abc: x = x.replace(cid, self.cidToChar(cid))

            GoodTExt += "\n" + repr(x).strip("'")
        return GoodTExt

    def cidToChar(self, cidx):
        return chr(int(re.findall(r'\(cid\:(\d+)\)', cidx)[0]) + 29)

    def get_insurance_type(self):

        for page in self.raw_data.pages:
            raw_text = page.extract_text(x_tolerance=1)
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                for policy_type, attrib in POLICY_MAP[self.policy_version].items():
                    check_list = set([attr in row for attr in attrib])
                    if len(check_list) == 1 and list(check_list)[0]:
                        if 'liability' in row:
                            policy_type = policy_type + "_TP"
                        elif 'PACKAGE POLICY' in row.upper():
                            policy_type = policy_type + "_PKG"
                        else:
                            policy_type = policy_type + "_OD"

                        if policy_type.split('_')[1]=='COMM':
                            m = re.match('.*Vehicle Type\s+(.*)',row.lower())
                            if m is not None:
                                use_string =m.groups()[0]
                                if 'passenger' in use_string.lower():
                                    vtype= 'Passanger Carrying'
                                else:
                                    if 'pubic' in use_string.lower():
                                        vtype = 'Goods - Public Carrier'
                                    else:
                                        vtype = 'Goods - PVT Carrier'
                                return Acronym_Map_BJ[policy_type.split('_')[0]],vtype,Acronym_Map_BJ[policy_type.split('_')[2]]
                        return Acronym_Map_BJ[policy_type.split('_')[0]], Acronym_Map_BJ[policy_type.split('_')[1]], \
                               Acronym_Map_BJ[policy_type.split('_')[2]]
        return None

    def get_all_policy_details(self):
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
            'R': None,
            'S': None,
            'T': None,
            'U': None,
            'V': None,
            'W': None,
            'X': None
        }
        if self.policy_version == "OLD":
            policy_obj = BAJAJ_OLD_POLCY(self.raw_data, self.raw_text, self.insurance_type)
            print('Customer Name is ', policy_obj.just_get_name())
            print('Customer Mobile Number is ', policy_obj.just_get_number())
            print('Expiry Date is ', policy_obj.get_expiry_date())
            print('Issue Date is ', policy_obj.get_policy_issue_date())
            print('Policy Number is ', policy_obj.get_policy_num())
            print('Make Info is below : ', policy_obj.get_registration_make())
            policy_obj.get_prices()
            data_dict['A'] = policy_obj.get_policy_issue_date()
            data_dict['B'] = policy_obj.just_get_name()
            data_dict['C'],data_dict['J'],data_dict['K'] = policy_obj.get_registration_make()
            data_dict['D'] = policy_obj.get_policy_num()
            data_dict['E'] = policy_obj.get_expiry_date()
            data_dict['F'] = policy_obj.just_get_number()
            if data_dict['F'].strip()!='NA':
                data_dict['F'] = int(data_dict['F'].replace('0-',''))
            data_dict['G'] = policy_obj.insurance_type[1]
            data_dict['H'] = policy_obj.insurance_type[2]
            data_dict['I'] = policy_obj.insurance_type[0]
            data_dict['L'],data_dict['M'],data_dict['N'],data_dict['O'] = policy_obj.get_prices()
            data_dict['Q'] = policy_obj.get_code()
        return data_dict

class BAJAJ_OLD_POLCY:
    def __init__(self, raw_data, raw_text, insurance_type):
        self.raw_data = raw_data
        self.raw_text = raw_text
        # print(self.raw_text)
        self.insurance_type = insurance_type

    def get_good_text(self, xx):
        GoodTExt = ""
        for x in xx.split('\n'):
            if x != '' and x != '(cid:3)':  # merely to compact the output
                abc = re.findall(r'\(cid\:\d+\)', x)
                if len(abc) > 0:
                    for cid in abc: x = x.replace(cid, self.cidToChar(cid))

            GoodTExt += "\n" + repr(x).strip("'")
        return GoodTExt

    def just_get_name(self):
        customer_name = None
        raw_text_list = self.raw_text.lower().split("\n")
        for row in raw_text_list:
            m = re.match("\d+.*proposer\s*name\s*:\s*(.*)", row.strip().lower())
            if m is not None:
                customer_name = m.groups()[0].strip().upper()
                return customer_name
        return None

    def cidToChar(self, cidx):
        return chr(int(re.findall(r'\(cid\:(\d+)\)', cidx)[0]) + 29)

    def just_get_number(self):
        customer_name = None
        raw_text_list = self.raw_text.lower().split("\n")
        for row in raw_text_list:
            m = re.match("\d+.*proposer\s*mobile\s*number\s*:\s*(.*)", row.strip().lower())
            if m is not None:
                customer_name = m.groups()[0].strip().upper()
                return customer_name
        return None

    def get_expiry_date(self):
        customer_name = None
        raw_text_list = self.raw_text.lower().split("\n")
        for row in raw_text_list:
            m = re.match(".*(\d{2}-[a-z]+-\d{4})\s*midnight.*", row.strip().lower())
            if m is not None:
                customer_name = m.groups()[0].strip().upper()
                return customer_name
        return None

    def get_policy_issue_date(self):
        customer_name = None
        raw_text_list = self.raw_text.lower().split("\n")
        for row in raw_text_list:
            m = re.match(".*policy\s*issued\s*on\s*(\d{2}-[a-z]+-\d{4}).*", row.strip().lower())
            if m is not None:
                customer_name = m.groups()[0].strip().upper()
                return customer_name
        return None

    def get_policy_num(self):
        customer_name = None
        raw_text_list = self.raw_text.lower().split("\n")
        for row in raw_text_list:
            m = re.match(".*policy\s*number\s*([a-z0-9-]+\d+).*", row.strip().lower())
            if m is not None:
                customer_name = m.groups()[0].strip().upper()
                return customer_name
        return None

    def get_clean_text(self, txt):
        return txt.replace('\n', ' ').replace('- ', '')

    def get_make_table(self):
        customer_name = None
        Make_Page = None
        for page in self.raw_data.pages:
            raw_text = self.get_good_text(page.extract_text(x_tolerance=1))
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                m = re.match("\d+.*proposer\s*name\s*:\s*(.*)", row.strip().lower())
                if m is not None:
                    Make_Page = page
                    print('Found page')
                    break
            if Make_Page is not None:
                break
        make_table = None
        if Make_Page is not None:
            page_tables = Make_Page.extract_tables({'text_x_tolerance': 1})

            for table in page_tables:
                # print(table)
                clean_table = []
                assign_table = False
                for row in table:
                    clean_row = [self.get_clean_text(data.upper()) for data in row]
                    clean_table.append(clean_row)
                    if 'REGISTRATION NUMBER' in clean_row:
                        assign_table = True
                if assign_table:
                    make_table = clean_table

            return make_table

    def get_table_row(self, tb, key):
        row_num = -1
        column_num = -1
        found = False
        values = None
        for row in tb:
            row_num += 1
            for cell in row:
                column_num += 1
                if key == cell.strip():
                    found = True
                    break
            if found:
                break
        if found:
            row_num_local = -1
            column_num_local = -1
            for row in tb:
                row_num_local += 1
                if row_num_local > row_num:
                    if row[column_num] != None:
                        value = row[column_num]
                        return value
        return None

    def get_registration_make(self):

        mk_table = self.get_make_table()
        if mk_table is not None:
            r_num = self.get_table_row(mk_table, 'REGISTRATION NUMBER')
            v_make = self.get_table_row(mk_table, 'VEHICLE MAKE')
            v_model = self.get_table_row(mk_table, 'VEHICLE MODEL')
            return r_num,v_make,v_model
        return None,None,None
    def get_code(self):
        code_pattern_1 = "generated\s*by\s*(.*)@general.*"
        code_pattern_2 = ".*\(web\)\s*\((.*)\).*"
        for page in self.raw_data.pages:
            raw_text = self.get_good_text(page.extract_text(x_tolerance=1))
            raw_text_list = raw_text.lower().split("\n")
            code=None
            for row in raw_text_list:
                m = re.match(code_pattern_1,row)
                n = re.match(code_pattern_2, row)

                if not m is None:
                    code= m.groups()[0]
                    return code
                elif not n is None:
                    code = n.groups()[0]
                    return code



    def get_price_table(self):
        customer_name = None
        price_Page = None
        for page in self.raw_data.pages:
            raw_text = page.extract_text(x_tolerance=1).upper()
            # raw_text_list = raw_text.lower().split("\n")
            if 'OWN DAMAGE' in raw_text and 'FINAL PREMIUM' in raw_text:
                price_Page = page
                break
        if price_Page is not None:
            sc_res = price_Page.search(".*(OWN Damage).*", regex=True, case=False, x_tolerance=1)
            if len(sc_res) != 0:
                top_y = sc_res[0]['top'] - 2 + sc_res[0]['top'] - sc_res[0]['bottom']
                x0 = 10
                if top_y + 150 < price_Page.height:
                    bottom_y = price_Page.height
                    # bottom_y = top_y + 150
                else:
                    bottom_y = price_Page.height
                x1 = price_Page.width
                new_page = price_Page.crop((x0, top_y, x1, bottom_y))
                tbls = new_page.extract_tables({'text_x_tolerance': 1})
                for tbl in tbls:
                    found_check_list = []
                    for row in tbl:
                        for cell in row:
                            if 'own damage' in str(cell).lower():
                                found_check_list.append(1)
                    if 1 in found_check_list:
                        clean_table = []
                        for row in tbl:
                            clean_row = [self.get_clean_text(str(data).upper()) for data in row]
                            clean_table.append(clean_row)
                        return clean_table
            return None

    def get_next_not_none(self,remaining_row):
        for cell in remaining_row:
            if cell.strip() != 'NONE':
                return cell
        return None

    def get_value_from_price_table(self,table,key,repeat=False):
        TotalValue = None
        for row in table:

            for cell_index, cell in enumerate(row):
                m= re.match(key,str(cell.strip()))
                if m is not None:
                    value = self.get_next_not_none(row[cell_index+1:])
                    if value is not None and len(value.strip())!=0:
                        if TotalValue is None:
                            TotalValue=0
                        TotalValue+=float(value.replace(',',''))
                        if repeat:
                            pass
                        else:
                            return TotalValue
        return TotalValue


    def get_prices(self):
        pc_table = self.get_price_table()
        if pc_table is not None:
            '''
            print('OD PRIMUIM ',self.get_value_from_price_table(pc_table,'.*OWN DAMAGE PREMIUM:*(?!\()'))
            print('TOTAL GST ', self.get_value_from_price_table(pc_table,'.*GST.*',True))
            print('Final Premium ', self.get_value_from_price_table(pc_table,'.*FINAL\s*PREMIUM.*'))
            print('TP Premium ', self.get_value_from_price_table(pc_table,'.*BASIC\s*THIRD\s*PARTY\s*LIABILITY.*'))

            '''
            ODP = self.get_value_from_price_table(pc_table, '.*OWN DAMAGE PREMIUM:*(?!\()')
            GST= self.get_value_from_price_table(pc_table, '.*GST.*', True)
            FP = self.get_value_from_price_table(pc_table, '.*FINAL\s*PREMIUM.*')
            TP = self.get_value_from_price_table(pc_table, '.*BASIC\s*THIRD\s*PARTY\s*LIABILITY.*')
            if TP is None:
                TP=0
            if ODP is None:
                ODP=0
            NetPremium = FP - GST
            return float(FP),float(TP),float(ODP),float(NetPremium)
        return None,None,None,None
