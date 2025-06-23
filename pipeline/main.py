import base64
import os
from mistralai import Mistral
from dotenv import load_dotenv
from pathlib import Path
from fill_pa import fill_pa
from pydantic import BaseModel
# from get_pa_fields import get_pa_fields
import time
from google import genai 
from google.genai import types

load_dotenv()
class Field(BaseModel):
    id: str
    value: str
# class Response(BaseModel):
#     response: list[Field]
def encode_pdf(pdf_path):
    """Encode the pdf to base64."""
    try:
        with open(pdf_path, "rb") as pdf_file:
            return base64.b64encode(pdf_file.read()).decode('utf-8')
    except FileNotFoundError:
        print(f"Error: The file {pdf_path} was not found.")
        return None
    except Exception as e:  # Added general exception handling
        print(f"Error: {e}")
        return None

# Path to your referral package pdf
script_dir = Path(__file__).parent
pdf_path = script_dir / ".." /"Input Data" /"Adbulla" / "referral_package.pdf"
pdf_path = str(pdf_path.resolve())

#Path to pA pdf
file_path = script_dir / ".." /"Input Data" /"Adbulla" / "PA.pdf"
fill_pa(file_path)

file_path = script_dir / ".."/"Input Data" /"Adbulla"/"PA_edited.pdf"
#pass the pdf to the fill_pa file to annotate the widgets in the PA


# Getting the base64 string
base64_pdf = encode_pdf(pdf_path)

#instantiate mistral
api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

#instantiate gemini
gemini_key = os.environ["GEMINI_API_KEY"]
gemini_client = genai.Client(api_key=gemini_key)

#read referral package with mistral ocr
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"""data:application/pdf;base64,{base64_pdf}""" 
    },
    include_image_base64=True
)

#add referral package information to user prompt variable 
prompt = ""
for page in ocr_response.pages:
    prompt += page.markdown
    
pdf_path = script_dir / ".." /"Input Data" /"Adbulla" / "PA.pdf"
print("Added referral info to prompt")

#query the gemini llm with pa field names and referral package information embedded in instructions and user prompt respectively.
chat_response = gemini_client.models.generate_content(
    model = "gemini-2.0-flash",
    config=types.GenerateContentConfig(
    system_instruction= f"""You are an expert medical data extractor. Your task is to accurately extract information from a provided medical record and fill out the pdf attached. Pay close attention to dates, patient demographics, medical history, and medication details.

**Instructions:**

1.  **Checkboxes:** If a field is a checkbox that has to be checked based on information from pdf, the value of the field is "Yes" otherwise "No". Don't use the field's name as the value
2.  **Date Format:** All dates should be in MM/DD/YYYY format. If only partial date information is available leave blank the missing ones.
3.  **Yes/No Fields:** For fields that expect a "Yes" or "No" answer, output "Yes" or "No" explicitly. If the information is not explicitly stated, infer based on the presence or absence of related details, or state "No" if no supporting information is found.
4.  **Drug Lists:** For sections with lists of drugs, if a drug is mentioned as being used, failed, or causing an adverse reaction, identify that specific drug. If multiple drugs are mentioned for a single choice (e.g., "Riabni (rituximab-arrx) Rituxan (rituximab)"), select only the relevant one.
5.  **Descriptive Fields:** For fields requiring descriptions (e.g., "Please describe the nature of the failure of the preferred drug"), extract the relevant text directly from the medical record.
6.  **"Other" Fields:** If "Other" is a selectable option, provide the specific "Other" value if present in the medical record.
7.  **Measurements:** Ensure weights are in lbs or kgs and heights in inches or cms, as indicated by the field. Convert if necessary or note if units are different.
8.  **Empty Fields:** If a field is not found or cannot be inferred from the medical record, leave its value blank. Do not invent information.
9.  **Field Index:** Every field has a name annotated to it(on top of checkboxes if field is textbox and in the textarea if field is a text area), in your response, use the index as the index field and then the set the value using the information in the medical record as reference. This indices will help a form filling software to find and populate the approriate fields.
Don't infer the names instead use the names as provided in the document. 

**Extract the corresponding value from the medical record for each field and return them as a list following the schema. The medical record will be supplied in the user prompt:**
            """,
    response_mime_type="application/json",
    response_schema=list[Field]
            ),
    contents = [
        types.Part.from_bytes(
            data=file_path.read_bytes(),
            mime_type="application/pdf"
        ),
        prompt
        ]
)

output = open("../Input Data/Adbulla/field_info.json", "w+")

output.write(chat_response.text)

print(chat_response.text)