from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import books, pages, fonts

app = FastAPI(title="Joya PDF Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(books.router)
app.include_router(pages.router)
app.include_router(fonts.router)


@app.get("/health")
def health():
    return {"status": "ok"}
