from app.engine.text_processor import substitute_placeholders, normalize_text


def test_substitute_name():
    result = substitute_placeholders("Hello {NAME}!", name="Jimin", date="2020-03-15")
    assert result == "Hello Jimin!"


def test_substitute_date():
    result = substitute_placeholders("Born on {DATE}", name="A", date="2020-03-15")
    assert result == "Born on 2020-03-15"


def test_substitute_both():
    result = substitute_placeholders("{NAME} was born on {DATE}.", name="지민", date="2020-03-15")
    assert result == "지민 was born on 2020-03-15."


def test_no_placeholder():
    result = substitute_placeholders("Once upon a time", name="A", date="B")
    assert result == "Once upon a time"


def test_normalize_vietnamese():
    """베트남어 NFC 정규화 - 성조 결합 문자 처리"""
    decomposed = "Xin cha\u0300o"  # 'a' + combining grave
    result = normalize_text(decomposed)
    assert result == "Xin ch\u00e0o"  # 'à' precomposed


def test_normalize_french():
    """프랑스어 악센트 NFC 정규화"""
    decomposed = "cafe\u0301"  # 'e' + combining acute
    result = normalize_text(decomposed)
    assert result == "caf\u00e9"  # 'é' precomposed
