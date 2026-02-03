import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { getGitHubAuthUrl, generateState } from "@/lib/auth"

export async function GET() {
  // Generate and store state for CSRF protection
  const state = generateState()
  
  const cookieStore = await cookies()
  cookieStore.set("oauth_state", state, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: 60 * 10, // 10 minutes
    path: "/",
  })
  
  // Redirect to GitHub OAuth
  const authUrl = getGitHubAuthUrl(state)
  return NextResponse.redirect(authUrl)
}
