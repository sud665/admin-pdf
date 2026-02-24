import os
import pytest

from app.engine.font_manager import FontManager

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "fonts")


@pytest.fixture
def font_manager():
    return FontManager(font_dir=FONT_DIR)


def test_register_font(font_manager):
    """TTF 폰트 등록이 성공하는지 확인"""
    if not os.path.exists(os.path.join(FONT_DIR, "NotoSans-Regular.ttf")):
        pytest.skip("Test font not available")
    font_name = font_manager.register_font("NotoSans-Regular", "NotoSans-Regular.ttf")
    assert font_name == "NotoSans-Regular"


def test_register_font_not_found(font_manager):
    """존재하지 않는 폰트 파일 등록 시 에러"""
    with pytest.raises(FileNotFoundError):
        font_manager.register_font("Missing", "nonexistent.ttf")


def test_get_registered_fonts(font_manager):
    """등록된 폰트 목록 조회"""
    if not os.path.exists(os.path.join(FONT_DIR, "NotoSans-Regular.ttf")):
        pytest.skip("Test font not available")
    font_manager.register_font("NotoSans-Regular", "NotoSans-Regular.ttf")
    assert "NotoSans-Regular" in font_manager.registered_fonts


def test_register_font_idempotent(font_manager):
    """같은 폰트 중복 등록해도 에러 없음"""
    if not os.path.exists(os.path.join(FONT_DIR, "NotoSans-Regular.ttf")):
        pytest.skip("Test font not available")
    font_manager.register_font("NotoSans-Regular", "NotoSans-Regular.ttf")
    font_manager.register_font("NotoSans-Regular", "NotoSans-Regular.ttf")
    assert len(font_manager.registered_fonts) == 1
