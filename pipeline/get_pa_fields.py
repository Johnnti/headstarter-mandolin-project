import pymupdf



def get_pa_fields(pdf_path):
    doc = pymupdf.open(pdf_path)
    field_names = []
    # field_values = []
    for page_number in range(len(doc)):
        page = doc[page_number]
        widgets = page.widgets()
        for widget in widgets:
            field_names.append(widget.field_label)

    return field_names

