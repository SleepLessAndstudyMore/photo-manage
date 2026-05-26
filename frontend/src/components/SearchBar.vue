<template>
  <div class="search-bar">
    <el-input
      v-model="query"
      placeholder="搜索照片名称或路径..."
      :prefix-icon="Search"
      clearable
      @keyup.enter="$emit('search', query)"
      @clear="$emit('search', '')"
    >
      <template #append>
        <el-button :icon="Search" @click="$emit('search', query)" />
      </template>
    </el-input>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

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
</style>
