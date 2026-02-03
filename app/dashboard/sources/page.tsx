import { getSession } from "@/lib/auth"
import { getFileContent } from "@/lib/github"
import { 
  Layers, 
  Plus, 
  Calendar, 
  Clock, 
  MoreVertical,
  Power,
  Newspaper,
  BookOpen,
  AlertCircle
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import YAML from "yaml"

interface Source {
  name: string
  type: string
  enabled: boolean
  mode: string
  schedule?: string
  retention_days: number
  sections?: string[]
}

interface SourcesConfig {
  version: string
  sources: Record<string, Source>
}

async function getSourcesConfig(accessToken: string): Promise<SourcesConfig | null> {
  try {
    const { content } = await getFileContent(accessToken, "config/sources.yaml")
    return YAML.parse(content) as SourcesConfig
  } catch {
    return null
  }
}

function getSourceIcon(type: string) {
  switch (type) {
    case "calibre_recipe":
      return Newspaper
    case "gutenberg":
      return BookOpen
    default:
      return Layers
  }
}

function formatSchedule(schedule?: string): string {
  if (!schedule) return "On demand"
  
  // Parse cron expression to human-readable
  const parts = schedule.split(" ")
  if (parts.length !== 5) return schedule
  
  const [minute, hour] = parts
  const hourNum = parseInt(hour)
  const period = hourNum >= 12 ? "PM" : "AM"
  const displayHour = hourNum > 12 ? hourNum - 12 : hourNum === 0 ? 12 : hourNum
  
  return `Daily at ${displayHour}:${minute.padStart(2, "0")} ${period} UTC`
}

export default async function SourcesPage() {
  const session = await getSession()
  
  let config: SourcesConfig | null = null
  if (session?.accessToken) {
    config = await getSourcesConfig(session.accessToken)
  }
  
  const sources = config?.sources ?? {}
  const sourceEntries = Object.entries(sources)
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Sources</h1>
          <p className="text-muted-foreground">
            Manage your content sources and schedules
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Source
        </Button>
      </div>
      
      {!config ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-10 gap-4">
            <AlertCircle className="w-10 h-10 text-muted-foreground" />
            <div className="text-center">
              <p className="font-medium">No configuration found</p>
              <p className="text-sm text-muted-foreground">
                Create a sources.yaml file to get started
              </p>
            </div>
            <Button>Create Configuration</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {sourceEntries.map(([id, source]) => {
            const Icon = getSourceIcon(source.type)
            
            return (
              <Card key={id} className="card-interactive">
                <CardHeader className="flex flex-row items-start justify-between space-y-0">
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      source.enabled ? "bg-primary/10" : "bg-muted"
                    }`}>
                      <Icon className={`w-5 h-5 ${source.enabled ? "text-primary" : "text-muted-foreground"}`} />
                    </div>
                    <div>
                      <CardTitle className="text-lg">{source.name}</CardTitle>
                      <CardDescription className="flex items-center gap-1 mt-1">
                        <Badge variant={source.enabled ? "default" : "secondary"} className="text-xs">
                          {source.type.replace("_", " ")}
                        </Badge>
                      </CardDescription>
                    </div>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="w-4 h-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>Edit</DropdownMenuItem>
                      <DropdownMenuItem>Trigger Now</DropdownMenuItem>
                      <DropdownMenuItem>View Logs</DropdownMenuItem>
                      <DropdownMenuItem className="text-destructive">Delete</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2 text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      <span>{formatSchedule(source.schedule)}</span>
                    </div>
                  </div>
                  
                  {source.sections && source.sections.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {source.sections.map((section) => (
                        <Badge key={section} variant="outline" className="text-xs">
                          {section}
                        </Badge>
                      ))}
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between pt-2 border-t border-border/50">
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span className="text-muted-foreground">
                        Keep {source.retention_days} days
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Power className="w-4 h-4 text-muted-foreground" />
                      <Switch checked={source.enabled} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
