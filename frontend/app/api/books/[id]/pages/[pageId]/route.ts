import { NextResponse } from "next/server";
import pages from "@/data/pages.json";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string; pageId: string }> }
) {
  const { pageId } = await params;
  const page = pages.find((p) => p.id === parseInt(pageId));
  if (!page) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  return NextResponse.json(page);
}

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string; pageId: string }> }
) {
  const { pageId } = await params;
  const page = pages.find((p) => p.id === parseInt(pageId));
  if (!page) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  const body = await request.json();
  return NextResponse.json({ ...page, ...body });
}

export async function DELETE(
  _request: Request,
  { params }: { params: Promise<{ id: string; pageId: string }> }
) {
  const { pageId } = await params;
  const page = pages.find((p) => p.id === parseInt(pageId));
  if (!page) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  return new NextResponse(null, { status: 204 });
}
