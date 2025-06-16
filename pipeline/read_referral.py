import base64
import os
from mistralai import Mistral
from dotenv import load_dotenv
from pathlib import Path
from read_pa import read_pa
from pydantic import BaseModel
from typing import Union
from datetime import datetime

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
prompt = ""
for page in ocr_response.pages:
    prompt += page.markdown
pdf_path = script_dir / ".." /"Input Data" /"Adbulla" / "PA.pdf"    

pa = read_pa(pdf_path)
prompt += "\n\n\n\n" + pa
chat_response = client.chat.complete(
    model = "ministral-8b-latest",
    messages = [
        {
            "role": "system",
            "content": """You are a healthcare professional seasoned in filling out preauthorization forms by extracting relevant data from a patient's medical records.
            The user will provide two parts of the information. The first part is the user's previous medical records. The second part is the user's preauthorization form from their
            insurance company both in markdown format. Use the information from the patient's medical records to fill out the preauthorization form. For example, in the name section of the PA form, 
            if the patient's name is John Doe, output {Fieldname: "Name", "value": "John Doe"}. Return a list of such fields with their values. The fieldname should be the same as that of the PA form to allow 
            pdf filling software to be able to automatically fill the form. 
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