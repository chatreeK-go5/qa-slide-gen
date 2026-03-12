<!-- HBarChart.vue
     Reusable horizontal bar chart (SVG-based, no external dependencies).
     Used by: Production Issues slide, Beauty in Sprint slide.
-->
<script setup lang="ts">
import { computed } from 'vue'

interface Item {
  label: string
  count: number
}

const props = defineProps<{
  title: string
  total?: number
  items: Item[]
  subtitle?: string
  badgeLabel?: string
}>()

const BAR_COLORS = ['#4A7FA5', '#6E9FBF', '#92BECE', '#B4D4E2', '#D2E8F2']
const BG = '#F5F0E8'

const LEFT_PAD = 170
const RIGHT_PAD = 80
const TOP_PAD = 90
const BOTTOM_PAD = 50
const BAR_H = 38
const BAR_GAP = 18
const CHART_W = 820

const SVG_W = LEFT_PAD + CHART_W + RIGHT_PAD

const sorted = computed(() => [...props.items].sort((a, b) => b.count - a.count))
const max = computed(() => Math.max(...sorted.value.map(i => i.count), 1))
const total = computed(() => props.total ?? sorted.value.reduce((s, i) => s + i.count, 0))
const svgH = computed(() => TOP_PAD + sorted.value.length * (BAR_H + BAR_GAP) - BAR_GAP + BOTTOM_PAD)

function bw(count: number) {
  return Math.max((count / max.value) * CHART_W, 2)
}
function by(i: number) {
  return TOP_PAD + i * (BAR_H + BAR_GAP)
}
</script>

<template>
  <svg
    :width="SVG_W"
    :height="svgH"
    :viewBox="`0 0 ${SVG_W} ${svgH}`"
    xmlns="http://www.w3.org/2000/svg"
    style="max-width:100%; height:auto;"
  >
    <!-- Background -->
    <rect width="100%" height="100%" :fill="BG" rx="10"/>

    <!-- Title -->
    <text x="20" y="42" font-family="'Noto Sans', sans-serif" font-size="24"
      font-weight="bold" fill="#2C3E50">{{ title.toUpperCase() }}</text>

    <!-- Subtitle -->
    <text v-if="subtitle" x="20" y="64" font-family="'Noto Sans', sans-serif"
      font-size="13" fill="#666">{{ subtitle }}</text>

    <!-- Total badge -->
    <rect :x="SVG_W - 118" y="14" width="100" height="56" rx="10"
      fill="white" opacity="0.85" stroke="#C8B89A" stroke-width="1.5"/>
    <text :x="SVG_W - 68" y="33" font-family="'Noto Sans', sans-serif"
      font-size="11" fill="#777" text-anchor="middle">{{ badgeLabel ?? 'TOTAL' }}</text>
    <text :x="SVG_W - 68" y="60" font-family="'Noto Sans', sans-serif"
      font-size="26" font-weight="bold" fill="#2C3E50" text-anchor="middle">{{ total }}</text>

    <!-- Grid lines -->
    <g v-for="t in [1,2,3,4,5]" :key="t">
      <line
        :x1="LEFT_PAD + (t / 5) * CHART_W"
        :y1="TOP_PAD - 8"
        :x2="LEFT_PAD + (t / 5) * CHART_W"
        :y2="TOP_PAD + sorted.length * (BAR_H + BAR_GAP) - BAR_GAP + 8"
        stroke="#C0B090" stroke-width="1" stroke-dasharray="5,5" opacity="0.4"
      />
    </g>

    <!-- Bars -->
    <g v-for="(item, i) in sorted" :key="item.label">
      <!-- Row background -->
      <rect
        :x="LEFT_PAD" :y="by(i)"
        :width="CHART_W" :height="BAR_H"
        fill="white" opacity="0.2" rx="3"
      />
      <!-- Label -->
      <text
        :x="LEFT_PAD - 12" :y="by(i) + BAR_H / 2 + 5"
        font-family="'Noto Sans', sans-serif" font-size="13" fill="#333" text-anchor="end"
      >{{ item.label }}</text>
      <!-- Bar fill -->
      <rect
        :x="LEFT_PAD" :y="by(i)"
        :width="bw(item.count)" :height="BAR_H"
        :fill="BAR_COLORS[i % BAR_COLORS.length]" rx="4" opacity="0.88"
      />
      <!-- Count label -->
      <text
        :x="LEFT_PAD + bw(item.count) + 10" :y="by(i) + BAR_H / 2 + 5"
        font-family="'Noto Sans', sans-serif" font-size="13" font-weight="bold"
        fill="#333" text-anchor="start"
      >{{ item.count }}</text>
    </g>
  </svg>
</template>
