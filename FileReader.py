from typing import List, Any

import fitz
import re

class Reader:
    def __init__(self, pdf_file):
        self.doc = fitz.Document(pdf_file)
def make_text(words):
    """Return textstring output of get_text("words").

    Word items are sorted for reading sequence left to right,
    top to bottom.
    """
    line_dict = {}  # key: vertical coordinate, value: list of words
    words.sort(key=lambda w: w[0])  # sort by horizontal coordinate
    for w in words:  # fill the line dictionary
        y1 = round(w[3], 1)  # bottom of a word: don't be too picky!
        word = w[4]  # the text of the word
        line = line_dict.get(y1, [])  # read current line content
        line.append(word)  # append new word
        line_dict[y1] = line  # write back to dict
    lines = list(line_dict.items())
    lines.sort()  # sort vertically
    return "\n".join([" ".join(line[1]) for line in lines])

class Digit:

    def __init__(self, pdf_file):
        self.pdf_file = pdf_file
        self.pdf_reader = Reader(pdf_file)
        self.doc= self.pdf_reader.doc

    def get_POI(self, pattern):
        POI = None
        code = None
        agent_code = None
        for page in self.doc.pages():
            blocks = page.get_text("blocks")
            for line in blocks:
                # page_text = page.get_text()

                m = re.match(pattern, (" ".join(line[4].split())).lower())
                if m is not None:
                    POI = page
                    # print('found')
                    break
            if POI is not None:
                break
        return POI

    def get_tp_premium(self,Policy_Type):
        if Policy_Type !='TP':

            od_return = self.get_od_premium()
            if od_return is not None:
                if len(od_return)==2:
                    return od_return[1]
        if self.doc.is_closed:
            self.pdf_reader = Reader(self.pdf_file)
            self.doc = self.pdf_reader.doc
        page = self.get_POI(".*Basic\s+Third.*".lower())
        blocks = page.get_text("blocks")

        blocktextlist = []
        txt = page.get_text()
        # blocks= POI.get_text("blocks",flags = fitz.fitz.TEXT_PRESERVE_LIGATURES | fitz.fitz.TEXT_PRESERVE_WHITESPACE)
        blocks.sort(key=lambda b: (b[3], b[0]))
        if Policy_Type != 'TP':
            s1 = (page.search_for('Total Act'))[0]
        else:
            s1 = (page.search_for('Basic Third'))[0]
        lst = [txt[4] for txt in blocks]

        lst = [txt[4] for txt in blocks]
        # print(" ".join(page.get_textbox([s1.x0, s1.y0-1, 9999, s1.y1]).split()))

        words = page.get_text("words")
        words.sort(key=lambda w: w[0])
        mywords = [w for w in words if
                   fitz.Rect(w[:4]).intersects(fitz.Rect(s1.x0, s1.y0 - 5, 9999, s1.y1)) and w[1] > s1.y0 - 5]
        # print(mywords)
        # print(s1.x0, s1.y0)
        ws = [w[4].replace(u"\xa0", u" ") for w in mywords]
        # print(ws)
        regnum = " ".join(ws)
        print(regnum)
        m = re.findall(r"[-+]?\d*\.\d+|\d+", regnum)
        self.doc.close()
        if m is not None:
            return m[0]


    def get_od_premium(self):
        page =  self.get_POI(".*total\s+od.*".lower())
        blocks = page.get_text("blocks")
        blocktextlist = []
        txt = page.get_text()
        # blocks= POI.get_text("blocks",flags = fitz.fitz.TEXT_PRESERVE_LIGATURES | fitz.fitz.TEXT_PRESERVE_WHITESPACE)
        blocks.sort(key=lambda b: (b[3], b[0]))
        s1 = (page.search_for('Total OD'))[0]
        lst = [txt[4] for txt in blocks]
        #print(" ".join(page.get_textbox([s1.x0, s1.y0-1, 9999, s1.y1]).split()))

        words = page.get_text("words")
        words.sort(key=lambda w: w[0])
        mywords = [w for w in words if fitz.Rect(w[:4]).intersects(fitz.Rect(s1.x0, s1.y0-1, 9999, s1.y1)) and w[1] > s1.y0-1]
        #print(mywords)
        #print(s1.x0, s1.y0)
        ws = [w[4].replace(u"\xa0", u" ") for w in mywords]
        #print(ws)
        regnum = " ".join(ws)

        print(regnum)
        m= re.findall(r"[-+]?\d*\.\d+|\d+", regnum)
        self.doc.close()
        if len(m)!=0:
            print(m)
            return m

    def get_final_premium(self):
        page = self.get_POI(".*BASIC\s*Third-Party.*".lower())
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[3], b[0]))
        s1 = page.search_for('Final Premium')
        if len(s1)!=0:
            s1 = s1[0]
            pass
        else:
            s1 = page.search_for('Total Premium')
            s1 = s1[0]


            # return s1
        words = page.get_text("words")
        words.sort(key=lambda w: w[0])
        mywords = [w for w in words if
                   fitz.Rect(w[:4]).intersects(fitz.Rect(s1.x0, s1.y0 - 5, 9999, s1.y1)) and w[1] > s1.y0 - 5]
        # print(mywords)
        # print(s1.x0, s1.y0)
        ws = [w[4].replace(u"\xa0", u" ") for w in mywords]
        # print(ws)
        regnum = " ".join(ws)

        #print(regnum)
        m = re.findall(r"[-+]?\d*\.\d+|\d+", regnum)
        self.doc.close()
        if len(m)!=0:
            #print(m)
            return m[0]

    def get_net_premium(self):
        page = self.get_POI(".*BASIC\s*Third-Party.*".lower())
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[0], b[3]))
        s1 = page.search_for('Net Premium')
        if len(s1) != 0:
            s1 = s1[0]
        no_period = True
        for bl in blocks:
            #print(bl)
            if "Net Premium" in bl[4].strip() and bl[:4][0] < 60:
                print(bl)
                s1.x0 = bl[:4][0]
                s1.y0 = bl[:4][1]
                s1.x1 = bl[:4][2]
                s1.y1 = bl[:4][3]
                no_period = False
                break


            # return s1
        words = page.get_text("words")
        words.sort(key=lambda w: w[0])
        mywords = [w for w in words if
                   fitz.Rect(w[:4]).intersects(fitz.Rect(s1.x0, s1.y0 - 5, 9999, s1.y1)) and w[1] > s1.y0 - 5]
        # print(mywords)
        # print(s1.x0, s1.y0)
        ws = [w[4].replace(u"\xa0", u" ") for w in mywords]
        # print(ws)
        regnum = " ".join(ws)

        # print(regnum)
        m = re.findall(r"[-+]?\d*\.\d+|\d+", regnum)
        self.doc.close()
        if len(m)!=0:
            # print(m)
            return m[0]
    def get_policy_expiry(self):
        page = self.get_POI(".*YOUR\s*POLICY\s*DETAILS*".lower())
        blocks = page.get_text("blocks")

        blocktextlist = []
        txt = page.get_text()
        # blocks= POI.get_text("blocks",flags = fitz.fitz.TEXT_PRESERVE_LIGATURES | fitz.fitz.TEXT_PRESERVE_WHITESPACE)
        blocks.sort(key=lambda b: (b[3], b[0]))
        s1 = (page.search_for('Period of Policy'))[0]
        lst = [txt[4] for txt in blocks]

        lst = [txt[4] for txt in blocks]
        no_period = True
        for bl in blocks:
            if "Period of Policy"==bl[4].strip():
                print(bl)
                s1.x0 = bl[:4][0]
                s1.y0 = bl[:4][1]
                s1.x1 = bl[:4][2]
                s1.y1 = bl[:4][3]
                no_period = False
                break
        if no_period:
            words = page.get_text("words")
            words.sort(key=lambda w: w[0])
            mywords = [w for w in words if
                       fitz.Rect(w[:4]).intersects(fitz.Rect(s1.x0, s1.y1 +1, 9999, s1.y1+ 30))]
            for w in mywords:

                if 'To' == w[4].strip():
                    s1.x0 = w[:4][0]
                    s1.y0 = w[:4][1]
                    s1.x1 = w[:4][2]
                    s1.y1 = w[:4][3]
        # print(lst)
        # print(" ".join(page.get_textbox([s1.x0, s1.y0-1, 9999, s1.y1]).split()))

        words = page.get_text("words")
        words.sort(key=lambda w: w[0])
        mywords = [w for w in words if
                   fitz.Rect(w[:4]).intersects(fitz.Rect(s1.x0, s1.y0 - 1, 9999, s1.y1)) and w[1] > s1.y0 - 1]
        # print(mywords)
        # print(s1.x0, s1.y0)
        ws = [w[4].replace(u"\xa0", u" ") for w in mywords]
        # print(ws)
        regnum = " ".join(ws)
        print(regnum)
        m = re.findall(r"\d{2}-[a-z]{3,4}-\d{4}\s*\d{2}:\d{2}:\d{2}", regnum)
        self.doc.close()

        if len(m)!=0:
            return m
        else:
            expiry_pattern = '.*to\s*(\d{2}-[a-z]{3,4}-\d{4})\s*(\d{2}:\d{2}:\d{2}).*'
            match = re.match(expiry_pattern, regnum.lower())
            if match is not None:
                return match.groups()[0].strip().upper()

    def has_numbers(self,inputString):
        return any(char.isdigit() for char in inputString)

    def def_get_make(self):
        page = self.get_POI(".*RTO\s*Location.*".lower())
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[3], b[0]))
        s1 = page.search_for('Make')
        if len(s1) != 0:
            s1 = s1[0]

            # return s1
        words = page.get_text("words")
        words.sort(key=lambda w: w[0])
        mywords = [w for w in words if
                   fitz.Rect(w[:4]).intersects(fitz.Rect(s1.x0, s1.y0 - 5, s1.x0 + 400, s1.y1)) and
                               (w[1] > s1.y0 - 5 and w[3] < s1.y1 + 5)]
        # print(mywords)
        # print(s1.x0, s1.y0)
        ws = [w[4].replace(u"\xa0", u" ") for w in mywords]
        print(ws)
        regnum = " ".join(ws)

        # print(regnum)
        # m = re.findall(r"[-+]?\d*\.\d+|\d+", regnum)
        self.doc.close()
        return ws[1]

    def get_make(self):
        page = self.get_POI(".*RTO\s*Location.*".lower())
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[3], b[0]))
        s1 = page.search_for('Make')
        if len(s1) != 0:
            s1 = s1[0]

            # return s1
        words = page.get_text("words")
        words.sort(key=lambda w: w[0])
        mywords = [w for w in words if
                   fitz.Rect(w[:4]).intersects(fitz.Rect(s1.x0, s1.y0 - 5, s1.x0 + 400, s1.y1)) and
                               (w[1] > s1.y0 - 5 and w[3] < s1.y1 + 5)]
        # print(mywords)
        # print(s1.x0, s1.y0)
        ws = [w[4].replace(u"\xa0", u" ") for w in mywords]
        print(ws)
        regnum = " ".join(ws)

        # print(regnum)
        # m = re.findall(r"[-+]?\d*\.\d+|\d+", regnum)
        self.doc.close()
        return ws[1]

    def flags_decomposer(self,flags):
        """Make font flags human readable."""
        l = []
        if flags & 2 ** 0:
            l.append("superscript")
        if flags & 2 ** 1:
            l.append("italic")
        if flags & 2 ** 2:
            l.append("serifed")
        else:
            l.append("sans")
        if flags & 2 ** 3:
            l.append("monospaced")
        else:
            l.append("proportional")
        if flags & 2 ** 4:
            l.append("bold")
        return ", ".join(l)
    def get_model(self):
        page = self.get_POI(".*RTO\s*Location.*".lower())
        blocks = page.get_text("dict", flags=11)["blocks"]

        s1 = page.search_for('Model/Vehicle')
        if len(s1) != 0:
            s1 = s1[0]
            if s1.x0 < page.rect[3]*0.20:
                #print('left')
                s1.x0 = 0
                s1.y0 = s1.y0-2
                s1.x1 = page.rect[3]*0.20
                s1.y1 = s1.y1+2
            else:
                #print('right')
                s1.x0 = s1.x0-2
                s1.y0 = s1.y0 - 2
                s1.x1 = page.rect[3]
                s1.y1 = s1.y1 + 10*(s1.x0/page.rect[3])
        #print(s1)
        #print(page.rect[3])
        #print(s1.x1)
        wrds = []
        for b in blocks:  # iterate through the text blocks
            for l in b["lines"]:  # iterate through the text lines
                for s in l["spans"]:  # iterate through the text spans
                    #print(s['text'])
                    if fitz.Rect([s1.x0, s1.y0, s1.x1, s1.y1]).intersects(fitz.Rect(s['origin'][0], s['origin'][1],s['bbox'][2]+2, s['bbox'][3]+2)):
                        wrds.append(s["text"])

        #print(wrds)
        pgnum=" ".join(wrds)
        repl_list=['Model/Vehicle','Variant','(','-',')','Sub','Type']
        for rp in repl_list:
            pgnum = pgnum.replace(rp,"")
        return pgnum
                    # print("Text: '%s'" % s["text"])  # simple print of text
                    # print(font_properties)

    def get_partner_name(self):
        page = self.get_POI(".*Partner\s*Name.*".lower())
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[3], b[0]))
        s1 = page.search_for('Partner Name')
        if len(s1) != 0:
            s1 = s1[0]

            # return s1
        words = page.get_text("words")
        words.sort(key=lambda w: w[0])
        mywords = [w for w in words if
                   fitz.Rect(w[:4]).intersects(fitz.Rect(s1.x0, s1.y0 - 10, s1.x0 + 400, s1.y1)) and ((w[1] > s1.y0 - 10 and w[3] < s1.y1+5) and not self.has_numbers(w[4]))]
        # print(mywords)
        # print(s1.x0, s1.y0)
        ws = [w[4].replace(u"\xa0", u" ") for w in mywords]
        # print(ws)
        print(ws)
        regnum = " ".join(ws)

        # print(regnum)
        # m = re.findall(r"[-+]?\d*\.\d+|\d+", regnum)
        regnum = regnum.replace("Partner Name","").strip()
        regnum = regnum.replace(":","").strip()
        regnum = regnum.replace("Vehicle","").strip()
        regnum = regnum.replace("Registration","").strip()
        regnum = regnum.replace("No.","").strip()
        self.doc.close()
        return regnum
        # if len(m) != 0:
            # print(m)
            # return m[0]



#
# import os
# for file in os.listdir(r'E:\NewDownloads\DemoDownloads\tata policy\digit'):
#
#     print("File Name ",file)
#     rd=Digit(os.path.join(r'E:\NewDownloads\DemoDownloads\tata policy\digit',file))
#     print(rd.get_tp_premium())