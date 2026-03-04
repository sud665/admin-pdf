import { NextResponse } from "next/server";
import orders from "@/data/orders.json";

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;
  const order = orders.find((o) => o.id === parseInt(id));
  if (!order) return NextResponse.json({ detail: "Not found" }, { status: 404 });
  return NextResponse.json(order);
}
