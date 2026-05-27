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
import { ref, watch, nextTick, onMounted } from 'vue'

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
  if (idx < 0 || !btnRefs.value[idx]) return
  const btn = btnRefs.value[idx]
  sliderStyle.value = {
    width: `${btn.offsetWidth}px`,
    left: `${btn.offsetLeft}px`,
  }
}

watch(() => props.modelValue, () => nextTick(updateSlider))
onMounted(() => nextTick(updateSlider))
</script>

<style scoped>
.segmented-control {
  display: inline-flex;
  position: relative;
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 2px;
}

[data-theme="dark"] .segmented-control {
  background: rgba(255, 255, 255, 0.08);
}

.segmented-slider {
  position: absolute;
  top: 2px;
  height: calc(100% - 4px);
  border-radius: 6px;
  background: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 1px 2px rgba(0, 0, 0, 0.04);
  transition: left 0.25s var(--ease-apple), width 0.25s var(--ease-apple);
  z-index: 0;
}

[data-theme="dark"] .segmented-slider {
  background: rgba(50, 50, 54, 0.9);
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.segmented-item {
  position: relative;
  z-index: 1;
  padding: 5px 16px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
  cursor: pointer;
  transition: color 0.2s var(--ease-apple);
  white-space: nowrap;
  line-height: 1.4;
}

.segmented-item.active {
  color: var(--text-primary);
  font-weight: 600;
}

.segmented-item:hover:not(.active) {
  color: var(--text-primary);
}
</style>
