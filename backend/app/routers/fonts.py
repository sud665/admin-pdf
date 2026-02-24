from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FontPreset
from app.schemas import FontPresetCreate, FontPresetUpdate, FontPresetOut

router = APIRouter(prefix="/api/fonts", tags=["fonts"])


@router.post("", response_model=FontPresetOut, status_code=201)
def create_font(body: FontPresetCreate, db: Session = Depends(get_db)):
    font = FontPreset(**body.model_dump())
    db.add(font)
    db.commit()
    db.refresh(font)
    return font


@router.get("", response_model=list[FontPresetOut])
def list_fonts(db: Session = Depends(get_db)):
    return db.query(FontPreset).all()


@router.get("/{font_id}", response_model=FontPresetOut)
def get_font(font_id: int, db: Session = Depends(get_db)):
    font = db.query(FontPreset).filter(FontPreset.id == font_id).first()
    if not font:
        raise HTTPException(status_code=404, detail="FontPreset not found")
    return font


@router.patch("/{font_id}", response_model=FontPresetOut)
def update_font(font_id: int, body: FontPresetUpdate, db: Session = Depends(get_db)):
    font = db.query(FontPreset).filter(FontPreset.id == font_id).first()
    if not font:
        raise HTTPException(status_code=404, detail="FontPreset not found")
    for key, val in body.model_dump(exclude_unset=True).items():
        setattr(font, key, val)
    db.commit()
    db.refresh(font)
    return font


@router.delete("/{font_id}", status_code=204)
def delete_font(font_id: int, db: Session = Depends(get_db)):
    font = db.query(FontPreset).filter(FontPreset.id == font_id).first()
    if not font:
        raise HTTPException(status_code=404, detail="FontPreset not found")
    db.delete(font)
    db.commit()
