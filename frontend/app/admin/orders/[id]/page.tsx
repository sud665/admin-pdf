"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import useSWR from "swr";
import { fetcher, apiUrl } from "@/lib/api";
import {
  Order,
  LANGUAGE_LABELS,
  STATUS_LABELS,
  Language,
} from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ArrowLeft, Download } from "lucide-react";

export default function OrderDetailPage() {
  const params = useParams();
  const orderId = params.id;
  const { data: order } = useSWR<Order>(`/api/orders/${orderId}`, fetcher);

  if (!order) return <div>로딩 중...</div>;

  return (
    <div>
      <Link
        href="/admin/orders"
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        주문 목록
      </Link>

      <h1 className="text-2xl font-bold mb-6">주문 #{order.id}</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>주문 정보</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">이름</span>
              <span className="font-medium">{order.person_name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">날짜</span>
              <span>{order.person_date}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">메인 언어</span>
              <span>
                {LANGUAGE_LABELS[order.main_language as Language]}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">서브 언어</span>
              <div className="flex gap-1">
                {order.sub_languages.map((lang) => (
                  <Badge key={lang} variant="outline">
                    {LANGUAGE_LABELS[lang as Language] ?? lang}
                  </Badge>
                ))}
              </div>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">상태</span>
              <Badge
                variant={
                  order.status === "completed" ? "default" : "secondary"
                }
              >
                {STATUS_LABELS[order.status]}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">생성일</span>
              <span>
                {new Date(order.created_at).toLocaleString("ko")}
              </span>
            </div>
            {order.warning && (
              <div className="p-3 bg-destructive/10 rounded-md text-sm text-destructive">
                {order.warning}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>PDF</CardTitle>
          </CardHeader>
          <CardContent>
            {order.status === "completed" ? (
              <div className="space-y-4">
                <p className="text-sm text-muted-foreground">
                  PDF가 성공적으로 생성되었습니다.
                </p>
                <a
                  href={apiUrl(`/api/generate/download/${order.id}`)}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Button className="w-full">
                    <Download className="w-4 h-4 mr-2" />
                    PDF 다운로드
                  </Button>
                </a>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">
                PDF가 아직 생성되지 않았습니다.
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
