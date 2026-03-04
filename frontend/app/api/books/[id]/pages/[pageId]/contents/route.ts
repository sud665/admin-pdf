import { NextResponse } from "next/server";
import contents from "@/data/contents.json";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string; pageId: string }> }
) {
  const { pageId } = await params;
  const pageContents = contents.filter((c) => c.page_id === parseInt(pageId));
  return NextResponse.json(pageContents);
}

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string; pageId: string }> }
) {
  const { pageId } = await params;
  const body = await request.json();
  const newContent = {
    id: contents.length + 1,
    page_id: parseInt(pageId),
    language: body.language,
    text_content: body.text_content,
    font_preset_id: body.font_preset_id || null,
  };
  return NextResponse.json(newContent, { status: 201 });
}
