import os
import json
import time
import google.generativeai as genai
from .config import ANALYSIS_SYSTEM_PROMPT, GEMINI_MODEL_NAME

def analyze_video_file(video_path, video_url, api_key, output_path):
    if os.path.exists(output_path):
        return json.load(open(output_path, 'r', encoding='utf-8'))

    genai.configure(api_key=api_key)
    
    uploaded_file = None
    try:
        print(f"Uploading {video_path}...")
        uploaded_file = genai.upload_file(path=video_path)
        
        while uploaded_file.state.name == "PROCESSING":
            time.sleep(2)
            uploaded_file = genai.get_file(uploaded_file.name)
            
        if uploaded_file.state.name == "FAILED":
            raise ValueError("Gemini processing failed")

        print(f"Analyzing...")
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(
            [uploaded_file, ANALYSIS_SYSTEM_PROMPT],
            generation_config={"response_mime_type": "application/json", "temperature": 0.2}
        )
        
        data = json.loads(response.text)
        data["metadata"]["url"] = video_url
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
        return data

    except Exception as e:
        print(f"Analysis error: {e}")
        return None
    finally:
        if uploaded_file:
            try: genai.delete_file(uploaded_file.name)
            except: pass
