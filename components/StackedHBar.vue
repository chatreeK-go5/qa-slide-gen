<!-- StackedHBar.vue
     Stacked horizontal bar chart (SVG). Used by: Over – 14 Days slide.
     Props:
       title  – slide title
       groups – [{ label: string, segments: [{ label, count, color }] }]
-->
<script setup lang="ts">
import { computed } from 'vue'

interface Segment { label: string; count: number; color: string }
interface Group    { label: string; segments: Segment[] }

const props = defineProps<{
  title: string
  groups: Group[]
}>()

// ── layout ───────────────────────────────────────────────────────────────────
const L  = 140   // left label pad
const R  = 60    // right pad
const T  = 96    // top pad
const B  = 90    // bottom pad (legend space)
const BH = 56    // bar height
const BG = 32    // bar gap
const CW = 880   // chart area width
const W  = L + CW + R

const grandMax = computed(() =>
  Math.max(...props.groups.map(g => g.segments.reduce((s, seg) => s + seg.count, 0)), 1)
)
const svgH = computed(() => T + props.groups.length * (BH + BG) - BG + B)

function segX(group: Group, segIdx: number) {
  return L + (group.segments.slice(0, segIdx).reduce((s, seg) => s + seg.count, 0) / grandMax.value) * CW
}
function segW(count: number) { return Math.max((count / grandMax.value) * CW, 3) }
function by(i: number)       { return T + i * (BH + BG) }

// Collect unique legend entries (preserving order)
const legend = computed(() => {
  const seen = new Set<string>()
  return props.groups.flatMap(g => g.segments)
    .filter(s => { const ok = !seen.has(s.label); seen.add(s.label); return ok })
    .map(s => ({ label: s.label, color: s.color }))
})

const legendY = computed(() => T + props.groups.length * (BH + BG) - BG + 24)
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
      <linearGradient id="bgGrad2" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0%"   stop-color="#FAF6EE"/>
        <stop offset="100%" stop-color="#EDE5D4"/>
      </linearGradient>
    </defs>
    <rect width="100%" height="100%" fill="url(#bgGrad2)" rx="12"/>

    <!-- ── title ─────────────────────────────────────────────────────────── -->
    <text x="20" y="44"
      font-family="'Noto Sans',sans-serif" font-size="26" font-weight="700"
      fill="#1A2E3D" letter-spacing="1">{{ title.toUpperCase() }}</text>

    <!-- ── grid lines ─────────────────────────────────────────────────────── -->
    <g v-for="t in [1,2,3,4,5]" :key="t">
      <line
        :x1="L + (t / 5) * CW" :y1="T - 10"
        :x2="L + (t / 5) * CW" :y2="T + groups.length * (BH + BG) - BG + 6"
        stroke="#C4B49A" stroke-width="1" stroke-dasharray="4,5" opacity="0.45"/>
    </g>
    <line :x1="L" :y1="T - 10" :x2="L" :y2="T + groups.length * (BH + BG) - BG + 6"
      stroke="#B0A090" stroke-width="1.5" opacity="0.6"/>

    <!-- ── bars ───────────────────────────────────────────────────────────── -->
    <g v-for="(group, gi) in groups" :key="group.label">
      <!-- ghost track -->
      <rect :x="L" :y="by(gi)" :width="CW" :height="BH"
        fill="white" opacity="0.18" rx="4"/>

      <!-- group label -->
      <text :x="L - 14" :y="by(gi) + BH / 2 + 6"
        font-family="'Noto Sans',sans-serif" font-size="16" font-weight="700"
        fill="#2C3E50" text-anchor="end">{{ group.label }}</text>

      <!-- segments -->
      <g v-for="(seg, si) in group.segments" :key="seg.label">
        <rect
          :x="segX(group, si)" :y="by(gi) + 3"
          :width="segW(seg.count)" :height="BH - 6"
          :fill="seg.color" rx="4" opacity="0.88"/>
        <!-- count inside segment (if wide enough) -->
        <text v-if="segW(seg.count) > 32"
          :x="segX(group, si) + segW(seg.count) / 2"
          :y="by(gi) + BH / 2 + 6"
          font-family="'Noto Sans',sans-serif" font-size="15" font-weight="700"
          fill="white" text-anchor="middle">{{ seg.count }}</text>
      </g>

      <!-- total after last segment -->
      <text
        :x="L + (group.segments.reduce((s, seg) => s + seg.count, 0) / grandMax) * CW + 12"
        :y="by(gi) + BH / 2 + 6"
        font-family="'Noto Sans',sans-serif" font-size="15" font-weight="700"
        fill="#2C3E50" text-anchor="start"
      >{{ group.segments.reduce((s, seg) => s + seg.count, 0) }}</text>
    </g>

    <!-- ── legend ─────────────────────────────────────────────────────────── -->
    <g v-for="(entry, li) in legend" :key="entry.label">
      <rect :x="L + li * 200" :y="legendY" width="20" height="20"
        :fill="entry.color" rx="4" opacity="0.88"/>
      <text :x="L + li * 200 + 28" :y="legendY + 15"
        font-family="'Noto Sans',sans-serif" font-size="14" fill="#3A3028">
        {{ entry.label }}
      </text>
    </g>
  </svg>
</template>
