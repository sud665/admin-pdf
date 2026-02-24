"use client";

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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Download } from "lucide-react";

function statusVariant(
  status: string
): "default" | "secondary" | "destructive" | "outline" {
  switch (status) {
    case "completed":
      return "default";
    case "failed":
    case "timeout":
      return "destructive";
    case "processing":
      return "outline";
    default:
      return "secondary";
  }
}

export default function OrdersPage() {
  const { data: orders } = useSWR<Order[]>("/api/orders", fetcher);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">주문 이력</h1>

      <Card>
        <CardHeader>
          <CardTitle>전체 주문</CardTitle>
        </CardHeader>
        <CardContent>
          {!orders || orders.length === 0 ? (
            <p className="text-muted-foreground text-sm py-8 text-center">
              주문이 없습니다. PDF 생성 페이지에서 주문을 생성해보세요.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>이름</TableHead>
                  <TableHead>메인 언어</TableHead>
                  <TableHead>서브 언어</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>생성일</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {orders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell>#{order.id}</TableCell>
                    <TableCell className="font-medium">
                      <Link
                        href={`/admin/orders/${order.id}`}
                        className="text-primary hover:underline"
                      >
                        {order.person_name}
                      </Link>
                    </TableCell>
                    <TableCell>
                      {LANGUAGE_LABELS[order.main_language as Language]}
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        {order.sub_languages.map((lang) => (
                          <Badge key={lang} variant="outline" className="text-xs">
                            {LANGUAGE_LABELS[lang as Language] ?? lang}
                          </Badge>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusVariant(order.status)}>
                        {STATUS_LABELS[order.status]}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(order.created_at).toLocaleDateString("ko")}
                    </TableCell>
                    <TableCell>
                      {order.status === "completed" && (
                        <a
                          href={apiUrl(`/api/generate/download/${order.id}`)}
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <Button variant="ghost" size="icon">
                            <Download className="w-4 h-4" />
                          </Button>
                        </a>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
