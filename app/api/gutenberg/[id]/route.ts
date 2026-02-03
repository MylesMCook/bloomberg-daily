import { NextRequest, NextResponse } from "next/server"

const GUTENDEX_API = "https://gutendex.com/books"

interface RouteParams {
  params: Promise<{ id: string }>
}

export async function GET(
  request: NextRequest,
  { params }: RouteParams
) {
  const { id } = await params
  
  try {
    const response = await fetch(`${GUTENDEX_API}/${id}`, {
      headers: {
        "User-Agent": "BloombergDaily/1.0 (e-ink reader news aggregator)",
      },
      next: { revalidate: 86400 }, // Cache for 24 hours
    })
    
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: "Book not found" },
          { status: 404 }
        )
      }
      throw new Error(`Gutendex API error: ${response.status}`)
    }
    
    const book = await response.json()
    
    // Transform to cleaner format
    return NextResponse.json({
      id: book.id,
      title: book.title,
      author: book.authors[0]?.name || "Unknown",
      authors: book.authors,
      subjects: book.subjects,
      bookshelves: book.bookshelves,
      language: book.languages[0] || "en",
      downloadCount: book.download_count,
      formats: {
        epub: book.formats["application/epub+zip"] || null,
        kindle: book.formats["application/x-mobipocket-ebook"] || null,
        html: book.formats["text/html"] || null,
        plainText: book.formats["text/plain; charset=utf-8"] || book.formats["text/plain"] || null,
      },
      coverUrl: book.formats["image/jpeg"] || null,
    })
    
  } catch (error) {
    console.error("Gutenberg book fetch error:", error)
    return NextResponse.json(
      { error: "Failed to fetch book details" },
      { status: 500 }
    )
  }
}
