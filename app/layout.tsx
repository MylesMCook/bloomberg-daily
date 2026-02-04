import type { Metadata, Viewport } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })

export const metadata: Metadata = {
  title: {
    default: "Daily Pipeline - News to EPUB",
    template: "%s | Daily Pipeline"
  },
  description: "Automated news-to-EPUB pipeline for e-ink readers. Fetch Bloomberg, WSJ, and Project Gutenberg content with a beautiful management dashboard.",
  openGraph: {
    title: "Daily Pipeline",
    description: "News-to-EPUB pipeline for e-ink readers",
    type: "website",
  },
}

export const viewport: Viewport = {
  themeColor: "#0a0a0a",
  colorScheme: "dark",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  )
}
