import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class NLPService:

    @staticmethod
    def summarize_news(text):
        prompt = f"""
Summarize the following news article in simple Hindi + English (Hinglish).

Rules:
- Do NOT copy sentences directly
- Keep all important facts and numbers
- Make it clear and news-style
- Keep it under 120–140 words

News:
{text}
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Summarization failed: {str(e)}"


    @staticmethod
    def translate_text(text, language):
        prompt = f"""
Translate this text into {language}.

Rules:
- Do NOT summarize
- Keep full meaning
- Make it natural and accurate

Text:
{text}
"""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Translation failed: {str(e)}"