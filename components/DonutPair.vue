<!-- DonutPair.vue
     N donut charts side by side — fills the full 1100×618 Slidev canvas.
     All text uses style="font-size:Npx" to bypass UnoCSS attributify.
     Used by: Summary by Priority (slide 4).

     Props:
       title  – chart title
       charts – [{ label, total, priorities: [{ label, count }] }, ...]  (2+ entries)
       bg     – background fill (default '#F5F0E8'; pass 'none' for transparent export)
-->
<script setup lang="ts">
import { computed } from 'vue'

interface PrioritySlice { label: string; count: number }
interface ChartSection  { label: string; total: number; priorities: PrioritySlice[] }

const props = defineProps<{
  title: string
  charts: ChartSection[]
  bg?: string
}>()

const bgFill = computed(() => props.bg ?? '#F5F0E8')

const PRIORITY_COLORS: Record<string, string> = {
  Highest: '#C0392B',
  High:    '#E67E22',
  Medium:  '#27AE60',
  Low:     '#2980B9',
  Lowest:  '#95A5A6',
}

const VW    = 1100
const VH    = 618
const CY    = 318   // donut centre Y
const LEG_Y = 552   // legend strip Y

const n = computed(() => props.charts.length)

// Scale donuts down when 3+ charts to avoid overlap
const rOut = computed(() => n.value <= 2 ? 178 : 115)
const rIn  = computed(() => n.value <= 2 ? 96  : 62)
const totalFontSize = computed(() => n.value <= 2 ? 52 : 36)
const subLabelSize  = computed(() => n.value <= 2 ? 19 : 16)

// Chart centres: evenly spaced across the slide width
const cx = computed(() => {
  return props.charts.map((_, i) => Math.round(VW * (i + 1) / (n.value + 1)))
})

// ── SVG arc path ──────────────────────────────────────────────────────────────
function arcPath(cxv: number, r1: number, r2: number, start: number, span: number): string {
  const clamp = Math.min(span, Math.PI * 2 - 0.0001)
  const s = start - Math.PI / 2
  const e = s + clamp
  const large = clamp > Math.PI ? 1 : 0
  const x1 = cxv + r1 * Math.cos(s), y1 = CY + r1 * Math.sin(s)
  const x2 = cxv + r1 * Math.cos(e), y2 = CY + r1 * Math.sin(e)
  const x3 = cxv + r2 * Math.cos(e), y3 = CY + r2 * Math.sin(e)
  const x4 = cxv + r2 * Math.cos(s), y4 = CY + r2 * Math.sin(s)
  return `M${x1} ${y1} A${r1} ${r1} 0 ${large} 1 ${x2} ${y2} L${x3} ${y3} A${r2} ${r2} 0 ${large} 0 ${x4} ${y4}Z`
}

interface SliceRender {
  label: string; count: number; color: string
  path: string; lx: number; ly: number; showLabel: boolean
}

function buildSlices(section: ChartSection, cxv: number, rOutV: number, rInV: number): SliceRender[] {
  const tot = section.priorities.reduce((s, p) => s + p.count, 0) || 1
  let angle = 0
  const lr = (rOutV + rInV) / 2
  return section.priorities.map(p => {
    const span = (p.count / tot) * Math.PI * 2
    const mid  = angle - Math.PI / 2 + span / 2
    const sl: SliceRender = {
      label:     p.label,
      count:     p.count,
      color:     PRIORITY_COLORS[p.label] ?? '#AAAAAA',
      path:      arcPath(cxv, rOutV, rInV, angle, span),
      lx:        cxv + lr * Math.cos(mid),
      ly:        CY  + lr * Math.sin(mid),
      showLabel: p.count > 0 && span > 0.2,
    }
    angle += span
    return sl
  })
}

const allSlices = computed(() =>
  props.charts.map((section, i) => buildSlices(section, cx.value[i] ?? VW / 2, rOut.value, rIn.value))
)

const legend = computed(() => {
  const seen = new Set<string>()
  return props.charts.flatMap(c => c.priorities)
    .filter(p => { const ok = !seen.has(p.label); seen.add(p.label); return ok })
    .map(p => ({ label: p.label, color: PRIORITY_COLORS[p.label] ?? '#AAAAAA' }))
})

const LEG_STEP   = 170
const legendX0   = computed(() => (VW - legend.value.length * LEG_STEP) / 2)
</script>

<template>
  <svg
    viewBox="0 0 1100 618"
    width="100%" height="100%"
    xmlns="http://www.w3.org/2000/svg"
    overflow="hidden"
    style="display:block"
  >
    <rect x="0" y="0" width="1100" height="618" :fill="bgFill"/>

    <!-- main title -->
    <text :x="VW / 2" y="52" text-anchor="middle"
      style="font-family:'Noto Sans',Arial,sans-serif;font-size:28px;font-weight:700;fill:#1A2E3D;letter-spacing:1px">
      {{ title.toUpperCase() }}
    </text>

    <!-- donuts -->
    <g v-for="(section, ci) in charts" :key="section.label">
      <!-- chart sub-label -->
      <text :x="cx[ci]" y="100" text-anchor="middle"
        :style="`font-family:'Noto Sans',Arial,sans-serif;font-size:${subLabelSize}px;font-weight:700;fill:#2C3E50`">
        {{ section.label }}
      </text>

      <!-- arcs -->
      <path
        v-for="sl in allSlices[ci]" :key="sl.label"
        :d="sl.path" :fill="sl.color" opacity="0.92"
        :stroke="bgFill" stroke-width="2.5"/>

      <!-- count labels on each slice -->
      <text
        v-for="sl in allSlices[ci].filter(s => s.showLabel)" :key="`lbl-${sl.label}`"
        :x="sl.lx" :y="sl.ly + 6"
        text-anchor="middle"
        style="font-family:'Noto Sans',Arial,sans-serif;font-size:15px;font-weight:700;fill:white">
        {{ sl.count }}
      </text>

      <!-- centre: big total number -->
      <text :x="cx[ci]" :y="CY + 16" text-anchor="middle"
        :style="`font-family:'Noto Sans',Arial,sans-serif;font-size:${totalFontSize}px;font-weight:800;fill:#1A2E3D`">
        {{ section.total }}
      </text>
      <!-- centre: "TOTAL" label -->
      <text :x="cx[ci]" :y="CY + 40" text-anchor="middle"
        style="font-family:'Noto Sans',Arial,sans-serif;font-size:12px;fill:#8A7A68;letter-spacing:1.5px">
        TOTAL
      </text>
    </g>

    <!-- legend -->
    <g v-for="(entry, li) in legend" :key="entry.label">
      <rect
        :x="legendX0 + li * LEG_STEP" :y="LEG_Y"
        width="20" height="20" :fill="entry.color" rx="4" opacity="0.9"/>
      <text :x="legendX0 + li * LEG_STEP + 28" :y="LEG_Y + 15"
        style="font-family:'Noto Sans',Arial,sans-serif;font-size:14px;fill:#3A3028">
        {{ entry.label }}
      </text>
    </g>
  </svg>
</template>
