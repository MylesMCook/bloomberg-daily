import Link from "next/link"
import { redirect } from "next/navigation"
import { Github, AlertCircle, ArrowLeft } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface LoginPageProps {
  searchParams: Promise<{ error?: string }>
}

const errorMessages: Record<string, string> = {
  oauth_error: "GitHub authentication failed. Please try again.",
  no_code: "No authorization code received from GitHub.",
  invalid_state: "Invalid session state. Please try again.",
  unauthorized: "You are not authorized to access this dashboard.",
  auth_failed: "Authentication failed. Please try again.",
}

async function getSessionSafe() {
  try {
    const { getSession } = await import("@/lib/auth")
    return await getSession()
  } catch {
    return null
  }
}

export default async function LoginPage({ searchParams }: LoginPageProps) {
  // Redirect if already logged in
  const session = await getSessionSafe()
  if (session) {
    redirect("/dashboard")
  }
  
  const params = await searchParams
  const error = params.error
  const errorMessage = error ? errorMessages[error] || "An unknown error occurred." : null
  
  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Link 
          href="/"
          className="inline-flex items-center gap-2 text-muted-foreground hover:text-foreground mb-8 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to home
        </Link>
        
        <Card className="border-border/50">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl">Sign in to Dashboard</CardTitle>
            <CardDescription>
              Manage your news sources and EPUB library
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {errorMessage && (
              <div className="flex items-center gap-3 p-4 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <p className="text-sm">{errorMessage}</p>
              </div>
            )}
            
            <Button asChild className="w-full" size="lg">
              <a href="/api/auth/login">
                <Github className="w-5 h-5 mr-2" />
                Continue with GitHub
              </a>
            </Button>
            
            <p className="text-xs text-muted-foreground text-center mt-4">
              Only authorized GitHub accounts can access the dashboard.
              <br />
              Authentication grants access to manage workflows and sources.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
