<template>
  <div class="segmented-control" ref="containerRef">
    <div class="segmented-slider" :style="sliderStyle" />
    <button
      v-for="(opt, i) in options"
      :key="opt.value"
      ref="btnRefs"
      class="segmented-item"
      :class="{ active: modelValue === opt.value }"
      @click="$emit('update:modelValue', opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted, computed } from 'vue'

interface Option {
  label: string
  value: string
}

const props = defineProps<{
  options: Option[]
  modelValue: string
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()

const containerRef = ref<HTMLElement | null>(null)
const btnRefs = ref<HTMLElement[]>([])
const sliderStyle = ref({})

function updateSlider() {
  const idx = props.options.findIndex(o => o.value === props.modelValue)
  if (idx < 0 || !btnRefs.value[idx] || !containerRef.value) return
  const btn = btnRefs.value[idx]
  const container = containerRef.value
  sliderStyle.value = {
    width: `${btn.offsetWidth}px`,
    transform: `translateX(${btn.offsetLeft - container.offsetLeft}px)`,
  }
}

watch(() => props.modelValue, () => nextTick(updateSlider))
onMounted(() => nextTick(updateSlider))
</script>

<style scoped>
.segmented-control {
  display: inline-flex;
  position: relative;
  gap: 2px;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 9px;
  padding: 3px;
}

[data-theme="dark"] .segmented-control {
  background: rgba(255, 255, 255, 0.06);
}

.segmented-slider {
  position: absolute;
  top: 3px;
  left: 3px;
  height: calc(100% - 6px);
  border-radius: 7px;
  background: var(--card-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: var(--shadow-sm);
  transition: transform 0.3s var(--ease-apple), width 0.3s var(--ease-apple);
  z-index: 0;
}

.segmented-item {
  position: relative;
  z-index: 1;
  padding: 5px 16px;
  border-radius: 7px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: color var(--transition-fast);
  white-space: nowrap;
}

.segmented-item.active {
  color: var(--text-primary);
}

.segmented-item:hover:not(.active) {
  color: var(--text-primary);
}
</style>
