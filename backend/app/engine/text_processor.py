import unicodedata


def substitute_placeholders(text: str, *, name: str, date: str) -> str:
    return text.replace("{NAME}", name).replace("{DATE}", date)


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)
