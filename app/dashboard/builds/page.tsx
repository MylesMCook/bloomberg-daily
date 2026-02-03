import { getSession } from "@/lib/auth"
import { getWorkflowRuns, listWorkflows } from "@/lib/github"
import { 
  CheckCircle2, 
  XCircle, 
  Loader2,
  ExternalLink,
  GitBranch,
  Clock,
  RefreshCw,
  Play
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffMins < 1) return "just now"
  if (diffMins < 60) return `${diffMins} minutes ago`
  if (diffHours < 24) return `${diffHours} hours ago`
  if (diffDays === 1) return "yesterday"
  return `${diffDays} days ago`
}

function formatDuration(start: string, end: string): string {
  const startDate = new Date(start)
  const endDate = new Date(end)
  const diffMs = endDate.getTime() - startDate.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const mins = Math.floor(diffSecs / 60)
  const secs = diffSecs % 60
  
  if (mins === 0) return `${secs}s`
  return `${mins}m ${secs}s`
}

export default async function BuildsPage() {
  const session = await getSession()
  
  let runs: Awaited<ReturnType<typeof getWorkflowRuns>> = []
  let workflows: Awaited<ReturnType<typeof listWorkflows>> = []
  
  try {
    if (session?.accessToken) {
      [runs, workflows] = await Promise.all([
        getWorkflowRuns(session.accessToken, undefined, 20),
        listWorkflows(session.accessToken),
      ])
    }
  } catch {
    // Silent fail
  }
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Builds</h1>
          <p className="text-muted-foreground">
            GitHub Actions workflow runs and history
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Play className="w-4 h-4 mr-2" />
            Trigger Build
          </Button>
        </div>
      </div>
      
      {/* Workflows */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {workflows.map((workflow) => (
          <Card key={workflow.id}>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">{workflow.name}</CardTitle>
              <CardDescription className="font-mono text-xs">
                {workflow.path}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <Badge variant={workflow.state === "active" ? "default" : "secondary"}>
                  {workflow.state}
                </Badge>
                <Button variant="outline" size="sm">
                  <Play className="w-3 h-3 mr-1" />
                  Run
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
      
      {/* Run History */}
      <Card>
        <CardHeader>
          <CardTitle>Run History</CardTitle>
          <CardDescription>Recent workflow executions</CardDescription>
        </CardHeader>
        <CardContent>
          {runs.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No workflow runs found
            </p>
          ) : (
            <div className="space-y-4">
              {runs.map((run) => (
                <div 
                  key={run.id} 
                  className="flex items-center justify-between p-4 rounded-lg border border-border/50 hover:bg-card/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    {run.status === "completed" ? (
                      run.conclusion === "success" ? (
                        <CheckCircle2 className="w-6 h-6 text-[hsl(var(--success))]" />
                      ) : (
                        <XCircle className="w-6 h-6 text-destructive" />
                      )
                    ) : (
                      <Loader2 className="w-6 h-6 text-primary animate-spin" />
                    )}
                    <div>
                      <p className="font-medium">{run.name}</p>
                      <div className="flex items-center gap-3 text-sm text-muted-foreground mt-1">
                        <span className="flex items-center gap-1">
                          <GitBranch className="w-3 h-3" />
                          {run.head_branch}
                        </span>
                        <span className="font-mono text-xs">
                          {run.head_sha.slice(0, 7)}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="flex items-center gap-2 justify-end">
                        <Badge 
                          variant={
                            run.conclusion === "success" ? "default" : 
                            run.conclusion === "failure" ? "destructive" : 
                            "secondary"
                          }
                        >
                          {run.conclusion || run.status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
                        <Clock className="w-3 h-3" />
                        {formatRelativeTime(run.created_at)}
                        {run.status === "completed" && (
                          <span className="text-xs">
                            ({formatDuration(run.created_at, run.updated_at)})
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <Button variant="ghost" size="icon" asChild>
                      <a href={run.html_url} target="_blank" rel="noopener noreferrer">
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
