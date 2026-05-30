import { createRouter, createWebHashHistory } from 'vue-router'

function lazyLoad(factory: () => Promise<any>) {
  return async () => {
    try {
      return await factory()
    } catch (err) {
      // 动态 chunk 加载失败（通常是缓存了旧 index.html），自动刷新
      const isChunkError =
        err instanceof Error &&
        /Failed to fetch dynamically imported module|Loading chunk/.test(err.message)
      if (isChunkError && !sessionStorage.getItem('reloaded')) {
        sessionStorage.setItem('reloaded', '1')
        window.location.reload()
        return
      }
      throw err
    }
  }
}

const routes = [
  { path: '/', redirect: '/timeline' },
  {
    path: '/timeline',
    name: 'timeline',
    component: lazyLoad(() => import('@/views/TimelineView.vue')),
  },
  {
    path: '/folders',
    name: 'folders',
    component: lazyLoad(() => import('@/views/FolderView.vue')),
  },
  {
    path: '/search',
    name: 'search',
    component: lazyLoad(() => import('@/views/SearchView.vue')),
  },
  {
    path: '/map',
    name: 'map',
    component: lazyLoad(() => import('@/views/MapView.vue')),
  },
  {
    path: '/people',
    name: 'people',
    component: lazyLoad(() => import('@/views/PeopleView.vue')),
  },
  {
    path: '/tags',
    name: 'tags',
    component: lazyLoad(() => import('@/views/TagsView.vue')),
  },
  {
    path: '/albums',
    name: 'albums',
    component: lazyLoad(() => import('@/views/AlbumsView.vue')),
  },
  {
    path: '/duplicates',
    name: 'duplicates',
    component: lazyLoad(() => import('@/views/DuplicatesView.vue')),
  },
  {
    path: '/albums/:id',
    name: 'album-detail',
    component: lazyLoad(() => import('@/views/AlbumDetailView.vue')),
    meta: { title: '相册详情' },
  },
  {
    path: '/people/:id',
    name: 'people-detail',
    component: lazyLoad(() => import('@/views/PeopleDetailView.vue')),
    meta: { title: '人物详情' },
  },
  {
    path: '/settings',
    name: 'settings',
    component: lazyLoad(() => import('@/views/SettingsView.vue')),
  },
  {
    path: '/photos/:id',
    name: 'photo-detail',
    component: lazyLoad(() => import('@/views/PhotoDetailView.vue')),
    meta: { title: '照片详情' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
