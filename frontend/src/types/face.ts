export interface FaceCluster {
  id: number
  name: string | null
  representative_face_id: number | null
  face_count: number
  cover_thumbnail: string | null
  created_at: string | null
}

export interface PhotoFace {
  id: number
  photo_id: number
  face_cluster_id: number | null
  bbox_x: number
  bbox_y: number
  bbox_w: number
  bbox_h: number
  confidence: number
  thumbnail_path: string | null
}

export interface FaceClusterDetail extends FaceCluster {
  faces: PhotoFace[]
}

export interface FaceClusterListResponse {
  items: FaceCluster[]
  total: number
}
