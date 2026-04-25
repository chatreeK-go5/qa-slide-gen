<!-- HBarChart.vue
     Horizontal bar chart — fills the full 1100×618 Slidev canvas.
     All text uses style="font-size:Npx" to bypass UnoCSS attributify.
     Shared by: Production Issues (slide 1) and Beauty in Sprint (slide 2).

     Props:
       title       – chart title (rendered UPPERCASE)
       total       – large badge number
       statuses    – [{ label: string, count: number }]
       subtitle    – date text below title (e.g. "Date: 2026-03-12")
       sprintBadge – sprint pill (e.g. "Sprint 9")
-->
<script setup lang="ts">
import { computed } from 'vue'

interface StatusItem { label: string; count: number }

const props = defineProps<{
  title: string
  total?: number
  statuses: StatusItem[]
  subtitle?: string
  sprintBadge?: string
  bg?: string
}>()

const PALETTE = ['#4A7FA5', '#5BA08A', '#6E9FBF', '#8BC4A8',
                 '#8B6F9E', '#C07070', '#B4A0C8', '#E0A0A0']

// ── Canvas: matches Slidev canvasWidth=1100 × (1100*9/16≈618) ─────────────────
const VW = 1100
const VH = 618

// ── Layout (all values in SVG user units = CSS px at 1:1 in native canvas) ───
const L   = 232   // left label column width
const R   = 80    // right pad after count labels
const T   = 96    // top area (title + badge)
const B   = 40    // bottom pad
const CW  = VW - L - R   // 788 — chart area width
const GAP = 20    // vertical gap between bars

// Badge (top-right)
const BDG_X  = VW - 212
const BDG_CX = VW - 106   // centre of badge
const BDG_W  = 202
const BDG_H  = 80

// ── Computed ─────────────────────────────────────────────────────────────────
const sorted = computed(() =>
  [...props.statuses].sort((a, b) => b.count - a.count)
)
const n      = computed(() => sorted.value.length)
const maxVal = computed(() => Math.max(...sorted.value.map(i => i.count), 1))
const total  = computed(() => props.total ?? sorted.value.reduce((s, i) => s + i.count, 0))

// Dynamic bar height fills the available vertical space
const BH = computed(() => {
  const available = VH - T - B
  return Math.max(Math.floor((available - (n.value - 1) * GAP) / n.value), 32)
})

function bw(count: number) { return Math.max((count / maxVal.value) * CW, 4) }
function by(i: number)     { return T + i * (BH.value + GAP) }

// Grid ticks at 5 evenly spaced intervals
const gridTicks = computed(() => {
  const step = Math.ceil(maxVal.value / 5)
  return [1, 2, 3, 4, 5].map(k => k * step)
})
</script>

<template>
  <!--
    viewBox="0 0 1100 618" + width/height 100% = fills the slide perfectly at
    any viewport size while keeping the 16:9 aspect ratio.
    All text styling is done via style="" to avoid UnoCSS attributify interception.
  -->
  <svg
    viewBox="0 0 1100 618"
    width="100%" height="100%"
    xmlns="http://www.w3.org/2000/svg"
    overflow="hidden"
    style="display:block"
  >
    <!-- background -->
    <rect x="0" y="0" width="1100" height="618" :fill="props.bg ?? '#F5F0E8'"/>

    <!-- title -->
    <text
      x="28" y="56"
      style="font-family:'Noto Sans',Arial,sans-serif;font-size:28px;font-weight:700;fill:#1A2E3D;letter-spacing:1px"
    >{{ title.toUpperCase() }}</text>

    <!-- sprint pill -->
    <g v-if="sprintBadge">
      <rect x="28" y="66" :width="sprintBadge.length * 8.5 + 28" height="22" rx="11" fill="#4A7FA5" opacity="0.18"/>
      <text x="42" y="81" style="font-family:'Noto Sans',Arial,sans-serif;font-size:13px;font-weight:600;fill:#2B5F80">
        {{ sprintBadge }}
      </text>
    </g>

    <!-- date subtitle (only when no sprint pill) -->
    <text v-if="subtitle && !sprintBadge" x="28" y="78"
      style="font-family:'Noto Sans',Arial,sans-serif;font-size:14px;fill:#7A6A58">
      {{ subtitle }}
    </text>

    <!-- total badge box -->
    <rect :x="BDG_X" y="10" :width="BDG_W" :height="BDG_H" rx="12"
      fill="white" opacity="0.78" stroke="#C8B89A" stroke-width="1.5"/>
    <text :x="BDG_CX" y="40" text-anchor="middle"
      style="font-family:'Noto Sans',Arial,sans-serif;font-size:12px;fill:#9A8A78;letter-spacing:1.5px">TOTAL</text>
    <text :x="BDG_CX" y="78" text-anchor="middle"
      style="font-family:'Noto Sans',Arial,sans-serif;font-size:42px;font-weight:800;fill:#1A2E3D">{{ total }}</text>

    <!-- grid lines -->
    <g v-for="tick in gridTicks" :key="tick">
      <line
        :x1="L + (tick / maxVal) * CW" :y1="T - 10"
        :x2="L + (tick / maxVal) * CW" :y2="T + n * (BH + GAP) - GAP + 8"
        stroke="#B8A898" stroke-width="1" stroke-dasharray="4 6" opacity="0.55"/>
    </g>
    <!-- baseline -->
    <line :x1="L" :y1="T - 10" :x2="L" :y2="T + n * (BH + GAP) - GAP + 8"
      stroke="#A09080" stroke-width="2" opacity="0.5"/>

    <!-- bars -->
    <g v-for="(item, i) in sorted" :key="item.label">
      <!-- ghost track -->
      <rect :x="L" :y="by(i)" :width="CW" :height="BH"
        fill="white" opacity="0.14" rx="5"/>
      <!-- row label -->
      <text :x="L - 14" :y="by(i) + BH / 2 + 5" text-anchor="end"
        style="font-family:'Noto Sans',Arial,sans-serif;font-size:16px;fill:#3A3028">
        {{ item.label }}
      </text>
      <!-- bar fill -->
      <rect
        :x="L" :y="by(i) + 4" :width="bw(item.count)" :height="BH - 8"
        :fill="PALETTE[i % PALETTE.length]" rx="5" opacity="0.9"/>
      <!-- count label -->
      <text :x="L + bw(item.count) + 12" :y="by(i) + BH / 2 + 5"
        style="font-family:'Noto Sans',Arial,sans-serif;font-size:16px;font-weight:700;fill:#2C3E50">
        {{ item.count }}
      </text>
    </g>
  </svg>
</template>
