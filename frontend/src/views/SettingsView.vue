<template>
  <div class="settings-page">
    <h2 class="page-title">设置</h2>

    <!-- System Status — 统计卡片 -->
    <section class="settings-section">
      <h3 class="section-title">系统状态</h3>
      <div v-if="sysStatus" class="status-cards">
        <div class="status-card">
          <div class="status-card-header">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
            </svg>
            <span class="status-label">照片总数</span>
          </div>
          <span class="status-value">{{ sysStatus.total_photos }}</span>
        </div>
        <div class="status-card">
          <div class="status-card-header">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
            <span class="status-label">图库源</span>
          </div>
          <span class="status-value">{{ sysStatus.total_libraries }}</span>
        </div>
        <div class="status-card">
          <div class="status-card-header">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
            </svg>
            <span class="status-label">数据库</span>
          </div>
          <span class="status-value">{{ sysStatus.db_size_mb.toFixed(1) }}<span class="status-unit">MB</span></span>
        </div>
        <div class="status-card">
          <div class="status-card-header">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
            </svg>
            <span class="status-label">缩略图</span>
          </div>
          <span class="status-value">{{ sysStatus.thumbnail_size_mb.toFixed(1) }}<span class="status-unit">MB</span></span>
        </div>
      </div>

      <div v-if="activeTasks.length > 0" class="tasks-area">
        <h4 class="tasks-title">活跃任务</h4>
        <div v-for="task in activeTasks" :key="task.id" class="task-item">
          <div class="task-header">
            <span class="task-type-badge" :class="task.status">{{ task.type }}</span>
            <span class="task-msg">{{ task.message }}</span>
            <button
              v-if="task.status === 'running'"
              class="pill-btn pill-btn--danger"
              @click="onCancelTask(task.id)"
            >
              取消
            </button>
          </div>
          <el-progress
            :percentage="Math.round(task.progress * 100)"
            :status="task.status === 'failed' ? 'exception' : undefined"
          />
        </div>
      </div>
    </section>

    <!-- Library Sources -->
    <section class="settings-section">
      <div class="section-header">
        <h3 class="section-title">图库源管理</h3>
        <button class="pill-btn pill-btn--primary" @click="showAddDialog = true">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          添加图库源
        </button>
      </div>
      <el-table v-if="libraries.length > 0" :data="libraries" stripe style="width: 100%">
        <el-table-column prop="name" label="名称" min-width="120" />
        <el-table-column prop="path" label="路径" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.scan_status)" size="small">
              {{ statusLabel(row.scan_status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="photo_count" label="照片数" width="80" />
        <el-table-column prop="last_scan_at" label="上次扫描" width="280">
          <template #default="{ row }">
            {{ row.last_scan_at ? new Date(row.last_scan_at).toLocaleString('zh-CN') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="200" fixed="right">
          <template #default="{ row }">
            <div class="op-btns">
              <button class="pill-btn pill-btn--sm" :disabled="row.scan_status === 'scanning'" @click="onScan(row.id)">
                <span v-if="row.scan_status === 'scanning'" class="spinner-sm" />
                扫描
              </button>
              <button class="pill-btn pill-btn--sm" @click="onCheckConsistency(row.id)">校验</button>
              <el-popconfirm title="确定删除此图库源？照片索引也会被删除。" @confirm="onDelete(row.id)">
                <template #reference>
                  <button class="pill-btn pill-btn--sm pill-btn--danger">删除</button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>
      <div v-else class="empty-hint">
        <el-empty description="暂无图库源，请添加一个本地照片目录" />
      </div>

      <div v-if="showProgress" class="progress-area">
        <div v-for="[libId, prog] in scanProgressEntries" :key="libId" class="progress-item">
          <span class="progress-label">{{ getLibraryName(libId) }}</span>
          <el-progress :percentage="Math.round(prog.progress * 100)" />
          <span class="progress-msg">{{ prog.message }}</span>
        </div>
      </div>
    </section>

    <!-- 主题设置 -->
    <section class="settings-section">
      <div class="section-header">
        <h3 class="section-title">主题设置</h3>
      </div>
      <div class="theme-options">
        <div
          v-for="opt in themeOptions"
          :key="opt.value"
          class="theme-option"
          :class="{ 'is-active': currentTheme === opt.value }"
          @click="setTheme(opt.value)"
        >
          <div class="theme-preview" :class="`theme-preview--${opt.value}`">
            <div class="theme-preview-bar" />
            <div class="theme-preview-content">
              <div class="theme-preview-dot" />
              <div class="theme-preview-lines">
                <div class="theme-preview-line" />
                <div class="theme-preview-line short" />
              </div>
            </div>
          </div>
          <span class="theme-option-label">{{ opt.label }}</span>
        </div>
      </div>
    </section>

    <!-- System Config -->
    <section class="settings-section">
      <h3 class="section-title">系统配置</h3>
      <div class="config-grid">
        <div class="config-item">
          <div class="config-label">扫描间隔（秒）</div>
          <div class="config-control">
            <el-input-number v-model="configForm.scan_interval" :min="10" :max="3600" size="default" />
          </div>
        </div>
        <div class="config-item">
          <div class="config-label">缩略图质量</div>
          <div class="config-control">
            <el-slider v-model="configForm.thumbnail_quality" :min="10" :max="100" style="width: 220px" />
            <span class="config-value">{{ configForm.thumbnail_quality }}%</span>
          </div>
        </div>
        <div class="config-item">
          <div class="config-label">文件监控</div>
          <div class="config-control">
            <el-switch v-model="configForm.watchdog_enabled" />
            <span class="switch-hint">{{ configForm.watchdog_enabled ? '已开启（实时监控文件变动）' : '已关闭' }}</span>
          </div>
        </div>
      </div>
      <div class="config-actions">
        <button type="button" class="pill-btn pill-btn--primary" @click="saveConfig">保存配置</button>
      </div>
    </section>

    <!-- Add Library Dialog -->
    <el-dialog v-model="showAddDialog" title="添加图库源" width="480px" class="glass-dialog" @closed="resetForm">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="addForm.name" placeholder="例如：我的照片" />
        </el-form-item>
        <el-form-item label="目录路径" required>
          <el-input v-model="addForm.path" placeholder="例如：D:\Photos" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="pill-btn" @click="showAddDialog = false">取消</button>
        <button class="pill-btn pill-btn--primary" :disabled="addingLibrary" @click="onAddLibrary">
          <span v-if="addingLibrary" class="spinner-sm" />
          确认添加
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useLibraryStore } from '@/stores/library'
import { useSystemStore } from '@/stores/system'
import { cancelTask } from '@/api/system'

const libraryStore = useLibraryStore()
const systemStore = useSystemStore()

const showAddDialog = ref(false)
const addingLibrary = ref(false)
const addForm = ref({ name: '', path: '' })
const currentTheme = ref(localStorage.getItem('theme') || 'system')
const themeOptions = [
  { value: 'light', label: '浅色模式' },
  { value: 'dark', label: '深色模式' },
  { value: 'system', label: '跟随系统' },
]

function setTheme(t: string) {
  currentTheme.value = t
  localStorage.setItem('theme', t)
  if (typeof (window as any).__setTheme === 'function') {
    ;(window as any).__setTheme(t)
  }
}

const libraries = computed(() => libraryStore.libraries)
const scanProgress = computed(() => libraryStore.scanProgress)
const sysStatus = computed(() => systemStore.status)

const scanProgressEntries = computed(() => {
  const entries: [number, { progress: number; message: string }][] = []
  for (const [k, v] of scanProgress.value.entries()) {
    entries.push([k, v])
  }
  return entries
})

const showProgress = computed(() =>
  scanProgressEntries.value.some(([, v]) => v.progress > 0)
)

const configForm = ref({
  scan_interval: 300,
  thumbnail_quality: 80,
  watchdog_enabled: false,
})

const activeTasks = computed(() =>
  systemStore.tasks.filter(t => t.status === 'running' || t.status === 'pending')
)

onMounted(async () => {
  await libraryStore.fetchLibraries()
  await systemStore.fetchStatus()
  await systemStore.fetchConfig()
  configForm.value = { ...systemStore.config }
  systemStore.connectWs()
})

function statusTagType(status: string) {
  const map: Record<string, string> = {
    idle: 'info', scanning: 'warning', completed: 'success', error: 'danger',
  }
  return map[status] || 'info'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    idle: '待扫描', scanning: '扫描中', completed: '已完成', error: '扫描失败',
  }
  return map[status] || status
}

function getLibraryName(id: number): string {
  return libraries.value.find(l => l.id === id)?.name || `图库 #${id}`
}

async function onAddLibrary() {
  if (!addForm.value.name.trim() || !addForm.value.path.trim()) {
    ElMessage.warning('请填写名称和路径')
    return
  }
  addingLibrary.value = true
  try {
    await libraryStore.add(addForm.value.name.trim(), addForm.value.path.trim())
    showAddDialog.value = false
    ElMessage.success('图库源已添加，扫描已启动')
    await systemStore.fetchStatus()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '添加失败')
  } finally {
    addingLibrary.value = false
  }
}

function resetForm() {
  addForm.value = { name: '', path: '' }
}

async function onScan(id: number) {
  try {
    await libraryStore.triggerScan(id)
    ElMessage.info('扫描已启动')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '启动扫描失败')
  }
}

async function onCheckConsistency(id: number) {
  try {
    await libraryStore.triggerCheckConsistency(id)
    ElMessage.info('一致性校验已启动')
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '启动校验失败')
  }
}

