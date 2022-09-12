from pdf2docx import parse
from pdf2docx import Converter
from typing import Tuple


class PdfWordConverter:

    def __init__(self, input_dpf_file):
        self.input_pdf_file = input_dpf_file
        self.output_docx_file = input_dpf_file[:-4] + '.docx'  # temporary

    def __convert_pdf2docx(self, input_file: str, output_file: str, pages: Tuple = None):
        """Converts pdf to docx"""
        if pages:
            pages = [int(i) for i in list(pages) if i.isnumeric()]
        result = parse(pdf_file=input_file,
                       docx_with_path=output_file, pages=pages)
        summary = {
            "File": input_file, "Pages": str(pages), "Output File": output_file
        }
        # Printing Summary
        print("## Summary ########################################################")
        print("\n".join("{}:{}".format(i, j) for i, j in summary.items()))
        print("###################################################################")
        return result
    def __newconverter(self,input_file: str, output_file: str):
        cv = Converter(input_file)
        cv.convert(docx_filename=output_file)
        cv.close()
    def convert_to_docx(self):
        # self.__convert_pdf2docx(self.input_pdf_file, self.output_docx_file)
        self.__newconverter(self.input_pdf_file, self.output_docx_file)
        return self.output_docx_file

