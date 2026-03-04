import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json(
    { detail: "데모 모드: PDF 다운로드는 실제 백엔드 연결 시 가능합니다." },
    { status: 200 }
  );
}
