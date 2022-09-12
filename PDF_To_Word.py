from pdf2docx import parse
from typing import Tuple

def convert_pdf2docx(input_file: str, output_file: str, pages: Tuple = None):
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


if __name__ == "__main__":
    import sys
    input_file = r"E:\NewDownloads\DemoDownloads\NEW PDF\SHRI RAM\commercial taxi package.pdf"
    output_file = r"E:\NewDownloads\DemoDownloads\NEW PDF\SHRI RAM\commercial taxi package.docx"
    convert_pdf2docx(input_file, output_file)