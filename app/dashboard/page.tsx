import { Suspense } from "react"
import { getSession } from "@/lib/auth"
import { getHealthStatus, getWorkflowRuns } from "@/lib/github"
import { 
  BookOpen, 
  Clock, 
  HardDrive, 
  Activity,
  CheckCircle2,
  XCircle,
  Loader2,
  ExternalLink,
  RefreshCw
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import Link from "next/link"

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffMins < 1) return "just now"
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  return `${diffDays}d ago`
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

async function StatsCards() {
  let health
  try {
    health = await getHealthStatus()
  } catch {
    health = null
  }
  
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Books</CardTitle>
          <BookOpen className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{health?.book_count ?? "..."}</div>
          <p className="text-xs text-muted-foreground">
            Rolling 7-day archive
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Latest Issue</CardTitle>
          <Clock className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {health?.newest_book ? new Date(health.newest_book).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "..."}
          </div>
          <p className="text-xs text-muted-foreground">
            {health?.last_update ? formatRelativeTime(health.last_update) : "..."}
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
          <HardDrive className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{health?.total_size_mb?.toFixed(1) ?? "..."} MB</div>
          <p className="text-xs text-muted-foreground">
            Across all EPUBs
          </p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Status</CardTitle>
          <Activity className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-2">
            <span className={`status-dot ${health?.status === "ok" ? "status-dot-success" : "status-dot-warning"}`} />
            <span className="text-2xl font-bold capitalize">{health?.status ?? "..."}</span>
          </div>
          <p className="text-xs text-muted-foreground">
            Feed operational
          </p>
        </CardContent>
      </Card>
    </div>
  )
}

async function RecentBooks() {
  let health
  try {
    health = await getHealthStatus()
  } catch {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Books</CardTitle>
          <CardDescription>Failed to load books</CardDescription>
        </CardHeader>
      </Card>
    )
  }
  
  const books = health?.books?.slice(0, 5) ?? []
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Recent Books</CardTitle>
          <CardDescription>Latest EPUBs in your library</CardDescription>
        </div>
        <Button variant="outline" size="sm" asChild>
          <Link href="/dashboard/library">View all</Link>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {books.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No books in library yet
            </p>
          ) : (
            books.map((book) => (
              <div key={book.filename} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded bg-secondary flex items-center justify-center">
                    <BookOpen className="w-5 h-5 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">{book.title}</p>
                    <p className="text-xs text-muted-foreground">{book.date}</p>
                  </div>
                </div>
                <span className="text-sm text-muted-foreground">
                  {formatBytes(book.size_bytes)}
                </span>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}

async function RecentBuilds() {
  const session = await getSession()
  
  let runs: Awaited<ReturnType<typeof getWorkflowRuns>> = []
  try {
    if (session?.accessToken) {
      runs = await getWorkflowRuns(session.accessToken, undefined, 5)
    }
  } catch {
    // Silent fail - will show empty state
  }
  
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Recent Builds</CardTitle>
          <CardDescription>GitHub Actions workflow runs</CardDescription>
        </div>
        <Button variant="outline" size="sm" asChild>
          <Link href="/dashboard/builds">View all</Link>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {runs.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No recent builds found
            </p>
          ) : (
            runs.map((run) => (
              <div key={run.id} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {run.status === "completed" ? (
                    run.conclusion === "success" ? (
                      <CheckCircle2 className="w-5 h-5 text-[hsl(var(--success))]" />
                    ) : (
                      <XCircle className="w-5 h-5 text-destructive" />
                    )
                  ) : (
                    <Loader2 className="w-5 h-5 text-primary animate-spin" />
                  )}
                  <div>
                    <p className="text-sm font-medium">{run.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {run.head_branch} &middot; {formatRelativeTime(run.created_at)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={run.conclusion === "success" ? "default" : run.conclusion === "failure" ? "destructive" : "secondary"}>
                    {run.conclusion || run.status}
                  </Badge>
                  <Button variant="ghost" size="icon" asChild>
                    <a href={run.html_url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}

function LoadingCard() {
  return (
    <Card>
      <CardContent className="flex items-center justify-center py-10">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </CardContent>
    </Card>
  )
}

export default async function DashboardPage() {
  const session = await getSession()
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome back, {session?.user.name || session?.user.login}
          </p>
        </div>
        <Button variant="outline" size="sm">
          <RefreshCw className="w-4 h-4 mr-2" />
          Trigger Build
        </Button>
      </div>
      
      <Suspense fallback={<div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">{Array(4).fill(0).map((_, i) => <LoadingCard key={i} />)}</div>}>
        <StatsCards />
      </Suspense>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Suspense fallback={<LoadingCard />}>
          <RecentBooks />
        </Suspense>
        
        <Suspense fallback={<LoadingCard />}>
          <RecentBuilds />
        </Suspense>
      </div>
    </div>
  )
}
