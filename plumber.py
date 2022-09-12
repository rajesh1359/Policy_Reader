import re, json
from datetime import datetime
from document_classifier import Classify
import FileReader

def convert_date_format(line):
    dateObj = None
    if re.match(r"^\d{4}(\d{2})\d{2}$", line):
        if int(re.match(r"^\d{4}(\d{2})\d{2}$", line).groups()[0]) < 12:
            dateObj = datetime.strptime(line, '%Y%m%d')
        else:
            dateObj = datetime.strptime(line, '%d%m%Y')
    elif re.match(r"^\d{1,2}/", line):
        dateObj = datetime.strptime(line, '%m/%d/%Y')
    elif re.match(r"^[a-z]{3}", line, re.IGNORECASE):
        dateObj = datetime.strptime(line, '%b %d %Y')
    elif re.match(r"^\d{1,2} [a-z]{3}", line, re.IGNORECASE):
        dateObj = datetime.strptime(line, '%d %b %Y')
    elif re.match(r"^\d{4}-\d{1,2}-\d{1,2}", line, re.IGNORECASE):
        dateObj = datetime.strptime(line, '%Y-%m-%d')
    elif re.match(r"^\d{1,2}-[a-z]+-\d{4}", line, re.IGNORECASE):
        dateObj = datetime.strptime(line, '%d-%b-%Y')
    elif re.match(r"^\d{1,2}-\d{1,2}-\d{4}", line, re.IGNORECASE):
        dateObj = datetime.strptime(line, '%d-%m-%Y')
    return dateObj.strftime('%d-%m-%Y')


Acronym_Map = {'DIGI': 'DIGIT', 'TW': 'TWO WHEELER', 'PC': 'Private Car', 'COMM': "Passenger Carrying",'GOODS': "Goods Carrying",'TP':'TP','PKG':'Package'}

INSURANCE_TYPE = {
    'DIGI_TW': ['digit', 'two', 'wheeler', 'policy'],
    'DIGI_PC': ['digit', 'private', 'car', 'policy'],
    'DIGI_COMM': ['digit', 'commercial', 'passenger', 'policy'],
    'DIGI_GOODS': ['digit', 'commercial', 'goods', 'policy']
}


