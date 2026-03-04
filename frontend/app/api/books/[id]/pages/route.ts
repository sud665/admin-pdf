import { NextResponse } from "next/server";
import pages from "@/data/pages.json";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const bookPages = pages.filter((p) => p.book_id === parseInt(id));
  return NextResponse.json(bookPages);
}

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const body = await request.json();
  const newPage = {
    id: pages.length + 1,
    book_id: parseInt(id),
    page_number: body.page_number,
    page_type: body.page_type,
    bg_image_url: body.bg_image_url || null,
    text_area_x: body.text_area_x ?? 60.0,
    text_area_y: body.text_area_y ?? 200.0,
    text_area_w: body.text_area_w ?? 480.0,
    text_area_h: body.text_area_h ?? 350.0,
    is_personalizable: body.is_personalizable ?? false,
  };
  return NextResponse.json(newPage, { status: 201 });
}
