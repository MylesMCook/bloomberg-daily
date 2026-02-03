import { NextRequest, NextResponse } from "next/server"
import { cookies } from "next/headers"
import {
  exchangeCodeForToken,
  getGitHubUser,
  createSession,
  isUserAuthorized,
} from "@/lib/auth"

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const code = searchParams.get("code")
  const state = searchParams.get("state")
  const error = searchParams.get("error")
  
  // Check for OAuth errors
  if (error) {
    console.error("OAuth error:", error)
    return NextResponse.redirect(new URL("/login?error=oauth_error", request.url))
  }
  
  // Validate code and state
  if (!code) {
    return NextResponse.redirect(new URL("/login?error=no_code", request.url))
  }
  
  // Verify state matches (CSRF protection)
  const cookieStore = await cookies()
  const storedState = cookieStore.get("oauth_state")?.value
  
  if (!storedState || storedState !== state) {
    return NextResponse.redirect(new URL("/login?error=invalid_state", request.url))
  }
  
  // Clear state cookie
  cookieStore.delete("oauth_state")
  
  try {
    // Exchange code for access token
    const accessToken = await exchangeCodeForToken(code)
    
    // Get user profile
    const user = await getGitHubUser(accessToken)
    
    // Check if user is authorized
    if (!isUserAuthorized(user)) {
      console.warn(`Unauthorized login attempt: ${user.login}`)
      return NextResponse.redirect(new URL("/login?error=unauthorized", request.url))
    }
    
    // Create session
    await createSession(user, accessToken)
    
    // Redirect to dashboard
    return NextResponse.redirect(new URL("/dashboard", request.url))
    
  } catch (err) {
    console.error("Auth callback error:", err)
    return NextResponse.redirect(new URL("/login?error=auth_failed", request.url))
  }
}