class Digit_RickShaw:
    def __init__(self, raw_data,pdf_path):
        self.pdf_path = pdf_path
        self.raw_data = raw_data
        self.raw_text = self._get_all_page_data()
        self.json_data = json.load(open("res/policy_class_helper.json", 'r'))

    def _get_all_page_data(self):
        tmp_txt = ""
        for page in self.raw_data.pages:
            tmp_txt = tmp_txt + "\n" + page.extract_text()
        return tmp_txt

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
            if len(set(match_list)) == 1:
                return policy

        return "Unknown"

    def get_customer_name(self):
        found_name = False
        customer_name = None
        registration_num = None
        name_pattern = ".*name(.*)vehicle registration no.\s([a-z0-9]+)\s*.*"
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                match = re.match(name_pattern, row)
                if match is not None:
                    found_name == True
                    customer_name = match.groups()[0].strip().upper()
                    registration_num = match.groups()[1].strip().upper()
                    return customer_name, registration_num
                    break
            if found_name:
                break

        if not found_name:
            registration_num = self.just_get_registrations()
            customer_name = self.just_get_name()

        return customer_name, registration_num

    def just_get_name(self):
        customer_name = None
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                if 'name' in row:
                    if 'partner' in row:
                        p_in = row.index('partner')
                        rw = row[:p_in]
                    else:
                        rw = row
                    m = re.match(".*name:(.*)", rw)
                    if m is not None:
                        customer_name = m.groups()[0].strip().upper()
                        return customer_name
        return None

    def just_get_number(self):
        customer_name = None
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                if 'mobile' in row:
                    if 'partner' in row:
                        p_in = row.index('partner')
                        rw = row[:p_in]
                    else:
                        rw = row
                    m = re.match(".*mobile.*:(.*)", rw)
                    if m is not None:
                        customer_name = m.groups()[0].strip().upper()
                        return customer_name
        return None

    def just_get_registrations(self):
        customer_name = None
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                if 'registration' in row:
                    if 'partner' in row:
                        p_in = row.index('partner')
                        rw = row[:p_in]
                    else:
                        rw = row
                    m = re.match(".*registration.*:(.*)", rw)
                    if m is not None:
                        customer_name = m.groups()[0].strip().upper()
                        return customer_name
        return None

    def get_policy_num(self):
        found_policy = False
        policy_num = None
        invoice_date = None
        policy_pattern = ".*policy no.\s+([a-z0-9]+)\s*/\s*(\d{8})\s*.*"
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                match = re.match(policy_pattern, row)
                if match is not None and 'previous' not in row:
                    found_policy = True
                    # print(row)
                    policy_num = match.groups()[0].strip().upper()
                    # print(match.groups())
                    invoice_date = convert_date_format(match.groups()[1].strip().upper())

                    break
            if found_policy:
                break
        if not found_policy:
            policy_pattern = ".*policy no:\s+([a-z0-9]+)\s*.*"
            for page in self.raw_data.pages:
                raw_text = page.extract_text()
                raw_text_list = raw_text.lower().split("\n")
                for row in raw_text_list:
                    match = re.match(policy_pattern, row)
                    if match is not None and 'previous' not in row:
                        found_policy == True
                        # print(row)
                        policy_num = match.groups()[0].strip().upper()
                        invoice_date = self.get_invoice_date()

                        break
                if found_policy:
                    break

        return policy_num, invoice_date

    def get_invoice_date(self):
        found_invoice_date = False
        invoice_date = None
        policy_pattern = ".*invoice number invoice date gross premium.*"
        check_invoice = False
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                if found_invoice_date:
                    break
                if not check_invoice:
                    match = re.match(policy_pattern, row)
                    if match is not None:
                        check_invoice = True
                        # print("header found")
                else:
                    split_row = row.split()
                    # print("Checking the invoice ", len(split_row))

                    if len(split_row) == 9:
                        found_invoice_date = True
                        invoice_date = convert_date_format(split_row[1])
                        # convert_date_format()
                        check_invoice = False
                        break

            if found_invoice_date:
                break

        return invoice_date

    def get_policy_expiry(self):
        found_policy_expiry = False
        policy_expiry = None
        expiry_pattern = ".*period of policy to\s*(\d{2}-[a-z]{3,4}-\d{4})\s*(\d{2}:\d{2}:\d{2}).*"
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                match = re.match(expiry_pattern, row)
                if match is not None:
                    found_policy_expiry = True
                    policy_expiry = match.groups()[0].strip().upper()

                    break
            if found_policy_expiry:
                break
        if not found_policy_expiry:
            check_next = False
            for page in self.raw_data.pages:
                raw_text = page.extract_text()
                raw_text_list = raw_text.lower().split("\n")
                for row in raw_text_list:
                    if not check_next:
                        if 'period of policy' in row:
                            check_next = True
                    else:
                        expiry_pattern = 'to\s*(\d{2}-[a-z]{3,4}-\d{4})\s*(\d{2}:\d{2}:\d{2}).*'
                        match = re.match(expiry_pattern, row)
                        if match is not None:
                            found_policy_expiry = True
                            policy_expiry = match.groups()[0].strip().upper()

                            break
                if found_policy_expiry:
                    break
        if policy_expiry is None:
            rd = FileReader.Digit(self.pdf_path)

            prem = rd.get_policy_expiry()
            if prem is not None:
                return prem
        return policy_expiry

    def get_mobile_num(self):
        found_number = False
        customer_number = None
        name_pattern = "(.*mobile\s*)([a-x0-9]{10})\s*"

        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                match = re.match(name_pattern, row)
                if match is not None:
                    found_number == True
                    customer_number = match.groups()[1].strip().upper()
                    return customer_number
                    break
            if found_number:
                break
        if not found_number:
            customer_number = self.just_get_number()

        return customer_number

    def get_insurance_type(self):

        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                for policy_type, attrib in INSURANCE_TYPE.items():
                    check_list = set([attr in row for attr in attrib])
                    if len(check_list) == 1 and list(check_list)[0]:
                        if 'liability' in row:
                            policy_type = policy_type + "_TP"
                        else:
                            policy_type = policy_type + "_PKG"

                        return Acronym_Map[policy_type.split('_')[0]],Acronym_Map[policy_type.split('_')[1]],Acronym_Map[policy_type.split('_')[2]]
        return None

    def get_make(self):

        # make = None
        make = None
        tpd = FileReader.Digit(self.pdf_path)
        make = tpd.get_make()
        if make is not None:
            return make
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.split("\n")
            for row in raw_text_list:
                if 'Make' in row:
                    if 'Model' in row:
                        p_in = row.index('Model')
                        row = row[:p_in]
                    elif 'Trailer' in row:
                        p_in = row.index('Trailer')
                        row = row[:p_in]
                    elif 'Vehicle' in row:
                        # print('Reached here........')
                        # print(row)
                        rw = row.split()
                        row = ""
                        for im in rw:
                            if 'Vehicle' in im:
                                break
                            else:
                                row = row + " " + im
                    elif 'Variant' in row:
                        # print('Reached here........')
                        # print(row)
                        rw = row.split()
                        row = ""
                        for im in rw:
                            if 'Variant' in im:
                                break
                            else:
                                row = row + " " + im
                        # temp_match=re.match("(.*)([^\s])/Vehicle.*",row)
                        # if temp_match is not None:
                        # row = temp_match.groups()[0]
                    else:
                        pass

                    m = re.match('.*Make\s*(.*)', row)
                    if m is not None:
                        make = m.groups()[0].strip().upper()
                        return make
        return make

    def get_model(self):
        # model = None
        model = None
        tpd = FileReader.Digit(self.pdf_path)
        model = tpd.get_model()
        if model is not None:
            return model
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.split("\n")
            for row in raw_text_list:
                if re.match(".*Model/*.*\s([^\s]+)/.*", row) is not None:
                    # print(row)
                    return re.match(".*Model/*.*\s([^\s]+)/.*", row).groups()[0]
                elif re.match(".*Variant.*\s+([^\s]+)/.*", row) is not None:
                    # print(row)
                    return re.match(".*Variant.*\s+([^\s]+)/.*", row).groups()[0]

        return None

    def get_final_premium(self):
        final_premium = None
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                match = re.match(".*final premium.*\(.*\).*\s+([+-]?([0-9]*[.])?[0-9]+).*", row)
                if match is not None:
                    return match.groups()[0]
                else:
                    match = re.match(".*total premium.*\(.*\).*\s+([+-]?([0-9]*[.])?[0-9]+).*", row)
                    if match is not None:
                        return match.groups()[0]

        rd = FileReader.Digit(self.pdf_path)

        prem = rd.get_final_premium()

        if prem is not None:
            return prem
        return None

    def get_net_premium(self):
        TP_Price = None
        tpd =  FileReader.Digit(self.pdf_path)
        TP_Price = tpd.get_net_premium()
        if TP_Price is not None:
            return TP_Price

        final_premium = None
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                match = re.match(".*net premium.*\s*\(.*\).*\s+([+-]?([0-9]*[.])?[0-9]+).*", row)
                if match is not None:
                    print(row)
                    return re.findall("[-+]?\d*\.\d+|\d+", row)[0]
                else:
                    match = re.match(".*total premium\s*\(.*\).*\s+([+-]?([0-9]*[.])?[0-9]+).*", row)
                    print(row)
                    if match is not None:
                        return re.findall(r"[-+]?\d*\.\d+|\d+", row)[0]
        return None

    def get_code(self):
        TP_Price = None
        tpd = FileReader.Digit(self.pdf_path)
        TP_Price = tpd.get_partner_name()
        if TP_Price is not None:
            return TP_Price

    def get_payout(self):
        insurance = self.get_insurance_type()
        if insurance is not None:
            if insurance[1]=="TWO WHEELER" and insurance[2]=="TP":
                return "O"
            if insurance[1]=="TWO WHEELER":
                return 'N'
            if insurance[1]=="Private Car" and insurance[2]=="TP":
                return "O"
            if insurance[1]=="Private Car":
                return "O"

        return "O"



    def get_od_premium_old(self):
        final_premium = None
        insurance= self.get_insurance_type()[2]
        if insurance=='TP':
            return '0'
        for page in self.raw_data.pages:
            raw_text = page.extract_text()
            raw_text_list = raw_text.lower().split("\n")
            for row in raw_text_list:
                match = re.match(".*od premium.*\s*\(.*\).*\s+([+-]?([0-9]*[.])?[0-9]+).*", row)
                if match is not None:
                    #return match.groups()[0]
                    all_floats=re.findall(r"[-+]?\d*\.\d+", row)
                    stub_end=row.index('od premium') + len('od premium')
                    closest_float=None
                    smallest_index= None
                    for each_float in all_floats:
                        if row.index(each_float) - stub_end > 0:
                            if closest_float is None:
                                closest_float=each_float
                                smallest_index=row.index(each_float)
                            else:
                                if row.index(each_float) < smallest_index:
                                    smallest_index = row.index(each_float)
                                    closest_float = each_float
                    return closest_float

                else:
                    match = re.match(".*total premium\s*\(.*\).*\s+([+-]?([0-9]*[.])?[0-9]+).*", row)
                    if match is not None:
                        return match.groups()[0]
        return None
    def get_tp_premium(self):

        rd = FileReader.Digit(self.pdf_path)
        insurance = self.get_insurance_type()[2]
        prem = rd.get_tp_premium(Policy_Type=insurance)

        if prem is not None:
            return prem

    def get_od_premium(self):
        final_premium = None
        insurance = self.get_insurance_type()[2]
        if insurance == 'TP':
            return '0'

        rd = FileReader.Digit(self.pdf_path)

        prem = rd.get_od_premium()

        if prem is not None:
            return prem[0]
