import { NextResponse } from "next/server";
import orders from "@/data/orders.json";

export async function GET() {
  return NextResponse.json(orders);
}

export async function POST(request: Request) {
  const body = await request.json();
  const newOrder = {
    id: orders.length + 1,
    book_id: body.book_id,
    main_language: body.main_language,
    sub_languages: body.sub_languages || [],
    person_name: body.person_name,
    person_date: body.person_date,
    status: "completed",
    pdf_url: "/sample.pdf",
    warning: null,
    created_at: new Date().toISOString(),
  };
  return NextResponse.json(newOrder, { status: 201 });
}
