import { getSession } from "@/lib/auth"
import { getRepository } from "@/lib/github"
import { 
  Settings, 
  Github, 
  Globe,
  Bell,
  Shield,
  ExternalLink,
  Copy
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

export default async function SettingsPage() {
  const session = await getSession()
  
  let repo = null
  try {
    if (session?.accessToken) {
      repo = await getRepository(session.accessToken)
    }
  } catch {
    // Silent fail
  }
  
  const opdsUrl = "https://mylesmcook.github.io/bloomberg-daily/opds.xml"
  const healthUrl = "https://mylesmcook.github.io/bloomberg-daily/health.json"
  
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">
          Manage your account and pipeline configuration
        </p>
      </div>
      
      {/* Account */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5" />
            Account
          </CardTitle>
          <CardDescription>Your GitHub account connection</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Avatar className="h-12 w-12">
                <AvatarImage src={session?.user.avatar_url} />
                <AvatarFallback>
                  {session?.user.login.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="font-medium">{session?.user.name || session?.user.login}</p>
                <p className="text-sm text-muted-foreground">@{session?.user.login}</p>
              </div>
            </div>
            <Button variant="outline" asChild>
              <a href="/api/auth/logout">Sign out</a>
            </Button>
          </div>
        </CardContent>
      </Card>
      
      {/* Repository */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Github className="w-5 h-5" />
            Repository
          </CardTitle>
          <CardDescription>Connected GitHub repository</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {repo ? (
            <>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium font-mono">{repo.full_name}</p>
                  <p className="text-sm text-muted-foreground">{repo.description}</p>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <a href={repo.html_url} target="_blank" rel="noopener noreferrer">
                    <ExternalLink className="w-4 h-4 mr-2" />
                    View on GitHub
                  </a>
                </Button>
              </div>
              <div className="grid gap-4 md:grid-cols-3 pt-4 border-t border-border/50">
                <div>
                  <p className="text-sm text-muted-foreground">Stars</p>
                  <p className="text-lg font-medium">{repo.stargazers_count}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Visibility</p>
                  <p className="text-lg font-medium capitalize">{repo.visibility}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Default Branch</p>
                  <p className="text-lg font-medium">{repo.default_branch}</p>
                </div>
              </div>
            </>
          ) : (
            <p className="text-muted-foreground">Unable to load repository information</p>
          )}
        </CardContent>
      </Card>
      
      {/* OPDS Feed */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="w-5 h-5" />
            OPDS Feed
          </CardTitle>
          <CardDescription>Feed URLs for e-reader access</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>OPDS Catalog URL</Label>
            <div className="flex gap-2">
              <Input 
                value={opdsUrl} 
                readOnly 
                className="font-mono text-sm"
              />
              <Button variant="outline" size="icon">
                <Copy className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              Add this URL to your e-reader&apos;s OPDS browser
            </p>
          </div>
          
          <div className="space-y-2">
            <Label>Health Check URL</Label>
            <div className="flex gap-2">
              <Input 
                value={healthUrl} 
                readOnly 
                className="font-mono text-sm"
              />
              <Button variant="outline" size="icon">
                <Copy className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="w-5 h-5" />
            Notifications
          </CardTitle>
          <CardDescription>Configure alert preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Build Failures</p>
              <p className="text-sm text-muted-foreground">
                Get notified when a workflow fails
              </p>
            </div>
            <Switch />
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Daily Summary</p>
              <p className="text-sm text-muted-foreground">
                Daily digest of new publications
              </p>
            </div>
            <Switch />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
