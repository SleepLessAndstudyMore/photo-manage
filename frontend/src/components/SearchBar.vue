<template>
  <div class="search-bar">
    <div class="search-bar-inner">
      <svg class="search-icon" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
      <input
        v-model="query"
        placeholder="搜索照片名称或路径..."
        class="search-input"
        @keyup.enter="$emit('search', query)"
      />
      <button v-if="query" class="search-clear" @click="query = ''; $emit('search', '')">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineEmits<{
  search: [query: string]
}>()

const query = ref('')
</script>

<style scoped>
.search-bar {
  width: 100%;
  max-width: 400px;
}

.search-bar-inner {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 8px 16px;
  border-radius: 100px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
}

.search-bar-inner:focus-within {
  border-color: var(--accent);
  box-shadow: 0 0 0 3px var(--accent-light);
}

.search-icon {
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: var(--text-sm);
  color: var(--text-primary);
  font-family: inherit;
}

.search-input::placeholder {
  color: var(--text-tertiary);
}

.search-clear {
  border: none;
  background: transparent;
  cursor: pointer;
  color: var(--text-tertiary);
  padding: 2px;
  display: flex;
  align-items: center;
  transition: color var(--transition-fast);
}

.search-clear:hover {
  color: var(--text-primary);
}
</style>
