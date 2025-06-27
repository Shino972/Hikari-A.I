import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
PARSE_MODE = "HTML"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

PROMPT_STYLES = {
    "default": {
        "files": {
            "eng": "prompt_eng.txt",
            "rus": "prompt_rus.txt",
            "chi": "prompt_chi.txt"
        }
    },
    "cute": {
        "files": {
            "eng": "cute_prompt_eng.txt",
            "rus": "cute_prompt_rus.txt",
            "chi": "cute_prompt_chi.txt"
        }
    },
    "cheeky": {
        "files": {
            "eng": "cheeky_prompt_eng.txt",
            "rus": "cheeky_prompt_rus.txt",
            "chi": "cheeky_prompt_chi.txt"
        }
    }
}