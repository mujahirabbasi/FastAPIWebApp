# app.py
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from ecg_processing import ecg_as_tensor, load_model, predict_risk, validate_ecg_file
import shutil
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
model = load_model()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(...)):
    try:
        file_location = f"/tmp/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Validate the ECG file format
        if not validate_ecg_file(file_location):
            os.remove(file_location)  # Clean up the invalid file
            return templates.TemplateResponse("index.html", {
                "request": request,
                "error": "Incorrect input data format"
            })
        
        # Process the file and make a prediction
        ecg_tensor = ecg_as_tensor(file_location)
        predictions = predict_risk(ecg_tensor, model)
        
        # Clean up the uploaded file
        os.remove(file_location)
        
        return templates.TemplateResponse("results.html", {
            "request": request,
            "predictions": predictions
        })
    except Exception as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"An error occurred during processing: {str(e)}"
        })
