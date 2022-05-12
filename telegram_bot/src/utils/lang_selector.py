from typing import List
from src.models import Lang, Phrase

class LanguagesSelector:
    def __init__(self):
        self.menu = {}

    def get_hotkey(self, code: str):
        return self.menu[code]

    async def update(self):
        menu = {}
        for code in await Phrase.all().values_list('code', flat=True):
            if code not in menu.keys():
                menu.update({code: await Phrase.filter(code=code).values_list('text', flat=True)})
        self.menu = menu

    async def get_button_texts(self, codes: List[str], lang_id: int) -> List[str]:
        """Get list of phrases."""
        return [await self.say(code, lang_id) for code in codes]

    async def say(self, code: str, lang_id: int) -> str:
        """Get one phrase by code and lang"""
        if await Lang.exists(id=lang_id):
            p = await Phrase.get_or_none(code=code, lang_id=lang_id)
            return p.text if p is not None else '???'
        else:
            return '???'

    async def format(self, code: str, lang_id: int, **kwargs) -> (str, str):
        """Formatting template phrase by yours params"""
        text = await self.say(code, lang_id)
        answer = []
        for row in text.split('\n'):
            value_is_null = True
            for key, value in kwargs.items():
                placeholder = '{' + f'{key}' + '}'
                if row.find(placeholder) != -1:
                    if row.startswith('???') and value is None:
                        continue
                    row = row.replace(placeholder, f'{value}')
                    value_is_null = False
            if row.startswith('???') and value_is_null:
                continue
            elif row.startswith('???'):
                row = row.replace('???', '')
            answer.append(row)
        return '\n'.join(answer)

lang_selector = LanguagesSelector()