<template>
  <div id="photo-manager-app">
    <nav class="app-nav">
      <router-link to="/timeline" class="nav-link" active-class="nav-link--active">
        <el-icon><Clock /></el-icon>
        <span>时间轴</span>
      </router-link>
      <router-link to="/folders" class="nav-link" active-class="nav-link--active">
        <el-icon><FolderOpened /></el-icon>
        <span>文件夹</span>
      </router-link>
      <router-link to="/search" class="nav-link" active-class="nav-link--active">
        <el-icon><Search /></el-icon>
        <span>搜索</span>
      </router-link>
      <router-link to="/tags" class="nav-link" active-class="nav-link--active">
        <el-icon><PriceTag /></el-icon>
        <span>标签</span>
      </router-link>
      <router-link to="/albums" class="nav-link" active-class="nav-link--active">
        <el-icon><Collection /></el-icon>
        <span>相册</span>
      </router-link>
      <router-link to="/map" class="nav-link" active-class="nav-link--active">
        <el-icon><MapLocation /></el-icon>
        <span>地图</span>
      </router-link>
      <router-link to="/duplicates" class="nav-link" active-class="nav-link--active">
        <el-icon><Delete /></el-icon>
        <span>清理</span>
      </router-link>
      <router-link to="/settings" class="nav-link" active-class="nav-link--active">
        <el-icon><Setting /></el-icon>
        <span>设置</span>
      </router-link>
    </nav>
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { Clock, FolderOpened, Search, PriceTag, Collection, MapLocation, Delete, Setting } from '@element-plus/icons-vue'
import { useSystemStore } from '@/stores/system'

onMounted(() => {
  useSystemStore().connectWs()
})
</script>

<style>
.app-nav {
  display: flex;
  align-items: center;
  height: 52px;
  padding: 0 20px;
  background: var(--color-bg-primary, #fff);
  border-bottom: 1px solid var(--color-border, #e8e8e8);
  gap: 4px;
  flex-shrink: 0;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
  color: var(--color-text-secondary, #666);
  text-decoration: none;
  font-size: 14px;
  transition: background 0.15s, color 0.15s;
}
.nav-link:hover {
  background: var(--color-bg-hover, #f0f0f0);
}
.nav-link--active {
  color: var(--color-primary, #7EC8C8);
  background: var(--color-primary-light, #e6f7f7);
  font-weight: 600;
}
.app-main {
  flex: 1;
  overflow: hidden;
}
</style>
