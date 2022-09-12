import re
import pdfplumber
class PlumReader:
    def __init__(self,file_path):
        self.file_path = file_path
        with pdfplumber.open(self.file_path) as pdf:
            self.raw_data = pdf
            self.raw_text = self._get_all_page_data()
            self.raw_data = None
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
