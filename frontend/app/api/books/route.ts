import { NextResponse } from "next/server";
import books from "@/data/books.json";

export async function GET() {
  return NextResponse.json(books);
}

export async function POST(request: Request) {
  const body = await request.json();
  const newBook = {
    id: books.length + 1,
    title: body.title,
    page_size: body.page_size || "8.5x11",
    bleed_mm: body.bleed_mm ?? 3.0,
    created_at: new Date().toISOString(),
  };
  return NextResponse.json(newBook, { status: 201 });
}
