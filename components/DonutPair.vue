<!-- DonutPair.vue
     Two donut charts side by side (SVG). Used by: Summary by Priority slide.
     Props:
       title  – slide title
       charts – [{ label, total, priorities: [{ label, count }] }, ...]  (exactly 2 elements)
-->
<script setup lang="ts">
import { computed } from 'vue'

interface PrioritySlice { label: string; count: number }
interface ChartSection  { label: string; total: number; priorities: PrioritySlice[] }

const props = defineProps<{
  title: string
  charts: ChartSection[]
}>()

const PRIORITY_COLORS: Record<string, string> = {
  Highest: '#C0392B',
  High:    '#E67E22',
  Medium:  '#27AE60',
  Low:     '#2980B9',
  Lowest:  '#95A5A6',
}

// ── layout ───────────────────────────────────────────────────────────────────
const SVG_W  = 1100
const SVG_H  = 560
const CY     = 290
const R_OUT  = 165
const R_IN   = 92
const TITLE_Y = 46
const CHART_LABEL_Y = 92

// Two chart centres, evenly spaced
const cx = computed(() => {
  if (props.charts.length === 2) return [SVG_W * 0.27, SVG_W * 0.73]
  const step = SVG_W / (props.charts.length + 1)
  return props.charts.map((_, i) => step * (i + 1))
})

// ── SVG arc maths ─────────────────────────────────────────────────────────────
function slicePath(
  cx: number, cy: number, r1: number, r2: number,
  start: number, span: number
): string {
  const clampedSpan = Math.min(span, Math.PI * 2 - 0.001)
  const s = start - Math.PI / 2
  const e = s + clampedSpan
  const cos = Math.cos, sin = Math.sin
  const large = clampedSpan > Math.PI ? 1 : 0
  const x1 = cx + r1 * cos(s), y1 = cy + r1 * sin(s)
  const x2 = cx + r1 * cos(e), y2 = cy + r1 * sin(e)
  const x3 = cx + r2 * cos(e), y3 = cy + r2 * sin(e)
  const x4 = cx + r2 * cos(s), y4 = cy + r2 * sin(s)
  return `M${x1} ${y1} A${r1} ${r1} 0 ${large} 1 ${x2} ${y2} L${x3} ${y3} A${r2} ${r2} 0 ${large} 0 ${x4} ${y4}Z`
}

function midAngle(start: number, span: number) {
  return start - Math.PI / 2 + span / 2
}

interface SliceRender {
  label: string; count: number; color: string
  path: string; lx: number; ly: number; showLabel: boolean
}

function buildSlices(section: ChartSection, cxVal: number): SliceRender[] {
  const totalCount = section.priorities.reduce((s, p) => s + p.count, 0) || 1
  let angle = 0
  return section.priorities.map(p => {
    const span = (p.count / totalCount) * Math.PI * 2
    const mid  = midAngle(angle, span)
    const lr   = (R_OUT + R_IN) / 2
    const item: SliceRender = {
      label:     p.label,
      count:     p.count,
      color:     PRIORITY_COLORS[p.label] ?? '#AAAAAA',
      path:      slicePath(cxVal, CY, R_OUT, R_IN, angle, span),
      lx:        cxVal + lr * Math.cos(mid),
      ly:        CY    + lr * Math.sin(mid),
      showLabel: p.count > 0 && span > 0.2,
    }
    angle += span
    return item
  })
}

const allSlices = computed(() =>
  props.charts.map((section, i) => buildSlices(section, cx.value[i] ?? SVG_W / 2))
)

// Legend (union of all priority labels)
const legend = computed(() => {
  const seen = new Set<string>()
  return props.charts.flatMap(c => c.priorities)
    .filter(p => { const ok = !seen.has(p.label); seen.add(p.label); return ok })
    .map(p => ({ label: p.label, color: PRIORITY_COLORS[p.label] ?? '#AAAAAA' }))
})

const legendStartX = computed(() => (SVG_W - legend.value.length * 170) / 2)
</script>

<template>
  <svg
    :width="SVG_W" :height="SVG_H"
    :viewBox="`0 0 ${SVG_W} ${SVG_H}`"
    xmlns="http://www.w3.org/2000/svg"
    style="max-width:100%;height:auto;display:block;margin:auto"
  >
    <!-- ── background ─────────────────────────────────────────────────────── -->
    <defs>
      <linearGradient id="bgGrad3" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%"   stop-color="#FAF6EE"/>
        <stop offset="100%" stop-color="#EDE5D4"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#bgGrad3)" rx="12"/>

    <!-- ── main title ─────────────────────────────────────────────────────── -->
    <text :x="SVG_W / 2" :y="TITLE_Y"
      font-family="'Noto Sans',sans-serif" font-size="26" font-weight="700"
      fill="#1A2E3D" text-anchor="middle" letter-spacing="1"
    >{{ title.toUpperCase() }}</text>

    <!-- ── donuts ─────────────────────────────────────────────────────────── -->
    <g v-for="(section, ci) in charts" :key="section.label">
      <!-- chart subtitle -->
      <text :x="cx[ci]" :y="CHART_LABEL_Y"
        font-family="'Noto Sans',sans-serif" font-size="18" font-weight="700"
        fill="#2C3E50" text-anchor="middle">{{ section.label }}</text>

      <!-- slices -->
      <path
        v-for="sl in allSlices[ci]" :key="sl.label"
        :d="sl.path" :fill="sl.color" opacity="0.9"
        stroke="white" stroke-width="2.5"/>

      <!-- slice count labels -->
      <text
        v-for="sl in allSlices[ci].filter(s => s.showLabel)" :key="`lbl-${sl.label}`"
        :x="sl.lx" :y="sl.ly + 5"
        font-family="'Noto Sans',sans-serif" font-size="14" font-weight="700"
        fill="white" text-anchor="middle">{{ sl.count }}</text>

      <!-- centre total -->
      <text :x="cx[ci]" :y="CY + 14"
        font-family="'Noto Sans',sans-serif" font-size="48" font-weight="800"
        fill="#1A2E3D" text-anchor="middle">{{ section.total }}</text>
      <text :x="cx[ci]" :y="CY + 36"
        font-family="'Noto Sans',sans-serif" font-size="12" fill="#8A7A68"
        text-anchor="middle" letter-spacing="1">TOTAL</text>
    </g>

    <!-- ── legend ─────────────────────────────────────────────────────────── -->
    <g v-for="(entry, li) in legend" :key="entry.label">
      <rect
        :x="legendStartX + li * 170" :y="SVG_H - 44"
        width="20" height="20" :fill="entry.color" rx="4" opacity="0.9"/>
      <text :x="legendStartX + li * 170 + 28" :y="SVG_H - 28"
        font-family="'Noto Sans',sans-serif" font-size="14" fill="#3A3028">
        {{ entry.label }}
      </text>
    </g>
  </svg>
</template>
