import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CA OS · Your preparation, in one place",
  description: "A focused operating system for CA students — learn, practice and progress with confidence.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
