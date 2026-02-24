"use client";

import { useState } from "react";
import Link from "next/link";
import useSWR, { mutate } from "swr";
import { apiFetch, fetcher } from "@/lib/api";
import { Book } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Plus, Trash2 } from "lucide-react";

export default function BooksPage() {
  const { data: books } = useSWR<Book[]>("/api/books", fetcher);
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");

  async function handleCreate() {
    if (!title.trim()) return;
    await apiFetch("/api/books", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
    setTitle("");
    setOpen(false);
    mutate("/api/books");
  }

  async function handleDelete(id: number) {
    await apiFetch(`/api/books/${id}`, { method: "DELETE" });
    mutate("/api/books");
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">도서 관리</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              도서 추가
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>새 도서 추가</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <Label htmlFor="title">도서 제목</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="예: Joya의 모험"
                />
              </div>
              <Button onClick={handleCreate} className="w-full">
                추가
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>도서 목록</CardTitle>
        </CardHeader>
        <CardContent>
          {!books || books.length === 0 ? (
            <p className="text-muted-foreground text-sm py-8 text-center">
              등록된 도서가 없습니다. 새 도서를 추가해주세요.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>제목</TableHead>
                  <TableHead>페이지 규격</TableHead>
                  <TableHead>도련(mm)</TableHead>
                  <TableHead>생성일</TableHead>
                  <TableHead className="w-[80px]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {books.map((book) => (
                  <TableRow key={book.id}>
                    <TableCell>{book.id}</TableCell>
                    <TableCell>
                      <Link
                        href={`/admin/books/${book.id}`}
                        className="text-primary hover:underline font-medium"
                      >
                        {book.title}
                      </Link>
                    </TableCell>
                    <TableCell>{book.page_size}</TableCell>
                    <TableCell>{book.bleed_mm}</TableCell>
                    <TableCell>
                      {new Date(book.created_at).toLocaleDateString("ko")}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(book.id)}
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
