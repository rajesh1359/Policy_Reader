import os
from pathlib import Path
from PDF_TO_DOC_Coverter import *
# from multiprocessing import Pool
# from pathos.multiprocessing import ProcessingPool as Pool

dir_path = r'E:\NewDownloads\DemoDownloads\NEW PDF\bajaj\Latest'

class pdfconverter:
    def __init__(self, my_pdf_files):
        self.pdf_files = my_pdf_files

    def convert_pdfs_doc(self):
        def pdf_converter(filename):
            cnv = PdfWordConverter(filename)
            #self.logger.setPlainText("Converting PDF {0} to docx".format(filename))
            return cnv.convert_to_docx()


        workers = os.cpu_count()
        # number of processors used will be equal to workers
        new_file= []
        for fl in self.pdf_files:
            new_file.append(pdf_converter(fl))
        return new_file
        # with Pool(workers) as p:
            # return p.map(pdf_converter, self.pdf_files)

'''
pdf_files = []
output_files = []
for root, _, files in os.walk(dir_path):
    for f in files:
        ext = Path(f).suffix.lower()
        #folder= os.path.dirname(Path(f))
        print(root)
        if 'pdf' in ext:
            pass
            pdf_files.append(os.path.join(root, f))

test= pdfconverter(pdf_files)
output_files = test.convert_pdfs_doc()

'''
