<template>
  <el-dialog
    v-model="visible"
    title="选择目录"
    width="520px"
    class="glass-dialog"
    @open="onOpen"
  >
    <!-- 当前路径面包屑 -->
    <div class="dir-path-bar">
      <button
        class="dir-up-btn"
        :disabled="!parentPath"
        @click="goUp"
      >
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 14L4 9l5-5"/><path d="M4 9h10.5a4.5 4.5 0 014.5 4.5v0a4.5 4.5 0 01-4.5 4.5H11"/>
        </svg>
        上级
      </button>
      <div class="dir-current">{{ currentPath }}</div>
    </div>

    <!-- 目录列表 -->
    <div class="dir-list">
      <div
        v-for="item in items"
        :key="item.path"
        class="dir-item"
        @click="enterDir(item.path)"
      >
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.5" class="dir-icon">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <span class="dir-name">{{ item.name }}</span>
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" class="dir-arrow">
          <polyline points="9 18 15 12 9 6"/>
        </svg>
      </div>
      <div v-if="items.length === 0" class="dir-empty">
        没有子目录
      </div>
    </div>

    <template #footer>
      <button class="pill-btn" @click="visible = false">取消</button>
      <button class="pill-btn pill-btn--primary" @click="confirm">
        选择当前目录
      </button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { browseDirectory } from '@/api/libraries'

const visible = defineModel<boolean>('visible', { default: false })
const emit = defineEmits<{
  select: [path: string]
}>()

interface DirItem {
  name: string
  path: string
}

const currentPath = ref('')
const parentPath = ref<string | null>(null)
const items = ref<DirItem[]>([])
const loading = ref(false)

async function onOpen() {
  if (!currentPath.value) {
    await loadDir()
  }
}

async function loadDir(path?: string) {
  loading.value = true
  try {
    const res = await browseDirectory(path)
    currentPath.value = res.data.current_path
    parentPath.value = res.data.parent_path
    items.value = res.data.items
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '读取目录失败')
  } finally {
    loading.value = false
  }
}

function enterDir(path: string) {
  loadDir(path)
}

function goUp() {
  if (parentPath.value) {
    loadDir(parentPath.value)
  }
}

function confirm() {
  if (currentPath.value) {
    emit('select', currentPath.value)
    visible.value = false
  }
}
</script>

<style scoped>
.dir-path-bar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  margin-bottom: var(--space-3);
  padding: var(--space-2) var(--space-3);
  background: var(--gray-50);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}

.dir-up-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: var(--text-caption);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.dir-up-btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}

.dir-up-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.dir-current {
  flex: 1;
  font-size: var(--text-caption);
  color: var(--text-secondary);
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  user-select: all;
}

.dir-list {
  max-height: 320px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.dir-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  cursor: pointer;
  transition: background var(--transition-fast);
  border-bottom: 1px solid var(--border-color);
}

.dir-item:last-child {
  border-bottom: none;
}

.dir-item:hover {
  background: var(--accent-light);
}

.dir-icon {
  color: var(--warning-500);
  flex-shrink: 0;
}

.dir-name {
  flex: 1;
  font-size: var(--text-body);
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dir-arrow {
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.dir-empty {
  padding: var(--space-6);
  text-align: center;
  color: var(--text-secondary);
  font-size: var(--text-body);
}

.pill-btn {
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  font-size: var(--text-body);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.pill-btn:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.pill-btn--primary {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

.pill-btn--primary:hover {
  opacity: 0.9;
}
</style>
