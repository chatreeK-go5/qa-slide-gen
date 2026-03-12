<!-- HBarChart.vue
     Horizontal bar chart (SVG). Shared by Production Issues and Beauty in Sprint.
     Props:
       title       – slide title (displayed UPPERCASE)
       total       – large badge number (e.g. 207)
       statuses    – [{ label: string, count: number }]
       subtitle    – optional small text below title (e.g. "Date: 2026-03-12")
       badgeLabel  – optional label above total (default "TOTAL")
       sprintBadge – optional sprint name pill (e.g. "Sprint 9")
-->
<script setup lang="ts">
import { computed } from 'vue'

interface StatusItem {
  label: string
  count: number
}

const props = defineProps<{
  title: string
  total?: number
  statuses: StatusItem[]
  subtitle?: string
  badgeLabel?: string
  sprintBadge?: string
}>()

// ── palette ──────────────────────────────────────────────────────────────────
const BAR_PALETTE = [
  '#4A7FA5', '#6E9FBF', '#5BA08A', '#8BC4A8',
  '#8B6F9E', '#B4A0C8', '#C07070', '#E0A0A0',
]

// ── layout constants ─────────────────────────────────────────────────────────
const L = 180   // left pad (label area)
const R = 90    // right pad
const T = 108   // top pad
const B = 52    // bottom pad
const BH = 40   // bar height
const BG = 14   // bar gap
const CW = 830  // chart area width
const W  = L + CW + R  // total SVG width

// ── computed ─────────────────────────────────────────────────────────────────
const sorted = computed(() =>
  [...props.statuses].sort((a, b) => b.count - a.count)
)
const maxVal  = computed(() => Math.max(...sorted.value.map(i => i.count), 1))
const total   = computed(() => props.total ?? sorted.value.reduce((s, i) => s + i.count, 0))
const svgH    = computed(() => T + sorted.value.length * (BH + BG) - BG + B)

function bw(count: number) { return Math.max((count / maxVal.value) * CW, 3) }
function by(i: number)     { return T + i * (BH + BG) }

// Five evenly-spaced grid tick values
const gridTicks = computed(() => {
  const step = Math.ceil(maxVal.value / 5)
  return [1, 2, 3, 4, 5].map(n => n * step)
})
</script>

<template>
  <svg
    :width="W" :height="svgH"
    :viewBox="`0 0 ${W} ${svgH}`"
    xmlns="http://www.w3.org/2000/svg"
    style="max-width:100%;height:auto;display:block;margin:auto"
  >
    <!-- ── background ─────────────────────────────────────────────────────── -->
    <defs>
      <linearGradient id="bgGrad" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%"   stop-color="#FAF6EE"/>
        <stop offset="100%" stop-color="#EDE5D4"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#bgGrad)" rx="12"/>

    <!-- ── title ─────────────────────────────────────────────────────────── -->
    <text x="20" y="44"
      font-family="'Noto Sans',sans-serif" font-size="26" font-weight="700"
      fill="#1A2E3D" letter-spacing="1">{{ title.toUpperCase() }}</text>

    <!-- sprint pill -->
    <g v-if="sprintBadge">
      <rect :x="20" y="54" :width="sprintBadge.length * 8 + 24" height="24"
        rx="12" fill="#4A7FA5" opacity="0.15"/>
      <text x="32" y="71"
        font-family="'Noto Sans',sans-serif" font-size="13" fill="#4A7FA5" font-weight="600"
      >{{ sprintBadge }}</text>
    </g>

    <!-- subtitle -->
    <text v-if="subtitle && !sprintBadge" x="20" y="70"
      font-family="'Noto Sans',sans-serif" font-size="13" fill="#7A6A58">
      {{ subtitle }}
    </text>

    <!-- ── total badge ─────────────────────────────────────────────────────── -->
    <rect :x="W - 130" y="12" width="112" height="76" rx="12"
      fill="white" opacity="0.72" stroke="#C8B89A" stroke-width="1.5"/>
    <text :x="W - 74" y="38"
      font-family="'Noto Sans',sans-serif" font-size="12" fill="#9A8A78"
      text-anchor="middle" letter-spacing="1">{{ (badgeLabel ?? 'TOTAL').toUpperCase() }}</text>
    <text :x="W - 74" y="76"
      font-family="'Noto Sans',sans-serif" font-size="38" font-weight="800"
      fill="#1A2E3D" text-anchor="middle">{{ total }}</text>

    <!-- ── grid lines ─────────────────────────────────────────────────────── -->
    <g v-for="tick in gridTicks" :key="tick">
      <line
        :x1="L + (tick / maxVal) * CW" :y1="T - 10"
        :x2="L + (tick / maxVal) * CW" :y2="T + sorted.length * (BH + BG) - BG + 6"
        stroke="#C4B49A" stroke-width="1" stroke-dasharray="4,5" opacity="0.5"/>
    </g>
    <!-- baseline -->
    <line :x1="L" :y1="T - 10" :x2="L" :y2="T + sorted.length * (BH + BG) - BG + 6"
      stroke="#B0A090" stroke-width="1.5" opacity="0.6"/>

    <!-- ── bars ───────────────────────────────────────────────────────────── -->
    <g v-for="(item, i) in sorted" :key="item.label">
      <!-- ghost track -->
      <rect :x="L" :y="by(i)" :width="CW" :height="BH"
        fill="white" opacity="0.18" rx="4"/>
      <!-- label -->
      <text :x="L - 12" :y="by(i) + BH / 2 + 5"
        font-family="'Noto Sans',sans-serif" font-size="14" fill="#3A3028"
        text-anchor="end">{{ item.label }}</text>
      <!-- bar -->
      <rect :x="L" :y="by(i) + 2"
        :width="bw(item.count)" :height="BH - 4"
        :fill="BAR_PALETTE[i % BAR_PALETTE.length]" rx="5" opacity="0.9"/>
      <!-- count -->
      <text :x="L + bw(item.count) + 10" :y="by(i) + BH / 2 + 5"
        font-family="'Noto Sans',sans-serif" font-size="14" font-weight="700"
        fill="#2C3E50">{{ item.count }}</text>
    </g>
  </svg>
</template>

