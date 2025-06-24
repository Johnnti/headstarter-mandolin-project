import json
import pymupdf

with open('field_info.json', 'r+') as file:
    data = json.load(file)
    
id_and_values = {elem['id']: elem['value'] for elem in data}
    
with pymupdf.open('../Input Data/Adbulla/PA.pdf') as source:
    for page in source.pages():
        for widget in page.widgets():
            # if widget.field_type == pymupdf.PDF_WIDGET_TYPE_TEXT:
            #     if type(id_and_values[widget.field_name]) == "Yes":
            #         widget.field_value = ""
            #         continue
            if widget.field_name in id_and_values:
                widget.field_value = id_and_values[widget.field_name]
                widget.update()
            
    source.save("PA_Filled.pdf")
    
    
print("success 😎")
    