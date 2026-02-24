export type Language = "ko" | "en" | "vi" | "fr";
export type PageType = "cover" | "opening" | "story" | "closing";
export type OrderStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "timeout";

export interface Book {
  id: number;
  title: string;
  page_size: string;
  bleed_mm: number;
  created_at: string;
}

export interface PageData {
  id: number;
  book_id: number;
  page_number: number;
  page_type: PageType;
  bg_image_url: string | null;
  text_area_x: number;
  text_area_y: number;
  text_area_w: number;
  text_area_h: number;
  is_personalizable: boolean;
}

export interface FontPreset {
  id: number;
  language: Language;
  font_family: string;
  font_file_url: string;
  font_size: number;
  letter_spacing: number;
  line_height: number;
}

export interface PageContent {
  id: number;
  page_id: number;
  language: Language;
  text_content: string;
  font_preset_id: number | null;
}

export interface Order {
  id: number;
  book_id: number;
  main_language: Language;
  sub_languages: string[];
  person_name: string;
  person_date: string;
  status: OrderStatus;
  pdf_url: string | null;
  warning: string | null;
  created_at: string;
}

export const LANGUAGE_LABELS: Record<Language, string> = {
  ko: "한국어",
  en: "English",
  vi: "Tiếng Việt",
  fr: "Français",
};

export const LANGUAGES: Language[] = ["ko", "en", "vi", "fr"];

export const PAGE_TYPE_LABELS: Record<PageType, string> = {
  cover: "표지",
  opening: "오프닝",
  story: "스토리",
  closing: "클로징",
};

export const STATUS_LABELS: Record<OrderStatus, string> = {
  pending: "대기",
  processing: "생성 중",
  completed: "완료",
  failed: "실패",
  timeout: "시간 초과",
};
