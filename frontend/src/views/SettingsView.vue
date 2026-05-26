<template>
  <div class="settings-page">
    <h2 class="page-title">设置</h2>

    <!-- Library Sources -->
    <section class="settings-section">
      <div class="section-header">
        <h3>图库源管理</h3>
        <el-button type="primary" :icon="Plus" size="small" @click="showAddDialog = true">
          添加图库源
        </el-button>
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
        <el-table-column prop="last_scan_at" label="上次扫描" width="160">
          <template #default="{ row }">
            {{ row.last_scan_at ? new Date(row.last_scan_at).toLocaleString('zh-CN') : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right">
          <template #default="{ row }">
            <el-button size="small" :loading="row.scan_status === 'scanning'" @click="onScan(row.id)">
              扫描
            </el-button>
            <el-button size="small" @click="onCheckConsistency(row.id)">校验</el-button>
            <el-popconfirm title="确定删除此图库源？照片索引也会被删除。" @confirm="onDelete(row.id)">
              <template #reference>
                <el-button size="small" type="danger" text>删除</el-button>
              </template>
            </el-popconfirm>
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

    <!-- System Status -->
    <section class="settings-section">
      <h3>系统状态</h3>
      <div v-if="sysStatus" class="status-cards">
        <div class="status-card">
          <span class="status-value">{{ sysStatus.total_photos }}</span>
          <span class="status-label">照片总数</span>
        </div>
        <div class="status-card">
          <span class="status-value">{{ sysStatus.total_libraries }}</span>
          <span class="status-label">图库源</span>
        </div>
        <div class="status-card">
          <span class="status-value">{{ sysStatus.db_size_mb.toFixed(1) }} MB</span>
          <span class="status-label">数据库</span>
        </div>
        <div class="status-card">
          <span class="status-value">{{ sysStatus.thumbnail_size_mb.toFixed(1) }} MB</span>
          <span class="status-label">缩略图</span>
        </div>
      </div>

      <div v-if="activeTasks.length > 0" class="tasks-area">
        <h4>活跃任务</h4>
        <div v-for="task in activeTasks" :key="task.id" class="task-item">
          <div class="task-header">
            <el-tag :type="task.status === 'running' ? 'primary' : 'warning'" size="small">
              {{ task.type }}
            </el-tag>
            <span class="task-msg">{{ task.message }}</span>
            <el-button
              v-if="task.status === 'running'"
              size="small"
              type="danger"
              text
              @click="onCancelTask(task.id)"
            >
              取消
            </el-button>
          </div>
          <el-progress
            :percentage="Math.round(task.progress * 100)"
            :status="task.status === 'failed' ? 'exception' : undefined"
          />
        </div>
      </div>
    </section>

    <!-- 主题设置 -->
    <section class="settings-section">
      <div class="section-header">
        <h3>主题设置</h3>
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
      <h3>系统配置</h3>
      <el-form :model="configForm" label-width="140px" size="small" class="config-form">
        <el-form-item label="扫描间隔（秒）">
          <el-input-number v-model="configForm.scan_interval" :min="10" :max="3600" />
        </el-form-item>
        <el-form-item label="缩略图质量">
          <el-slider v-model="configForm.thumbnail_quality" :min="10" :max="100" show-input style="width: 200px" />
        </el-form-item>
        <el-form-item label="文件监控">
          <el-switch v-model="configForm.watchdog_enabled" />
          <span class="switch-hint">{{ configForm.watchdog_enabled ? '已开启（实时监控文件变动）' : '已关闭' }}</span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
        </el-form-item>
      </el-form>
    </section>

    <!-- Add Library Dialog -->
    <el-dialog v-model="showAddDialog" title="添加图库源" width="480px" @closed="resetForm">
      <el-form :model="addForm" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="addForm.name" placeholder="例如：我的照片" />
        </el-form-item>
        <el-form-item label="目录路径" required>
          <el-input v-model="addForm.path" placeholder="例如：D:\Photos" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="addingLibrary" @click="onAddLibrary">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
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
  padding: var(--space-xl);
  overflow-y: auto;
  height: 100%;
}
.page-title {
  margin: 0 0 var(--space-lg);
  font-size: var(--text-2xl);
  font-weight: 700;
  letter-spacing: -0.5px;
}
.settings-section {
  margin-bottom: var(--space-2xl);
  background: var(--card-bg);
  backdrop-filter: var(--card-blur);
  -webkit-backdrop-filter: var(--card-blur);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  border: 1px solid var(--border-color);
}
.settings-section h3 {
  margin: 0 0 var(--space-md);
  font-size: var(--text-lg);
  font-weight: 600;
}
.settings-section h4 {
  margin: var(--space-md) 0 var(--space-sm);
  font-size: var(--text-sm);
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}
.section-header h3 {
  margin: 0;
}
.empty-hint {
  padding: var(--space-xl) 0;
}

/* ===== 主题选择 ===== */
.theme-options {
  display: flex;
  gap: var(--space-md);
}
.theme-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  padding: var(--space-md);
  border-radius: var(--radius-sm);
  border: 2px solid transparent;
  transition: all var(--transition-fast);
}
.theme-option:hover {
  border-color: var(--border-color-hover);
}
.theme-option.is-active {
  border-color: var(--accent);
  background: var(--accent-light);
}
.theme-preview {
  width: 120px;
  height: 80px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  border: 1px solid var(--border-color);
}
.theme-preview--light {
  background: #fff;
}
.theme-preview--dark {
  background: #1E1E1E;
}
.theme-preview--system {
  background: linear-gradient(135deg, #fff 50%, #1E1E1E 50%);
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
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-primary);
}

.progress-area {
  margin-top: var(--space-md);
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}
.progress-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.progress-label {
  font-size: var(--text-sm);
  font-weight: 500;
}
.progress-msg {
  font-size: var(--text-xs);
  color: var(--text-secondary);
}
.status-cards {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
}
.status-card {
  flex: 1;
  min-width: 160px;
  padding: var(--space-md);
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  background: var(--bg-secondary);
}
.status-value {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--accent);
  font-variant-numeric: tabular-nums;
}
.status-label {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}
.tasks-area {
  margin-top: var(--space-md);
}
.task-item {
  padding: var(--space-sm) 0;
  border-bottom: 1px solid var(--border-color);
}
.task-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: 4px;
}
.task-msg {
  flex: 1;
  font-size: var(--text-sm);
}
.config-form {
  max-width: 500px;
  margin-top: var(--space-sm);
}
.switch-hint {
  margin-left: var(--space-sm);
  font-size: var(--text-xs);
  color: var(--text-secondary);
}
</style>
