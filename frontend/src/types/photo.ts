export interface Photo {
  id: number
  library_source_id: number | null
  file_name: string
  file_path: string
  file_size: number
  is_video: boolean
  date_taken: string | null
  thumbnail_path: string | null
  thumbnail_width: number | null
  thumbnail_height: number | null
  preview_path: string | null
  width: number | null
  height: number | null
  rating: number
  is_favorite: boolean
  file_missing: boolean
  duration: number | null
}

export interface PhotoExif {
  photo_id: number
  camera_make: string | null
  camera_model: string | null
  lens_model: string | null
  f_number: number | null
  exposure_time: string | null
  iso: number | null
  focal_length: number | null
  gps_latitude: number | null
  gps_longitude: number | null
  date_taken: string | null
  width: number | null
  height: number | null
  file_size: number
  orientation: number
}

export interface PhotoDetail extends Photo {
  camera_make: string | null
  camera_model: string | null
  lens_model: string | null
  f_number: number | null
  exposure_time: string | null
  iso: number | null
  focal_length: number | null
  gps_latitude: number | null
  gps_longitude: number | null
  orientation: number
  date_modified: string | null
  file_hash: string | null
}

export interface PhotoListParams {
  page?: number
  page_size?: number
  library_id?: number
  year?: number
  month?: number
  day?: number
  folder?: string
  sort_by?: string
  sort_order?: string
}

export interface PhotoListResponse {
  items: Photo[]
  total: number
  page: number
  page_size: number
}

export interface TimelineDay {
  day: number
  count: number
}

export interface TimelineMonth {
  month: number
  count: number
  days: TimelineDay[]
}

export interface TimelineYear {
  year: number
  count: number
  months: TimelineMonth[]
}

export interface TimelineResponse {
  years: TimelineYear[]
}

export interface FolderItem {
  path: string
  name: string
  photo_count: number
  cover_photo: Photo | null
}

export interface FolderListResponse {
  items: FolderItem[]
}
