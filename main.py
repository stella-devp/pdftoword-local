from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import subprocess
import uuid
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")
print(f"API_KEY loaded: {API_KEY}")


app = FastAPI()

@app.post("/convert")
async def convert_pdf_to_word(file: UploadFile = File(...), authorization: str = Header(None)):
    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)

    input_path = os.path.join(temp_dir, f"{uuid.uuid4()}.pdf")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    try:
        subprocess.run([
            "soffice", "--headless", "--convert-to", "docx",
            "--outdir", temp_dir, input_path
        ], check=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion failed: {str(e)}")

    output_path = input_path.replace(".pdf", ".docx")
    if not os.path.exists(output_path):
        raise HTTPException(status_code=500, detail="Conversion failed.")

    return FileResponse(
        path=output_path,
        filename=file.filename.replace(".pdf", ".docx"),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

