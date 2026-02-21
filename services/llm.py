from openai import OpenAI
import json
import os
from dotenv import load_dotenv

load_dotenv()


client=OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def llm(system_prompt,user_prompt):

    try:

        response=client.chat.completions.create(
            model="gemini-2.5-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type":"json_object"},
            timeout=60
        )

        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        raise Exception(f"LLM call failed: {str(e)}")