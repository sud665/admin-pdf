import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const body = await request.json();
  const order = {
    id: Math.floor(Math.random() * 1000) + 10,
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
  return NextResponse.json(order);
}
