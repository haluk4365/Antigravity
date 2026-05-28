import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { videos } from '../_videos'

export const dynamicParams = false

export async function generateStaticParams() {
  return videos.map((v) => ({ id: v.id }))
}

export async function generateMetadata(
  props: { params: Promise<{ id: string }> }
): Promise<Metadata> {
  const params = await props.params
  const video = videos.find((v) => v.id === params.id)
  return {
    title: video?.label ?? `Reklam ${params.id}`,
    robots: { index: false, follow: false },
  }
}

export default async function ReklamTekVideoPage(
  props: { params: Promise<{ id: string }> }
) {
  const params = await props.params
  const video = videos.find((v) => v.id === params.id)
  if (!video) notFound()

  return (
    <div className="min-h-screen pt-24 pb-24 relative">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-[#4F8BFF]/5 blur-[150px] rounded-full pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-[#4F8BFF]/5 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-xl mx-auto px-4 sm:px-6 relative z-10">
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-white text-center mb-8">
          {video.label}
        </h1>

        <div className="mx-auto w-full max-w-sm">
          <video
            controls
            playsInline
            preload="metadata"
            autoPlay={false}
            className="w-full rounded-2xl shadow-2xl bg-black aspect-[9/16] object-cover"
          >
            <source src={video.src} type="video/mp4" />
          </video>
        </div>
      </div>
    </div>
  )
}
