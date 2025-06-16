import base64
import os
from mistralai import Mistral
from dotenv import load_dotenv
from pathlib import Path
# from read_pa import read_pa
from pydantic import BaseModel
from typing import Union
from datetime import datetime
from get_pa_fields import get_pa_fields

load_dotenv()

class Field(BaseModel):
    fieldname: str
    value: Union[str, bool, int, datetime]
class Response(BaseModel):
    response: list[Field]
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

# Path to your pdf
script_dir = Path(__file__).parent
pdf_path = script_dir / ".." /"Input Data" /"Adbulla" / "referral_package.pdf"
pdf_path = str(pdf_path.resolve())


# Getting the base64 string
base64_pdf = encode_pdf(pdf_path)

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": f"""data:application/pdf;base64,{base64_pdf}""" 
    },
    include_image_base64=True
)
#read p
prompt = ""
for page in ocr_response.pages:
    prompt += page.markdown
# pdf_path = script_dir / ".." /"Input Data" /"Adbulla" / "PA.pdf"    

chat_response = client.chat.complete(
    model = "ministral-8b-latest",
    messages = [
        {
            "role": "system",
            "content": f"""You are an expert medical data extractor. Your task is to accurately extract information from a provided medical record and fill out the fields below. Pay close attention to dates, patient demographics, medical history, and medication details.

**Instructions:**

1.  **Extract Exactly:** Only extract information that directly corresponds to the fields listed.
2.  **Date Format:** All dates should be in MM/DD/YYYY format. If only partial date information is available, use "XX" for missing month or day, and "XXXX" for missing year (e.g., XX/DD/YYYY, MM/XX/YYYY, XX/XX/YYYY).
3.  **Yes/No Fields:** For fields that expect a "Yes" or "No" answer, output "Yes" or "No" explicitly. If the information is not explicitly stated, infer based on the presence or absence of related details, or state "No" if no supporting information is found.
4.  **Drug Lists:** For sections with lists of drugs, if a drug is mentioned as being used, failed, or causing an adverse reaction, identify that specific drug. If multiple drugs are mentioned for a single choice (e.g., "Riabni (rituximab-arrx) Rituxan (rituximab)"), select only the relevant one.
5.  **Descriptive Fields:** For fields requiring descriptions (e.g., "Please describe the nature of the failure of the preferred drug"), extract the relevant text directly from the medical record.
6.  **"Other" Fields:** If "Other" is a selectable option, provide the specific "Other" value if present in the medical record.
7.  **Measurements:** Ensure weights are in lbs or kgs and heights in inches or cms, as indicated by the field. Convert if necessary or note if units are different.
8.  **Empty Fields:** If a field is not found or cannot be inferred from the medical record, leave its value blank. Do not invent information.

**Here are the fields to fill, along with their expected format. Extract the corresponding value from the medical record for each field:**
{}

            """
            
        },
        {
            "role": "user",
            "content": prompt
        }
    ],
    response_format = {"type": "json_object", "schema": Field.model_json_schema()},
)
print(chat_response.choices[0].message.content)