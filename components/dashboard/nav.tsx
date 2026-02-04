"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { 
  LayoutDashboard, 
  Layers, 
  Library, 
  History, 
  Settings,
  LogOut,
  Book
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

interface GitHubUser {
  login: string
  avatar_url: string
  name?: string | null
}

interface DashboardNavProps {
  user: GitHubUser
}

const navItems = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/dashboard/sources", label: "Sources", icon: Layers },
  { href: "/dashboard/library", label: "Library", icon: Library },
  { href: "/dashboard/builds", label: "Builds", icon: History },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
]

export function DashboardNav({ user }: DashboardNavProps) {
  const pathname = usePathname()
  
  return (
    <header className="border-b border-border/50 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Book className="w-4 h-4 text-primary" />
            </div>
            <span className="font-semibold">Daily Pipeline</span>
          </Link>
          
          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || 
                (item.href !== "/dashboard" && pathname.startsWith(item.href))
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    isActive
                      ? "bg-secondary text-foreground"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                  )}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </Link>
              )
            })}
          </nav>
          
          {/* User Menu */}
          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2">
              <img 
                src={user.avatar_url} 
                alt={user.login}
                className="w-8 h-8 rounded-full"
              />
              <span className="text-sm text-muted-foreground">@{user.login}</span>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <a href="/api/auth/logout">
                <LogOut className="w-4 h-4" />
                <span className="sr-only">Sign out</span>
              </a>
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}
