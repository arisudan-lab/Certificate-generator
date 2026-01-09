from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
import uuid
import os

from generate import certificate  # your function

app = FastAPI()

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.post("/generate")
def generate_certificate(name: str = Form(...)):
    output_file = f"{OUTPUT_DIR}/{uuid.uuid4()}.pdf"

    certificate(
        "template.pdf",
        "template_blank.pdf",
        output_file,
        name
    )

    return FileResponse(
        output_file,
        media_type="application/pdf",
        filename="certificate.pdf"
    )
