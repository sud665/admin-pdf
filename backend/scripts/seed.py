"""
더미 동화 시드 데이터:
- 1권: "Joya의 모험"
- 5페이지: 표지, 오프닝, 스토리x2, 클로징
- 4개 언어: 한/영/베트남/불어
- 표지/오프닝/클로징에 {NAME}, {DATE} 플레이스홀더
- 4개 언어 폰트 프리셋 (NotoSans-Regular)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Book, Page, PageContent, FontPreset, Language, PageType

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///seed.db")


def seed(db_url: str = DATABASE_URL):
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Check if data already exists
    if db.query(Book).first():
        print("Data already exists. Skipping seed.")
        db.close()
        return

    # 1. Create book
    book = Book(title="Joya의 모험", page_size="8.5x11", bleed_mm=3.0)
    db.add(book)
    db.commit()
    db.refresh(book)
    print(f"Created book: {book.title} (id={book.id})")

    # 2. Create font presets
    font_presets = {}
    for lang in Language:
        preset = FontPreset(
            language=lang,
            font_family="NotoSans-Regular",
            font_file_url="NotoSans-Regular.ttf",
            font_size=14.0 if lang == Language.ko else 12.0,
            letter_spacing=0.0,
            line_height=1.4 if lang == Language.ko else 1.3,
        )
        db.add(preset)
        db.commit()
        db.refresh(preset)
        font_presets[lang] = preset
        print(f"  Font preset: {lang.value} -> {preset.font_family} (id={preset.id})")

    # 3. Create pages with content
    pages_data = [
        {
            "page_number": 1,
            "page_type": PageType.cover,
            "is_personalizable": True,
            "text_area_x": 80.0,
            "text_area_y": 300.0,
            "text_area_w": 450.0,
            "text_area_h": 200.0,
            "contents": {
                Language.ko: "{NAME}의 특별한 모험\n{DATE}에 시작된 이야기",
                Language.en: "The Special Adventure of {NAME}\nA story that began on {DATE}",
                Language.vi: "Cuộc phiêu lưu đặc biệt của {NAME}\nCâu chuyện bắt đầu vào {DATE}",
                Language.fr: "L'aventure spéciale de {NAME}\nUne histoire commencée le {DATE}",
            },
        },
        {
            "page_number": 2,
            "page_type": PageType.opening,
            "is_personalizable": True,
            "text_area_x": 60.0,
            "text_area_y": 200.0,
            "text_area_w": 480.0,
            "text_area_h": 350.0,
            "contents": {
                Language.ko: "어느 화창한 날, {NAME}은(는) 숲 속에서 반짝이는 작은 빛을 발견했어요.\n\"저건 뭘까?\" {NAME}은(는) 궁금해하며 빛을 따라갔어요.",
                Language.en: "One sunny day, {NAME} discovered a tiny shimmering light in the forest.\n\"What could that be?\" {NAME} wondered, following the light.",
                Language.vi: "Vào một ngày nắng đẹp, {NAME} phát hiện một ánh sáng nhỏ lấp lánh trong rừng.\n\"Đó là gì vậy?\" {NAME} tự hỏi và đi theo ánh sáng.",
                Language.fr: "Par un beau jour ensoleillé, {NAME} découvrit une petite lumière scintillante dans la forêt.\n\"Qu'est-ce que c'est ?\" se demanda {NAME} en suivant la lumière.",
            },
        },
        {
            "page_number": 3,
            "page_type": PageType.story,
            "is_personalizable": False,
            "text_area_x": 60.0,
            "text_area_y": 200.0,
            "text_area_w": 480.0,
            "text_area_h": 350.0,
            "contents": {
                Language.ko: "빛을 따라가니 아름다운 정원이 나타났어요. 정원에는 알록달록한 꽃들이 피어 있었고, 나비들이 춤을 추고 있었어요.\n가운데에는 작은 요정이 앉아 있었답니다.",
                Language.en: "Following the light, a beautiful garden appeared. The garden was filled with colorful flowers, and butterflies were dancing.\nIn the middle sat a tiny fairy.",
                Language.vi: "Đi theo ánh sáng, một khu vườn tuyệt đẹp hiện ra. Vườn đầy hoa sắc màu và những chú bướm đang nhảy múa.\nỞ giữa vườn, một nàng tiên nhỏ đang ngồi.",
                Language.fr: "En suivant la lumière, un magnifique jardin apparut. Le jardin était rempli de fleurs colorées et les papillons dansaient.\nAu milieu se trouvait une petite fée.",
            },
        },
        {
            "page_number": 4,
            "page_type": PageType.story,
            "is_personalizable": False,
            "text_area_x": 60.0,
            "text_area_y": 200.0,
            "text_area_w": 480.0,
            "text_area_h": 350.0,
            "contents": {
                Language.ko: "\"안녕! 너를 기다리고 있었어,\" 요정이 말했어요.\n\"이 마법의 정원은 용기 있는 아이만 찾을 수 있단다. 네가 바로 그 아이야!\"\n요정은 반짝이는 씨앗 하나를 건네주었어요.",
                Language.en: "\"Hello! I've been waiting for you,\" said the fairy.\n\"Only a brave child can find this magical garden. You are that child!\"\nThe fairy handed over a sparkling seed.",
                Language.vi: "\"Xin chào! Tôi đã đợi bạn,\" nàng tiên nói.\n\"Chỉ những đứa trẻ dũng cảm mới tìm được khu vườn phép thuật này. Bạn chính là đứa trẻ đó!\"\nNàng tiên trao một hạt giống lấp lánh.",
                Language.fr: "\"Bonjour ! Je t'attendais,\" dit la fée.\n\"Seul un enfant courageux peut trouver ce jardin magique. Tu es cet enfant !\"\nLa fée tendit une graine scintillante.",
            },
        },
        {
            "page_number": 5,
            "page_type": PageType.closing,
            "is_personalizable": True,
            "text_area_x": 80.0,
            "text_area_y": 250.0,
            "text_area_w": 450.0,
            "text_area_h": 250.0,
            "contents": {
                Language.ko: "{NAME}은(는) 씨앗을 소중히 품에 안고 집으로 돌아왔어요.\n그 씨앗은 {NAME}의 용기와 사랑으로 자라나 세상에서 가장 아름다운 꽃이 되었답니다.\n\n— 끝 —",
                Language.en: "{NAME} held the seed close and returned home.\nThe seed grew with {NAME}'s courage and love, becoming the most beautiful flower in the world.\n\n— The End —",
                Language.vi: "{NAME} ôm hạt giống và trở về nhà.\nHạt giống lớn lên nhờ lòng dũng cảm và tình yêu của {NAME}, trở thành bông hoa đẹp nhất thế giới.\n\n— Hết —",
                Language.fr: "{NAME} serra la graine contre son cœur et rentra à la maison.\nLa graine grandit grâce au courage et à l'amour de {NAME}, devenant la plus belle fleur du monde.\n\n— Fin —",
            },
        },
    ]

    for page_data in pages_data:
        contents = page_data.pop("contents")
        page = Page(book_id=book.id, **page_data)
        db.add(page)
        db.commit()
        db.refresh(page)
        print(f"  Page {page.page_number}: {page.page_type.value} (id={page.id})")

        for lang, text in contents.items():
            content = PageContent(
                page_id=page.id,
                language=lang,
                text_content=text,
                font_preset_id=font_presets[lang].id,
            )
            db.add(content)

    db.commit()
    print(f"\nSeed complete: 1 book, 5 pages, 20 contents, 4 font presets")
    db.close()


if __name__ == "__main__":
    seed()
