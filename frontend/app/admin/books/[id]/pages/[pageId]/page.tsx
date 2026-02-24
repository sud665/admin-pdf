"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import useSWR, { mutate } from "swr";
import { apiFetch, fetcher } from "@/lib/api";
import {
  PageData,
  PageContent,
  PAGE_TYPE_LABELS,
  LANGUAGE_LABELS,
  LANGUAGES,
  Language,
} from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, Save } from "lucide-react";

export default function PageEditPage() {
  const params = useParams();
  const bookId = params.id;
  const pageId = params.pageId;

  const { data: page } = useSWR<PageData>(
    `/api/books/${bookId}/pages/${pageId}`,
    fetcher
  );
  const { data: contents } = useSWR<PageContent[]>(
    `/api/books/${bookId}/pages/${pageId}/contents`,
    fetcher
  );

  const [texts, setTexts] = useState<Record<Language, string>>({
    ko: "",
    en: "",
    vi: "",
    fr: "",
  });
  const [contentIds, setContentIds] = useState<Record<Language, number | null>>(
    {
      ko: null,
      en: null,
      vi: null,
      fr: null,
    }
  );
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (contents) {
      const newTexts: Record<Language, string> = {
        ko: "",
        en: "",
        vi: "",
        fr: "",
      };
      const newIds: Record<Language, number | null> = {
        ko: null,
        en: null,
        vi: null,
        fr: null,
      };
      for (const c of contents) {
        newTexts[c.language] = c.text_content;
        newIds[c.language] = c.id;
      }
      setTexts(newTexts);
      setContentIds(newIds);
    }
  }, [contents]);

  async function handleSave(lang: Language) {
    setSaving(true);
    try {
      if (contentIds[lang]) {
        await apiFetch(
          `/api/books/${bookId}/pages/${pageId}/contents/${contentIds[lang]}`,
          {
            method: "PATCH",
            body: JSON.stringify({ text_content: texts[lang] }),
          }
        );
      } else {
        await apiFetch(`/api/books/${bookId}/pages/${pageId}/contents`, {
          method: "POST",
          body: JSON.stringify({
            language: lang,
            text_content: texts[lang],
          }),
        });
      }
      mutate(`/api/books/${bookId}/pages/${pageId}/contents`);
    } finally {
      setSaving(false);
    }
  }

  function insertPlaceholder(placeholder: string, lang: Language) {
    setTexts((prev) => ({
      ...prev,
      [lang]: prev[lang] + placeholder,
    }));
  }

  if (!page) return <div>로딩 중...</div>;

  return (
    <div>
      <Link
        href={`/admin/books/${bookId}`}
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground mb-4"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        페이지 목록
      </Link>

      <div className="mb-6">
        <h1 className="text-2xl font-bold">
          페이지 {page.page_number} — {PAGE_TYPE_LABELS[page.page_type]}
        </h1>
        <div className="flex gap-2 mt-2">
          {page.is_personalizable && (
            <Badge variant="secondary">개인화 페이지</Badge>
          )}
          <span className="text-sm text-muted-foreground">
            텍스트 영역: x:{page.text_area_x} y:{page.text_area_y} w:
            {page.text_area_w} h:{page.text_area_h}
          </span>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>원고 편집</CardTitle>
          <CardDescription>
            언어별로 텍스트를 입력하세요.
            {page.is_personalizable &&
              " {NAME}과 {DATE} 플레이스홀더를 사용할 수 있습니다."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="ko">
            <TabsList>
              {LANGUAGES.map((lang) => (
                <TabsTrigger key={lang} value={lang}>
                  {LANGUAGE_LABELS[lang]}
                </TabsTrigger>
              ))}
            </TabsList>
            {LANGUAGES.map((lang) => (
              <TabsContent key={lang} value={lang}>
                <div className="space-y-3">
                  <Textarea
                    value={texts[lang]}
                    onChange={(e) =>
                      setTexts((prev) => ({
                        ...prev,
                        [lang]: e.target.value,
                      }))
                    }
                    rows={6}
                    placeholder={`${LANGUAGE_LABELS[lang]} 텍스트를 입력하세요...`}
                  />
                  <div className="flex items-center gap-2">
                    {page.is_personalizable && (
                      <>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => insertPlaceholder("{NAME}", lang)}
                        >
                          {"{NAME}"} 삽입
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => insertPlaceholder("{DATE}", lang)}
                        >
                          {"{DATE}"} 삽입
                        </Button>
                      </>
                    )}
                    <Button
                      size="sm"
                      onClick={() => handleSave(lang)}
                      disabled={saving}
                      className="ml-auto"
                    >
                      <Save className="w-4 h-4 mr-2" />
                      저장
                    </Button>
                  </div>
                </div>
              </TabsContent>
            ))}
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
