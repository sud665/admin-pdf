import { NextResponse } from "next/server";
import fonts from "@/data/fonts.json";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const font = fonts.find((f) => f.id === parseInt(id));
  if (!font) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  return NextResponse.json(font);
}

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const font = fonts.find((f) => f.id === parseInt(id));
  if (!font) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  const body = await request.json();
  return NextResponse.json({ ...font, ...body });
}

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const font = fonts.find((f) => f.id === parseInt(id));
  if (!font) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  return new NextResponse(null, { status: 204 });
}
