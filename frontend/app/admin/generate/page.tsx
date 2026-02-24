"use client";

import { useState } from "react";
import useSWR from "swr";
import { apiFetch, fetcher, apiUrl } from "@/lib/api";
import {
  Book,
  Order,
  LANGUAGE_LABELS,
  LANGUAGES,
  Language,
} from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Wand2, Download, Loader2, CheckCircle, XCircle } from "lucide-react";

export default function GeneratePage() {
  const { data: books } = useSWR<Book[]>("/api/books", fetcher);

  const [bookId, setBookId] = useState<string>("");
  const [mainLang, setMainLang] = useState<Language>("ko");
  const [subLangs, setSubLangs] = useState<Set<Language>>(
    new Set(["en", "vi", "fr"])
  );
  const [name, setName] = useState("");
  const [date, setDate] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);

  function toggleSubLang(lang: Language) {
    setSubLangs((prev) => {
      const next = new Set(prev);
      if (next.has(lang)) {
        next.delete(lang);
      } else {
        next.add(lang);
      }
      return next;
    });
  }

  async function handleGenerate() {
    if (!bookId || !name.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const order = await apiFetch<Order>("/api/generate", {
        method: "POST",
        body: JSON.stringify({
          book_id: parseInt(bookId),
          main_language: mainLang,
          sub_languages: Array.from(subLangs).filter((l) => l !== mainLang),
          person_name: name,
          person_date: date,
        }),
      });
      setResult(order);
    } catch (e) {
      setError(e instanceof Error ? e.message : "PDF 생성에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  const availableSubLangs = LANGUAGES.filter((l) => l !== mainLang);

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold mb-6">PDF 생성</h1>

      <Card>
        <CardHeader>
          <CardTitle>주문 정보 입력</CardTitle>
          <CardDescription>
            도서, 언어, 개인화 정보를 입력하고 PDF를 생성하세요.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* 도서 선택 */}
          <div>
            <Label>도서 선택</Label>
            <Select value={bookId} onValueChange={setBookId}>
              <SelectTrigger>
                <SelectValue placeholder="도서를 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                {books?.map((book) => (
                  <SelectItem key={book.id} value={String(book.id)}>
                    {book.title}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 메인 언어 */}
          <div>
            <Label>메인 언어</Label>
            <Select
              value={mainLang}
              onValueChange={(v) => {
                setMainLang(v as Language);
                setSubLangs((prev) => {
                  const next = new Set(prev);
                  next.delete(v as Language);
                  return next;
                });
              }}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {LANGUAGES.map((lang) => (
                  <SelectItem key={lang} value={lang}>
                    {LANGUAGE_LABELS[lang]}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 서브 언어 */}
          <div>
            <Label className="mb-2 block">서브 언어 (최대 3개)</Label>
            <div className="flex gap-2 flex-wrap">
              {availableSubLangs.map((lang) => (
                <Badge
                  key={lang}
                  variant={subLangs.has(lang) ? "default" : "outline"}
                  className="cursor-pointer select-none px-3 py-1.5"
                  onClick={() => toggleSubLang(lang)}
                >
                  {LANGUAGE_LABELS[lang]}
                </Badge>
              ))}
            </div>
          </div>

          {/* 개인화 정보 */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="name">이름</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="예: 지민"
              />
            </div>
            <div>
              <Label htmlFor="date">날짜</Label>
              <Input
                id="date"
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
          </div>

          {/* 생성 버튼 */}
          <Button
            onClick={handleGenerate}
            disabled={loading || !bookId || !name.trim()}
            className="w-full"
            size="lg"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                PDF 생성 중...
              </>
            ) : (
              <>
                <Wand2 className="w-4 h-4 mr-2" />
                PDF 생성하기
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* 결과 */}
      {error && (
        <Card className="mt-4 border-destructive">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-destructive">
              <XCircle className="w-5 h-5" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {result && result.status === "completed" && (
        <Card className="mt-4 border-green-500">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-green-600 mb-4">
              <CheckCircle className="w-5 h-5" />
              <p className="font-medium">PDF가 성공적으로 생성되었습니다!</p>
            </div>
            <div className="space-y-2 text-sm text-muted-foreground mb-4">
              <p>주문 번호: #{result.id}</p>
              <p>이름: {result.person_name}</p>
              <p>
                언어: {LANGUAGE_LABELS[result.main_language as Language]} +{" "}
                {result.sub_languages
                  .map((l) => LANGUAGE_LABELS[l as Language] ?? l)
                  .join(", ")}
              </p>
            </div>
            <a
              href={apiUrl(`/api/generate/download/${result.id}`)}
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button className="w-full" variant="outline">
                <Download className="w-4 h-4 mr-2" />
                PDF 다운로드
              </Button>
            </a>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
