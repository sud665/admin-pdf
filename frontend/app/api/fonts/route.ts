import { NextResponse } from "next/server";
import fonts from "@/data/fonts.json";

export async function GET() {
  return NextResponse.json(fonts);
}

export async function POST(request: Request) {
  const body = await request.json();
  const newFont = {
    id: fonts.length + 1,
    language: body.language,
    font_family: body.font_family,
    font_file_url: body.font_file_url || "",
    font_size: body.font_size ?? 12.0,
    letter_spacing: body.letter_spacing ?? 0.0,
    line_height: body.line_height ?? 1.2,
  };
  return NextResponse.json(newFont, { status: 201 });
}
