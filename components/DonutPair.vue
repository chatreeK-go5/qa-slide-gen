<!-- DonutPair.vue
     Two donut charts rendered side by side (SVG-based, no external dependencies).
     Used by: Summary by Priority slide.
-->
<script setup lang="ts">
import { computed } from 'vue'

interface PrioritySlice {
  label: string
  count: number
}

interface PieSection {
  label: string
  total: number
  priorities: PrioritySlice[]
}

const props = defineProps<{
  title: string
  left: PieSection
  right: PieSection
}>()

const PRIORITY_COLORS: Record<string, string> = {
  Highest: '#C0392B',
  High:    '#E67E22',
  Medium:  '#27AE60',
  Low:     '#2980B9',
  Lowest:  '#95A5A6',
}

const BG = '#F5F0E8'
const SVG_W = 1060
const SVG_H = 520
const CX_LEFT = 280
const CX_RIGHT = 780
const CY = 250
const R_OUTER = 150
const R_INNER = 82

function slicePath(cx: number, cy: number, r1: number, r2: number, start: number, end: number): string {
  // Clamp to avoid full-circle edge case
  const delta = Math.min(end - start, 2 * Math.PI - 0.001)
  const s = start - Math.PI / 2
  const e = s + delta
  const x1 = cx + r1 * Math.cos(s)
  const y1 = cy + r1 * Math.sin(s)
  const x2 = cx + r1 * Math.cos(e)
  const y2 = cy + r1 * Math.sin(e)
  const x3 = cx + r2 * Math.cos(e)
  const y3 = cy + r2 * Math.sin(e)
  const x4 = cx + r2 * Math.cos(s)
  const y4 = cy + r2 * Math.sin(s)
  const large = delta > Math.PI ? 1 : 0
  return `M ${x1} ${y1} A ${r1} ${r1} 0 ${large} 1 ${x2} ${y2} L ${x3} ${y3} A ${r2} ${r2} 0 ${large} 0 ${x4} ${y4} Z`
}

function labelPos(cx: number, cy: number, start: number, span: number) {
  const mid = start - Math.PI / 2 + span / 2
  const r = (R_OUTER + R_INNER) / 2
  return { x: cx + r * Math.cos(mid), y: cy + r * Math.sin(mid) }
}

function buildSlices(section: PieSection, cx: number) {
  const total = section.priorities.reduce((s, p) => s + p.count, 0)
  let angle = 0
  return section.priorities.map(p => {
    const span = (p.count / (total || 1)) * 2 * Math.PI
    const start = angle
    angle += span
    return {
      label: p.label,
      count: p.count,
      color: PRIORITY_COLORS[p.label] ?? '#AAAAAA',
      path: slicePath(cx, CY, R_OUTER, R_INNER, start, start + span),
      labelPos: labelPos(cx, CY, start, span),
      showLabel: p.count > 0,
    }
  })
}

const leftSlices = computed(() => buildSlices(props.left, CX_LEFT))
const rightSlices = computed(() => buildSlices(props.right, CX_RIGHT))

// Legend entries (from left section as canonical)
const legendEntries = computed(() => {
  const all = [...props.left.priorities, ...props.right.priorities]
  const seen = new Set<string>()
  return all.filter(p => { const ok = !seen.has(p.label); seen.add(p.label); return ok })
    .map(p => ({ label: p.label, color: PRIORITY_COLORS[p.label] ?? '#AAAAAA' }))
})
</script>

<template>
  <svg
    :width="SVG_W"
    :height="SVG_H"
    :viewBox="`0 0 ${SVG_W} ${SVG_H}`"
    xmlns="http://www.w3.org/2000/svg"
    style="max-width:100%; height:auto;"
  >
    <!-- Background -->
    <rect width="100%" height="100%" :fill="BG" rx="10"/>

    <!-- Main title -->
    <text x="530" y="42" font-family="'Noto Sans', sans-serif" font-size="24"
      font-weight="bold" fill="#2C3E50" text-anchor="middle">{{ title.toUpperCase() }}</text>

    <!-- LEFT donut -->
    <g>
      <text :x="CX_LEFT" y="90" font-family="'Noto Sans', sans-serif" font-size="18"
        font-weight="bold" fill="#2C3E50" text-anchor="middle">{{ left.label }}</text>
      <!-- Slices -->
      <path
        v-for="sl in leftSlices" :key="sl.label"
        :d="sl.path" :fill="sl.color" opacity="0.9"
        stroke="white" stroke-width="2"
      />
      <!-- Centre total -->
      <text :x="CX_LEFT" :y="CY + 10" font-family="'Noto Sans', sans-serif"
        font-size="36" font-weight="bold" fill="#2C3E50" text-anchor="middle">{{ left.total }}</text>
      <!-- Slice labels -->
      <text
        v-for="sl in leftSlices.filter(s => s.showLabel)" :key="`lbl-${sl.label}`"
        :x="sl.labelPos.x" :y="sl.labelPos.y + 5"
        font-family="'Noto Sans', sans-serif" font-size="13" font-weight="bold"
        fill="white" text-anchor="middle"
      >{{ sl.count }}</text>
    </g>

    <!-- RIGHT donut -->
    <g>
      <text :x="CX_RIGHT" y="90" font-family="'Noto Sans', sans-serif" font-size="18"
        font-weight="bold" fill="#2C3E50" text-anchor="middle">{{ right.label }}</text>
      <!-- Slices -->
      <path
        v-for="sl in rightSlices" :key="sl.label"
        :d="sl.path" :fill="sl.color" opacity="0.9"
        stroke="white" stroke-width="2"
      />
      <!-- Centre total -->
      <text :x="CX_RIGHT" :y="CY + 10" font-family="'Noto Sans', sans-serif"
        font-size="36" font-weight="bold" fill="#2C3E50" text-anchor="middle">{{ right.total }}</text>
      <!-- Slice labels -->
      <text
        v-for="sl in rightSlices.filter(s => s.showLabel)" :key="`lbl-${sl.label}`"
        :x="sl.labelPos.x" :y="sl.labelPos.y + 5"
        font-family="'Noto Sans', sans-serif" font-size="13" font-weight="bold"
        fill="white" text-anchor="middle"
      >{{ sl.count }}</text>
    </g>

    <!-- Legend -->
    <g v-for="(entry, li) in legendEntries" :key="entry.label">
      <rect
        :x="120 + li * 165" y="468"
        width="18" height="18"
        :fill="entry.color" rx="3" opacity="0.9"
      />
      <text
        :x="120 + li * 165 + 26" y="482"
        font-family="'Noto Sans', sans-serif" font-size="13" fill="#333"
      >{{ entry.label }}</text>
    </g>
  </svg>
</template>
