import pymupdf

def fill_pa(file_path):
    doc = pymupdf.open(file_path)
    #target each page's widgets
    for page in doc.pages():
        #retrive each widget in page
        widgets = page.widgets()
        #assign an index to each widget
        for widget in widgets:
            if widget.field_type == pymupdf.PDF_WIDGET_TYPE_CHECKBOX:
                widget.update()
                page.insert_text(widget.rect.tl, f"{widget.field_name}", fontsize=5, color=(1,0,0))
            if widget.field_type == pymupdf.PDF_WIDGET_TYPE_TEXT:
                widget.field_value = f"{widget.field_name}"
                widget.text_fontsize = 5
                widget.update()
    #save file 
    doc.save("../Input Data/Adbulla/PA_edited.pdf")
    
    
# fill_pa("../Input Data/Adbulla/PA.pdf")
          
# print("success👏👏")
        