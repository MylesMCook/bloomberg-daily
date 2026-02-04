import Link from "next/link"
import { Book, Clock, Rss, Cpu, Building2, Newspaper, ArrowRight, Github, Tablet } from "lucide-react"
import { Button } from "@/components/ui/button"

async function getSessionSafe() {
  try {
    const { getSession } = await import("@/lib/auth")
    return await getSession()
  } catch (error) {
    console.log("[v0] Auth error (likely missing env vars):", error)
    return null
  }
}

export default async function Home() {
  const session = await getSessionSafe()
  
  return (
    <main className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-border/50 bg-card/30 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
              <Book className="w-4 h-4 text-primary" />
            </div>
            <span className="font-semibold">Daily Pipeline</span>
          </div>
          
          {session ? (
            <Button asChild size="sm">
              <Link href="/dashboard">
                Dashboard
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          ) : (
            <Button asChild variant="outline" size="sm">
              <Link href="/login">
                <Github className="w-4 h-4 mr-2" />
                Sign in
              </Link>
            </Button>
          )}
        </div>
      </header>
      
      {/* Hero */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-2xl text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm mb-6">
            <Tablet className="w-4 h-4" />
            Optimized for CrossPoint OS
          </div>
          
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-4">
            News-to-EPUB
            <br />
            <span className="text-primary">Pipeline</span>
          </h1>
          
          <p className="text-lg text-muted-foreground mb-8 max-w-lg mx-auto">
            Automated daily news delivery from Bloomberg and more, 
            beautifully formatted for e-ink readers.
          </p>

          {/* OPDS Feed Card */}
          <div className="bg-card border border-border rounded-xl p-6 mb-6 text-left">
            <div className="flex items-center gap-2 mb-4">
              <span className="status-dot status-dot-success" />
              <span className="flex items-center gap-2 text-sm font-medium">
                <Rss className="w-4 h-4" />
                OPDS Feed Available
              </span>
            </div>
            <div className="font-mono bg-background p-4 rounded-lg text-primary text-sm break-all border border-border">
              https://mylesmcook.github.io/bloomberg-daily/opds.xml
            </div>
            <p className="text-muted-foreground text-sm mt-3">
              Add this URL to your e-reader&apos;s OPDS browser
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            {/* Sections */}
            <div className="bg-card border border-border rounded-xl p-6 text-left">
              <p className="font-semibold mb-3 flex items-center gap-2">
                <Book className="w-4 h-4 text-primary" />
                Sections Included
              </p>
              <div className="flex gap-2 flex-wrap">
                <SectionTag icon={<Cpu className="w-3.5 h-3.5" />} label="AI" />
                <SectionTag icon={<Rss className="w-3.5 h-3.5" />} label="Technology" />
                <SectionTag icon={<Building2 className="w-3.5 h-3.5" />} label="Industries" />
                <SectionTag icon={<Newspaper className="w-3.5 h-3.5" />} label="Latest" />
              </div>
            </div>

            {/* Schedule */}
            <div className="bg-card border border-border rounded-xl p-6 text-left">
              <p className="font-semibold mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4 text-primary" />
                Automated Schedule
              </p>
              <p className="text-muted-foreground text-sm">
                Daily at midnight UTC (6 PM CST)
                <br />
                Rolling 7-day archive maintained automatically
              </p>
            </div>
          </div>

          {/* CTA */}
          <div className="flex items-center justify-center gap-4">
            {session ? (
              <Button asChild size="lg">
                <Link href="/dashboard">
                  Go to Dashboard
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
              </Button>
            ) : (
              <Button asChild size="lg">
                <Link href="/login">
                  <Github className="w-4 h-4 mr-2" />
                  Sign in to Manage
                </Link>
              </Button>
            )}
            <Button variant="outline" size="lg" asChild>
              <a 
                href="https://github.com/MylesMCook/bloomberg-daily" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                View on GitHub
              </a>
            </Button>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="border-t border-border/50 py-6">
        <p className="text-center text-sm text-muted-foreground">
          Powered by GitHub Actions
          {" "}&middot;{" "}
          Built with Next.js
          {" "}&middot;{" "}
          <a
            href="https://github.com/MylesMCook/bloomberg-daily"
            className="text-primary hover:underline"
          >
            Open Source
          </a>
        </p>
      </footer>
    </main>
  )
}

function SectionTag({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <span className="bg-secondary text-foreground px-3 py-1.5 rounded-full text-sm flex items-center gap-1.5">
      {icon}
      {label}
    </span>
  )
}
