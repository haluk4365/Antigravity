import type { Metadata } from 'next'
import { videos } from './_videos'

export const metadata: Metadata = {
  title: 'Reklam Videoları',
  robots: { index: false, follow: false },
}

export default function ReklamlarTopluPage() {
  return (
    <div className="min-h-screen pt-24 pb-24 relative">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-[#4F8BFF]/5 blur-[150px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-[#4F8BFF]/5 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-6xl mx-auto px-4 sm:px-6 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-6">
          {videos.map((v) => (
            <div key={v.id} className="space-y-4">
              <h2 className="text-base sm:text-lg font-semibold tracking-tight text-white text-center">
                {v.label}
              </h2>
              <video
                controls
                playsInline
                preload="metadata"
                className="w-full rounded-2xl shadow-2xl bg-black aspect-[9/16] object-cover"
              >
                <source src={v.src} type="video/mp4" />
              </video>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
