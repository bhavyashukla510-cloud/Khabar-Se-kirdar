import os
import requests

RUNWAY_API_KEY = os.getenv("RUNWAY_API_KEY")


def generate_with_runway(prompt: str):

    url = "https://api.dev.runwayml.com/v1/text_to_video"

    headers = {
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "Content-Type": "application/json",
        "X-Runway-Version": "2024-11-06"
    }

    data = {
        "model": "gen4.5",
        "promptText": prompt,
        "ratio": "1280:720",
        "duration": 5
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            return {
                "status": "fail",
                "error": response.text
            }

        result = response.json()

        return {
            "status": "success",
            "video_url": result.get("url")
        }

    except Exception as e:
        return {
            "status": "fail",
            "error": str(e)
        }