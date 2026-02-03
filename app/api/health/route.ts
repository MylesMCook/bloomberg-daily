import { NextResponse } from "next/server"
import { getHealthStatus } from "@/lib/github"

export const revalidate = 60 // Revalidate every 60 seconds

export async function GET() {
  try {
    const health = await getHealthStatus()
    return NextResponse.json(health)
  } catch (error) {
    console.error("Failed to get health status:", error)
    return NextResponse.json(
      { 
        status: "error", 
        error: "Failed to fetch health status",
        book_count: 0,
        books: []
      }, 
      { status: 500 }
    )
  }
}
