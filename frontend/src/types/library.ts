export interface LibrarySource {
  id: number
  name: string
  path: string
  type: string
  scan_status: string
  last_scan_at: string | null
  photo_count: number
  created_at: string
}

export interface ScanProgress {
  progress: number
  message: string
}
