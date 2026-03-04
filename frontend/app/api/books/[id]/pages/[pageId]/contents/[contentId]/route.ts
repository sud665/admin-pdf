import { NextResponse } from "next/server";
import contents from "@/data/contents.json";

export async function PATCH(
  request: Request,
  { params }: { params: Promise<{ id: string; pageId: string; contentId: string }> }
) {
  const { contentId } = await params;
  const content = contents.find((c) => c.id === parseInt(contentId));
  if (!content) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  const body = await request.json();
  return NextResponse.json({ ...content, ...body });
}
