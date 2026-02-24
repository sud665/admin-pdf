"use client";

import { useState } from "react";
import useSWR, { mutate } from "swr";
import { apiFetch, fetcher } from "@/lib/api";
import { FontPreset, LANGUAGE_LABELS, LANGUAGES, Language } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
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
import { Plus, Trash2 } from "lucide-react";

export default function FontsPage() {
  const { data: fonts } = useSWR<FontPreset[]>("/api/fonts", fetcher);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    language: "ko" as Language,
    font_family: "",
    font_file_url: "",
    font_size: 12,
    letter_spacing: 0,
    line_height: 1.2,
  });

  async function handleCreate() {
    if (!form.font_family.trim()) return;
    await apiFetch("/api/fonts", {
      method: "POST",
      body: JSON.stringify(form),
    });
    setForm({
      language: "ko",
      font_family: "",
      font_file_url: "",
      font_size: 12,
      letter_spacing: 0,
      line_height: 1.2,
    });
    setOpen(false);
    mutate("/api/fonts");
  }

  async function handleDelete(id: number) {
    await apiFetch(`/api/fonts/${id}`, { method: "DELETE" });
    mutate("/api/fonts");
  }

  const fontsByLang = LANGUAGES.map((lang) => ({
    lang,
    presets: fonts?.filter((f) => f.language === lang) ?? [],
  }));

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">폰트 프리셋</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="w-4 h-4 mr-2" />
              프리셋 추가
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>새 폰트 프리셋</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <div>
                <Label>언어</Label>
                <Select
                  value={form.language}
                  onValueChange={(v) =>
                    setForm((p) => ({ ...p, language: v as Language }))
                  }
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
              <div>
                <Label>폰트 패밀리</Label>
                <Input
                  value={form.font_family}
                  onChange={(e) =>
                    setForm((p) => ({ ...p, font_family: e.target.value }))
                  }
                  placeholder="NotoSans-Regular"
                />
              </div>
              <div>
                <Label>폰트 파일 경로</Label>
                <Input
                  value={form.font_file_url}
                  onChange={(e) =>
                    setForm((p) => ({ ...p, font_file_url: e.target.value }))
                  }
                  placeholder="NotoSans-Regular.ttf"
                />
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <Label>크기(pt)</Label>
                  <Input
                    type="number"
                    value={form.font_size}
                    onChange={(e) =>
                      setForm((p) => ({
                        ...p,
                        font_size: parseFloat(e.target.value),
                      }))
                    }
                  />
                </div>
                <div>
                  <Label>자간</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={form.letter_spacing}
                    onChange={(e) =>
                      setForm((p) => ({
                        ...p,
                        letter_spacing: parseFloat(e.target.value),
                      }))
                    }
                  />
                </div>
                <div>
                  <Label>행간</Label>
                  <Input
                    type="number"
                    step="0.1"
                    value={form.line_height}
                    onChange={(e) =>
                      setForm((p) => ({
                        ...p,
                        line_height: parseFloat(e.target.value),
                      }))
                    }
                  />
                </div>
              </div>
              <Button onClick={handleCreate} className="w-full">
                추가
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {fontsByLang.map(({ lang, presets }) => (
          <Card key={lang}>
            <CardHeader>
              <CardTitle className="text-lg">{LANGUAGE_LABELS[lang]}</CardTitle>
              <CardDescription>
                {presets.length}개 프리셋 등록됨
              </CardDescription>
            </CardHeader>
            <CardContent>
              {presets.length === 0 ? (
                <p className="text-muted-foreground text-sm">
                  프리셋이 없습니다.
                </p>
              ) : (
                <div className="space-y-3">
                  {presets.map((preset) => (
                    <div
                      key={preset.id}
                      className="flex items-center justify-between p-3 rounded-lg border"
                    >
                      <div>
                        <p className="font-medium text-sm">
                          {preset.font_family}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {preset.font_size}pt · 자간 {preset.letter_spacing} ·
                          행간 {preset.line_height}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleDelete(preset.id)}
                      >
                        <Trash2 className="w-4 h-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
