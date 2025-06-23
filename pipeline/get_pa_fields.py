import pymupdf



def get_pa_fields(pdf_path):
    doc = pymupdf.open(pdf_path)
    field_labels = []
    field_names = []
    for page_number in range(len(doc)):
        page = doc[page_number]
        widgets = page.widgets()
        for widget in widgets:
            for label, name in zip(widget.field_label, widget.field_name): 
                field_names.append(widget.field_label)

    return field_names


result = get_pa_fields(r"C:\Users\dejhs\headstarter\headstarter-mandolin-project\Input Data\Adbulla\PA.pdf")
