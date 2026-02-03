import { getHealthStatus } from "@/lib/github"
import { 
  BookOpen, 
  Download, 
  Eye,
  Search,
  Filter,
  Calendar,
  HardDrive
} from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric", 
    month: "long",
    day: "numeric"
  })
}

export default async function LibraryPage() {
  let health
  try {
    health = await getHealthStatus()
  } catch {
    health = null
  }
  
  const books = health?.books ?? []
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Library</h1>
          <p className="text-muted-foreground">
            Browse and download your EPUB collection
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              placeholder="Search books..." 
              className="pl-9 w-[250px]"
            />
          </div>
          <Button variant="outline" size="icon">
            <Filter className="w-4 h-4" />
          </Button>
        </div>
      </div>
      
      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <BookOpen className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{books.length}</p>
              <p className="text-sm text-muted-foreground">Total Books</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <HardDrive className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">{health?.total_size_mb?.toFixed(1) ?? 0} MB</p>
              <p className="text-sm text-muted-foreground">Storage Used</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-4 pt-6">
            <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <Calendar className="w-6 h-6 text-primary" />
            </div>
            <div>
              <p className="text-2xl font-bold">7</p>
              <p className="text-sm text-muted-foreground">Day Rolling Archive</p>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Book Grid */}
      {books.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-10 gap-4">
            <BookOpen className="w-10 h-10 text-muted-foreground" />
            <div className="text-center">
              <p className="font-medium">No books in library</p>
              <p className="text-sm text-muted-foreground">
                Books will appear here after your first successful fetch
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {books.map((book) => (
            <Card key={book.filename} className="card-interactive overflow-hidden">
              <div className="aspect-[3/4] bg-gradient-to-br from-secondary to-background flex items-center justify-center border-b border-border/50">
                <BookOpen className="w-16 h-16 text-muted-foreground/30" />
              </div>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg line-clamp-1">{book.title}</CardTitle>
                <CardDescription>{formatDate(book.date)}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">Bloomberg</Badge>
                  <span className="text-sm text-muted-foreground">
                    {formatBytes(book.size_bytes)}
                  </span>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="flex-1" asChild>
                    <a 
                      href={`https://mylesmcook.github.io/bloomberg-daily/books/${book.filename}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </a>
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Eye className="w-4 h-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