async function onDelete(id: number) {
  try {
    await libraryStore.remove(id)
    ElMessage.success('图库源已删除')
    await systemStore.fetchStatus()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

async function onCancelTask(taskId: string) {
  try {
    await cancelTask(taskId)
    await systemStore.fetchTasks()
  } catch { /* ignore */ }
}

async function saveConfig() {
  try {
    await systemStore.updateConfig({
      scan_interval: configForm.value.scan_interval,
      thumbnail_quality: configForm.value.thumbnail_quality,
      watchdog_enabled: configForm.value.watchdog_enabled,
    })
    ElMessage.success('配置已保存')
  } catch {
    ElMessage.error('保存配置失败')
  }
}
</script>

<style scoped>
.settings-page {
  max-width: 960px;
  margin: 0 auto;
  padding: var(--space-8);
  overflow-y: auto;
  height: 100%;
}

.page-title {
  margin: 0 0 var(--space-8);
  font-size: var(--text-h1);
  font-weight: var(--font-weight-bold);
  letter-spacing: var(--tracking-tight);
}

/* ===== 设置区块 ===== */
.settings-section {
  margin-bottom: var(--space-6);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--space-6);
}

.section-title {
  margin: 0 0 var(--space-4);
  font-size: var(--text-h3);
  font-weight: var(--font-weight-semibold);
  letter-spacing: var(--tracking-tight);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.section-title::before {
  content: '';
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: var(--accent);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.section-header .section-title {
  margin: 0;
}

.tasks-title {
  margin: var(--space-4) 0 var(--space-2);
  font-size: var(--text-caption);
  font-weight: var(--font-weight-medium);
  color: var(--text-secondary);
}

.empty-hint {
  padding: var(--space-6) 0;
}

.spinner-sm {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

/* ===== 系统状态 — 统计卡片 ===== */
.status-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--space-4);
}

.status-card {
  padding: 20px;
  border-radius: var(--radius-lg);
  background: var(--gray-50);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  transition: all var(--transition-fast);
  cursor: default;
}

.status-card:hover {
  background: var(--bg-card);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.status-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-card-header svg {
  color: var(--accent);
}

.status-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-value {
  font-size: 28px;
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  letter-spacing: var(--tracking-tight);
  line-height: 1.2;
}

.status-unit {
  font-size: var(--text-body);
  font-weight: var(--font-weight-regular);
  margin-left: 2px;
  opacity: 0.6;
}

.tasks-area {
  margin-top: var(--space-4);
}

.task-item {
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--border-color);
}

.task-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-bottom: var(--space-1);
}

.task-type-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--text-caption);
  font-weight: var(--font-weight-semibold);
  background: var(--accent-light);
  color: var(--accent);
}

