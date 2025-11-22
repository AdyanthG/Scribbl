from fastapi import APIRouter, UploadFile, File
import uuid
import os

from app.services.storage import StorageManager
from app.services.pdf_processor import PDFProcessor

router = APIRouter()
storage = StorageManager()
processor = PDFProcessor()


@router.post("/process")
async def upload_and_process_pdf(file: UploadFile = File(...)):
    # Save temp file
    file_id = str(uuid.uuid4())
    tmp_path = f"/tmp/{file_id}.pdf"

    with open(tmp_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Upload to Supabase
    dest_path = f"uploads/pdf/{file_id}.pdf"
    pdf_url = storage.upload_file(tmp_path, dest_path)

    # Process PDF
    processed = processor.process_pdf(tmp_path)

    # Remove temp file
    os.remove(tmp_path)

    return {
        "pdf_id": file_id,
        "pdf_url": pdf_url,
        "processed": processed
    }
