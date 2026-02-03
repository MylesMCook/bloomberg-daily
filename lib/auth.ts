/**
 * GitHub OAuth Authentication
 * 
 * Handles authentication with GitHub for dashboard access.
 * Uses HTTP-only cookies for secure session management.
 */

import { cookies } from "next/headers"
import { redirect } from "next/navigation"

const GITHUB_CLIENT_ID = process.env.GITHUB_CLIENT_ID!
const GITHUB_CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET!
const APP_URL = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"

// Allowed GitHub usernames (set via environment variable)
const ALLOWED_USERS = (process.env.ALLOWED_GITHUB_USERS || "").split(",").filter(Boolean)

export interface GitHubUser {
  id: number
  login: string
  name: string | null
  avatar_url: string
  email: string | null
}

export interface Session {
  user: GitHubUser
  accessToken: string
  expiresAt: number
}

const SESSION_COOKIE = "session"
const SESSION_DURATION = 7 * 24 * 60 * 60 * 1000 // 7 days

/**
 * Get the current session from cookies
 */
export async function getSession(): Promise<Session | null> {
  const cookieStore = await cookies()
  const sessionCookie = cookieStore.get(SESSION_COOKIE)
  
  if (!sessionCookie?.value) {
    return null
  }
  
  try {
    const session = JSON.parse(atob(sessionCookie.value)) as Session
    
    // Check if session is expired
    if (Date.now() > session.expiresAt) {
      return null
    }
    
    return session
  } catch {
    return null
  }
}

/**
 * Create a session cookie
 */
export async function createSession(user: GitHubUser, accessToken: string): Promise<void> {
  const cookieStore = await cookies()
  
  const session: Session = {
    user,
    accessToken,
    expiresAt: Date.now() + SESSION_DURATION,
  }
  
  const sessionValue = btoa(JSON.stringify(session))
  
  cookieStore.set(SESSION_COOKIE, sessionValue, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    maxAge: SESSION_DURATION / 1000,
    path: "/",
  })
}

/**
 * Delete the session cookie
 */
export async function deleteSession(): Promise<void> {
  const cookieStore = await cookies()
  cookieStore.delete(SESSION_COOKIE)
}

/**
 * Get the GitHub OAuth authorization URL
 */
export function getGitHubAuthUrl(state: string): string {
  const params = new URLSearchParams({
    client_id: GITHUB_CLIENT_ID,
    redirect_uri: `${APP_URL}/api/auth/callback`,
    scope: "read:user user:email repo workflow",
    state,
  })
  
  return `https://github.com/login/oauth/authorize?${params}`
}

/**
 * Exchange authorization code for access token
 */
export async function exchangeCodeForToken(code: string): Promise<string> {
  const response = await fetch("https://github.com/login/oauth/access_token", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      client_id: GITHUB_CLIENT_ID,
      client_secret: GITHUB_CLIENT_SECRET,
      code,
    }),
  })
  
  const data = await response.json()
  
  if (data.error) {
    throw new Error(data.error_description || data.error)
  }
  
  return data.access_token
}

/**
 * Get GitHub user profile
 */
export async function getGitHubUser(accessToken: string): Promise<GitHubUser> {
  const response = await fetch("https://api.github.com/user", {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: "application/json",
    },
  })
  
  if (!response.ok) {
    throw new Error("Failed to fetch GitHub user")
  }
  
  return response.json()
}

/**
 * Check if a user is authorized to access the dashboard
 */
export function isUserAuthorized(user: GitHubUser): boolean {
  // If no users are specified, allow anyone who can authenticate
  if (ALLOWED_USERS.length === 0) {
    return true
  }
  
  return ALLOWED_USERS.includes(user.login)
}

/**
 * Require authentication - redirects to login if not authenticated
 */
export async function requireAuth(): Promise<Session> {
  const session = await getSession()
  
  if (!session) {
    redirect("/login")
  }
  
  return session
}

/**
 * Generate a random state value for OAuth
 */
export function generateState(): string {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, byte => byte.toString(16).padStart(2, "0")).join("")
}
