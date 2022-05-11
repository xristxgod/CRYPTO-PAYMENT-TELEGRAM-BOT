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
    phrases: List[JSON] = [
        JSON(code='welcome', text="Добро пожаловать")
    ]
    translator = Translator()
    for phrase in phrases:
        for lang in await Lang.all():
            if not await Phrase.exists(code=phrase.code, lang_id=lang.id):
                if lang.id == 1:
                    await Phrase.create(**phrase.get(), lang_id=lang.id)
                else:
                    res = translator.translate(phrase.text, src="ru")
                    await Phrase.create(
                        code=phrase.code, lang_id=lang.id, text=res.text
                    )