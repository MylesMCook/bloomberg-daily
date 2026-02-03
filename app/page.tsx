import { Book, Clock, Rss, Activity, Cpu, Building2, Newspaper } from "lucide-react"

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-[#1a1a2e] to-[#16213e] text-[#e4e4e4] flex items-center justify-center p-5">
      <div className="max-w-[600px] text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-2 bg-gradient-to-r from-[#667eea] to-[#764ba2] bg-clip-text text-transparent">
          Bloomberg Daily Briefing
        </h1>
        <p className="text-[#888] mb-8 text-lg">
          Curated news for e-ink readers
        </p>

        {/* OPDS Feed Card */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 mb-6">
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="flex items-center gap-2">
              <Rss className="w-4 h-4" />
              OPDS Feed Available
            </span>
          </div>
          <div className="font-mono bg-black/30 p-4 rounded-lg text-[#a5d6a7] text-sm break-all my-4">
            https://mylesmcook.github.io/bloomberg-daily/opds.xml
          </div>
          <p className="text-[#888] text-sm">
            Add this URL to your e-reader&apos;s OPDS browser
          </p>
        </div>

        {/* Sections Card */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 mb-6">
          <p className="font-semibold mb-4 flex items-center justify-center gap-2">
            <Book className="w-4 h-4" />
            Sections Included
          </p>
          <div className="flex gap-2 justify-center flex-wrap">
            <SectionTag icon={<Cpu className="w-3.5 h-3.5" />} label="AI" />
            <SectionTag icon={<Activity className="w-3.5 h-3.5" />} label="Technology" />
            <SectionTag icon={<Building2 className="w-3.5 h-3.5" />} label="Industries" />
            <SectionTag icon={<Newspaper className="w-3.5 h-3.5" />} label="Latest" />
          </div>
        </div>

        {/* Schedule Card */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 mb-6">
          <p className="font-semibold flex items-center justify-center gap-2">
            <Clock className="w-4 h-4" />
            Schedule: Weekdays at 6:00 AM CST
          </p>
          <p className="text-[#888] text-sm mt-2">
            Rolling 7-day archive maintained automatically
          </p>
        </div>

        {/* Footer */}
        <p className="text-[#666] text-sm mt-8">
          Powered by{" "}
          <a
            href="https://github.com/MylesMCook/bloomberg-daily"
            className="text-[#667eea] hover:underline"
          >
            GitHub Actions
          </a>
          {" "}&middot;{" "}
          Optimized for CrossPoint OS
        </p>
      </div>
    </main>
  )
}

function SectionTag({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <span className="bg-[#667eea]/20 text-[#a5b4fc] px-3 py-1.5 rounded-full text-sm flex items-center gap-1.5">
      {icon}
      {label}
    </span>
  )
}
