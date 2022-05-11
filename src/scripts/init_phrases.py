from typing import List
from googletrans import Translator
from src.models import Lang, Phrase

class JSON:
    def __init__(self, code, text):
        self.code = code
        self.text = text

    def get(self):
        return {'code': self.code, 'text': self.text}

async def init_phrases():
    if not await Lang.exists(id=1):
        await Lang.create(id=1, name='🇷🇺 RU')
    if not await Lang.exists(id=2):
        await Lang.create(id=2, name='🇬🇧 EN')
    phrase: List[JSON] = [
        JSON(code='welcome', text="Добро пожаловать")
    ]