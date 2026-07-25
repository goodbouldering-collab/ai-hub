import type { Metadata } from "next";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "AI相談 彦根",
  description:
    "AI講習・個別相談・オンラインサロンを通じて、AIを仕事の成果につなげるための実践拠点です。",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ja">
      <body style={{ margin: 0 }}>{children}</body>
    </html>
  );
}
