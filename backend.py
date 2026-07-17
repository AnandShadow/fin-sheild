import os
import io
import json
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

app = FastAPI(
    title="Forensic Scam Analyzer Backend",
    description="FastAPI backend to analyze financial scam images using Gemini 1.5 Flash",
    version="1.0.1"
)

# Add CORS middleware to allow stream lit and other clients to access the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = r"""You are an elite financial forensic AI operating for a digital literacy platform. Your objective is to protect vulnerable citizens from hyper-localized financial scams.
Analyze the provided image and the user's optional text description.
Perform these tasks strictly:

Threat Detection: Identify the primary threat vector (e.g., Phishing URL, Fake KYC Request, Electricity Scam). If safe, output Safe.

Risk Assessment: Assign a risk_index from 1 to 5, where 5 is the highest risk.

Translation and Extraction: Extract any vernacular text (Telugu, Hindi, slang) from the image and translate it to formal English.

Localized Warning: Draft a short 2-sentence warning explaining the scam and immediate preventative action.
Output ONLY a valid JSON object with the exact keys: threat_category, risk_index, english_translation, and localized_warning. Do not include markdown formatting or json code blocks in the output. Return raw JSON."""

@app.get("/")
def read_root():
    return {"status": "running", "endpoints": ["/analyze"]}

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    # Configure inside the endpoint as requested
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY environment variable is not set. Please add it to your .env file."
        )
    
    # Configure the SDK
    genai.configure(api_key=api_key)
    
    # Read and open the uploaded image
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid image file: {str(e)}"
        )
    
    try:
        # Build contents for generation
        prompt_contents = [image, SYSTEM_PROMPT]
        if description:
            prompt_contents.append(f"\nUser-provided context/description: {description}")
        
        # Instantiate the model and handle cases where gemini-1.5-flash is not supported
        model_name = "gemini-1.5-flash"
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                prompt_contents,
                generation_config={"response_mime_type": "application/json"}
            )
        except Exception as e:
            if "not found" in str(e).lower() or "404" in str(e) or "not supported" in str(e).lower():
                # Fallback to other available Flash models
                fallback_models = ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest"]
                success = False
                last_err = e
                for fb_model in fallback_models:
                    try:
                        model = genai.GenerativeModel(fb_model)
                        response = model.generate_content(
                            prompt_contents,
                            generation_config={"response_mime_type": "application/json"}
                        )
                        success = True
                        model_name = fb_model
                        break
                    except Exception as fb_err:
                        last_err = fb_err
                        continue
                if not success:
                    raise last_err
            else:
                raise e
        
        # Parse the output
        response_text = response.text.strip()
        
        # Attempt to parse raw JSON string to ensure valid structure
        data = json.loads(response_text)
        
        # Validate that the keys exist
        required_keys = ["threat_category", "risk_index", "english_translation", "localized_warning"]
        for key in required_keys:
            if key not in data:
                data[key] = "Not analyzed" if key != "risk_index" else 1
        
        return JSONResponse(content=data)
        
    except json.JSONDecodeError as jde:
        # Fallback if Gemini returned invalid JSON structure despite system instruction
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to parse model response as JSON.",
                "raw_response": response_text
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating analysis: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
