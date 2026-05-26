export interface SystemStatus {
  total_photos: number
  total_libraries: number
  db_size_mb: number
  thumbnail_size_mb: number
  is_scanning: boolean
  active_tasks: number
}

export interface TaskInfo {
  id: string
  type: string
  status: string
  progress: number
  message: string
  library_id: number | null
  created_at: number
  updated_at: number
}

export interface SystemConfig {
  scan_interval: number
  page_size_default: number
  thumbnail_quality: number
  watchdog_enabled: boolean
}
