import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/timeline' },
  {
    path: '/timeline',
    name: 'timeline',
    component: () => import('@/views/TimelineView.vue'),
  },
  {
    path: '/folders',
    name: 'folders',
    component: () => import('@/views/FolderView.vue'),
  },
  {
    path: '/search',
    name: 'search',
    component: () => import('@/views/SearchView.vue'),
  },
  {
    path: '/map',
    name: 'map',
    component: () => import('@/views/MapView.vue'),
  },
  {
    path: '/people',
    name: 'people',
    component: () => import('@/views/PeopleView.vue'),
  },
  {
    path: '/tags',
    name: 'tags',
    component: () => import('@/views/TagsView.vue'),
  },
  {
    path: '/settings',
    name: 'settings',
    component: () => import('@/views/SettingsView.vue'),
  },
  {
    path: '/photos/:id',
    name: 'photo-detail',
    component: () => import('@/views/PhotoDetailView.vue'),
    meta: { title: '照片详情' },
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

export default router
