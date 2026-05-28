export type ReklamVideo = {
  id: string
  src: string
  label: string
}

export const videos: ReklamVideo[] = [
  { id: 'video-1', src: '/videos/video-1.mp4', label: '[VIDEO 1 BASLIK]' },
  { id: 'video-2', src: '/videos/video-2.mp4', label: '[VIDEO 2 BASLIK]' },
  { id: 'video-3', src: '/videos/video-3.mp4', label: '[VIDEO 3 BASLIK]' },
]
