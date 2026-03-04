import { NextResponse } from "next/server";
import books from "@/data/books.json";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const book = books.find((b) => b.id === parseInt(id));
  if (!book) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  return NextResponse.json(book);
}

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const book = books.find((b) => b.id === parseInt(id));
  if (!book) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  const body = await request.json();
  return NextResponse.json({ ...book, ...body });
}

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const book = books.find((b) => b.id === parseInt(id));
  if (!book) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  return new NextResponse(null, { status: 204 });
}
