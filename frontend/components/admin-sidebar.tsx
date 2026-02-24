"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  BookOpen,
  Type,
  ShoppingCart,
  Wand2,
  LayoutDashboard,
} from "lucide-react";

const menuItems = [
  { href: "/admin/dashboard", label: "대시보드", icon: LayoutDashboard },
  { href: "/admin/books", label: "도서 관리", icon: BookOpen },
  { href: "/admin/fonts", label: "폰트 프리셋", icon: Type },
  { href: "/admin/orders", label: "주문 이력", icon: ShoppingCart },
  { href: "/admin/generate", label: "PDF 생성", icon: Wand2 },
];

export function AdminSidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-64 border-r bg-gray-50/50 min-h-screen p-4 flex flex-col">
      <div className="px-3 mb-8">
        <h1 className="text-xl font-bold tracking-tight">Joya Admin</h1>
        <p className="text-xs text-muted-foreground mt-1">
          자동 조판 시스템
        </p>
      </div>
      <nav className="space-y-1 flex-1">
        {menuItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors",
              pathname.startsWith(item.href)
                ? "bg-primary/10 text-primary font-medium"
                : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
            )}
          >
            <item.icon className="w-4 h-4" />
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="px-3 py-2 text-xs text-muted-foreground border-t">
        MVP Prototype v0.1
      </div>
    </aside>
  );
}