.task-type-badge.warning {
  background: var(--warning-100);
  color: var(--warning-500);
}

.task-msg {
  flex: 1;
  font-size: var(--text-body);
}

/* ===== 主题选择 ===== */
.theme-options {
  display: flex;
  gap: var(--space-4);
}

.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
  padding: var(--space-3);
  border-radius: var(--radius-sm);
  border: 2px solid var(--border-color);
  transition: all var(--transition-fast);
}

.theme-option:hover {
  border-color: var(--accent);
}

.theme-option.is-active {
  border-color: var(--accent);
  background: var(--accent-light);
}

.theme-preview {
  width: 120px;
  height: 80px;
  border-radius: var(--radius-xs);
  overflow: hidden;
  border: 1px solid var(--border-color);
}

.theme-preview--light {
  background: linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%);
}

.theme-preview--dark {
  background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
}

.theme-preview--system {
  background: linear-gradient(135deg, #F9FAFB 50%, #0F172A 50%);
}

.theme-preview-bar {
  height: 16px;
  background: var(--accent);
  opacity: 0.2;
}

.theme-preview-content {
  padding: 8px;
  display: flex;
  gap: 6px;
  align-items: flex-start;
}

.theme-preview-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent);
  flex-shrink: 0;
  margin-top: 3px;
}

.theme-preview-lines {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.theme-preview-line {
  height: 4px;
  border-radius: 2px;
  background: var(--border-color);
}

.theme-preview-line.short {
  width: 60%;
}

.theme-option-label {
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.progress-area {
  margin-top: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.progress-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.progress-label {
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
}

.progress-msg {
  font-size: var(--text-caption);
  color: var(--text-secondary);
}

/* ===== 操作按钮 ===== */
.op-btns {
  display: flex;
  gap: var(--space-2);
  align-items: center;
}

.pill-btn--sm {
  padding: var(--space-1) var(--space-3);
  font-size: var(--text-caption);
  border-radius: var(--radius-sm);
}

.pill-btn--danger {
  color: var(--danger-500);
}

.pill-btn--danger:hover {
  background: var(--danger-100);
  color: var(--danger-500);
}

.spinner-sm {
  width: 12px;
  height: 12px;
  border: 1.5px solid var(--border-color);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
  margin-right: var(--space-1);
}

.config-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  max-width: 480px;
}

.config-item {
  display: flex;
  align-items: center;
  gap: var(--space-8);
}

.config-label {
  font-size: var(--text-body);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
  min-width: 120px;
  flex-shrink: 0;
}

.config-control {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex: 1;
}

.config-value {
  font-size: var(--text-body);
  color: var(--text-secondary);
  min-width: 36px;
  font-variant-numeric: tabular-nums;
}

.config-actions {
  margin-top: var(--space-6);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-color);
}

.switch-hint {
  margin-left: var(--space-2);
  font-size: var(--text-caption);
  color: var(--text-secondary);
}

:deep(.glass-dialog .el-dialog) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
