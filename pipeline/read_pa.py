import pdfplumber
import os
def read_pa(file_path):
    with pdfplumber.open(file_path) as pdf:
        second_page = pdf.pages[1]
        return second_page.extract_text(layout=True)
    

