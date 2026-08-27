import requests
from django.conf import settings
from .languages import LANGUAGES

def execute_code(source_code, language_id, stdin=None):
    url = f"{settings.JUDGE0_API_URL}/submissions"
    querystring = {"wait": "true"}
    
    payload = {
        "source_code": source_code,
        "language_id": language_id,
        "stdin": stdin,
        "cpu_time_limit": 5,
        "memory_limit": 128000
    }
    
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
        "X-RapidAPI-Host": settings.JUDGE0_API_HOST
    }

    try:
        response = requests.post(url, json=payload, headers=headers, params=querystring)
        response.raise_for_status()
        data = response.json()
        
        return {
            "stdout": data.get("stdout") or "",
            "stderr": data.get("stderr") or data.get("compile_output") or "",
            "status": data.get("status", {}),
            "time": data.get("time", "0.0"),
            "memory": data.get("memory", 0)
        }
    except requests.exceptions.RequestException as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "status": {"id": 13, "description": "Internal Error"},
            "time": "0.0",
            "memory": 0
        }
