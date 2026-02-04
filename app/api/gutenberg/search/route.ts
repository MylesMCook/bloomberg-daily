import { NextRequest, NextResponse } from "next/server"

const GUTENDEX_API = "https://gutendex.com/books"

interface GutenbergBook {
  id: number
  title: string
  authors: Array<{ name: string; birth_year: number | null; death_year: number | null }>
  subjects: string[]
  languages: string[]
  formats: Record<string, string>
  download_count: number
}

interface GutendexResponse {
  count: number
  next: string | null
  previous: string | null
  results: GutenbergBook[]
}

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  
  const query = searchParams.get("q") || ""
  const author = searchParams.get("author") || ""
  const title = searchParams.get("title") || ""
  const topic = searchParams.get("topic") || ""
  const language = searchParams.get("language") || "en"
  const page = searchParams.get("page") || "1"
  
  // Build query params for Gutendex
  const params = new URLSearchParams()
  params.set("page", page)
  
  if (query) params.set("search", query)
  if (author) params.set("author", author)
  if (title) params.set("title", title)
  if (topic) params.set("topic", topic)
  if (language) params.set("languages", language)
  
  try {
    const response = await fetch(`${GUTENDEX_API}?${params}`, {
      headers: {
        "User-Agent": "BloombergDaily/1.0 (e-ink reader news aggregator)",
      },
      next: { revalidate: 3600 }, // Cache for 1 hour
    })
    
    if (!response.ok) {
      throw new Error(`Gutendex API error: ${response.status}`)
    }
    
    const data: GutendexResponse = await response.json()
    
    // Transform results to a cleaner format
    const books = data.results.map((book) => ({
      id: book.id,
      title: book.title,
      author: book.authors[0]?.name || "Unknown",
      authors: book.authors,
      subjects: book.subjects.slice(0, 5), // Limit subjects
      language: book.languages[0] || "en",
      downloadCount: book.download_count,
      epubUrl: book.formats["application/epub+zip"] || null,
      coverUrl: book.formats["image/jpeg"] || null,
    }))
    
    return NextResponse.json({
      books,
      total: data.count,
      page: parseInt(page, 10),
      hasNext: !!data.next,
      hasPrevious: !!data.previous,
    })
    
  } catch (error) {
    console.error("Gutenberg search error:", error)
    return NextResponse.json(
      { error: "Failed to search Project Gutenberg" },
      { status: 500 }
    )
  }
}
