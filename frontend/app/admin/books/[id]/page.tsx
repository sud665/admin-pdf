"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import useSWR, { mutate } from "swr";
import { apiFetch, fetcher } from "@/lib/api";
import { Book, PageData, PAGE_TYPE_LABELS, PageType } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Plus, Trash2, ArrowLeft } from "lucide-react";

export default function BookDetailPage() {
  const params = useParams();
  const bookId = params.id;
  const { data: book } = useSWR<Book>(`/api/books/${bookId}`, fetcher);
  const { data: pages } = useSWR<PageData[]>(
    `/api/books/${bookId}/pages`,
    fetcher
  );

  const [open, setOpen] = useState(false);
  const [pageType, setPageType] = useState<PageType>("story");
  const [pageNumber, setPageNumber] = useState("");

  async function handleCreatePage() {
    const num = parseInt(pageNumber);
    if (isNaN(num)) return;
    const isPersonalizable = ["cover", "opening", "closing"].includes(pageType);
    await apiFetch(`/api/books/${bookId}/pages`, {
      method: "POST",
      body: JSON.stringify({
        page_number: num,
        page_type: pageType,
        is_personalizable: isPersonalizable,
      }),
    });
    setPageNumber("");
    setOpen(false);
    mutate(`/api/books/${bookId}/pages`);
  }

  async function handleDeletePage(pageId: number) {
    await apiFetch(`/api/books/${bookId}/pages/${pageId}`, {
      method: "DELETE",
    });
    mutate(`/api/books/${bookId}/pages`);
  }

  if (!book) return <div>로딩 중...</div>;

  return (
    <div>
      <Link
        href="/admin/books"
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        도서 목록
      </Link>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{book.title}</h1>
          <p className="text-muted-foreground text-sm">
            {book.page_size}&quot; · 도련 {book.bleed_mm}mm
          </p>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>페이지 목록</CardTitle>
          <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="w-4 h-4 mr-2" />
                페이지 추가
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>새 페이지 추가</DialogTitle>
              </DialogHeader>
              <div className="space-y-4 pt-4">
                <div>
                  <Label>페이지 번호</Label>
                  <Input
                    type="number"
                    value={pageNumber}
                    onChange={(e) => setPageNumber(e.target.value)}
                    placeholder="1"
                  />
                </div>
                <div>
                  <Label>페이지 유형</Label>
                  <Select
                    value={pageType}
                    onValueChange={(v) => setPageType(v as PageType)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {(
                        Object.entries(PAGE_TYPE_LABELS) as [
                          PageType,
                          string,
                        ][]
                      ).map(([val, label]) => (
                        <SelectItem key={val} value={val}>
                          {label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button onClick={handleCreatePage} className="w-full">
                  추가
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </CardHeader>
        <CardContent>
          {!pages || pages.length === 0 ? (
            <p className="text-muted-foreground text-sm py-8 text-center">
              페이지가 없습니다.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>번호</TableHead>
                  <TableHead>유형</TableHead>
                  <TableHead>개인화</TableHead>
                  <TableHead>텍스트 영역</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pages.map((page) => (
                  <TableRow key={page.id}>
                    <TableCell>{page.page_number}</TableCell>
                    <TableCell>
                      <Link
                        href={`/admin/books/${bookId}/pages/${page.id}`}
                        className="text-primary hover:underline"
                      >
                        {PAGE_TYPE_LABELS[page.page_type]}
                      </Link>
                    </TableCell>
                    <TableCell>
                      {page.is_personalizable && (
                        <Badge variant="secondary">개인화</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-xs text-muted-foreground">
                      x:{page.text_area_x} y:{page.text_area_y} w:
                      {page.text_area_w} h:{page.text_area_h}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDeletePage(page.id)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
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
