<!-- StackedHBar.vue
     Stacked horizontal bar chart — fills the full 1100×618 Slidev canvas.
     All text uses style="font-size:Npx" to bypass UnoCSS attributify.
     Used by: Over – 14 Days (slide 3).

     Props:
       title  – chart title
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

const VW = 1100
const VH = 618

const L   = 180   // left label column
const R   = 50    // right pad
const T   = 96    // top (title area)
const LEG = 72    // legend strip at bottom
const CW  = VW - L - R   // 870 chart width
const BH  = 110   // bar height
const GAP = 80    // gap between group bars

const BARS_H = computed(() => props.groups.length * BH + (props.groups.length - 1) * GAP)
// Centre bars in the available vertical space between title and legend
const BARS_Y = computed(() => {
  const available = VH - T - LEG
  return T + Math.max(Math.round((available - BARS_H.value) / 2), 0)
})

const grandMax = computed(() =>
  Math.max(...props.groups.map(g => g.segments.reduce((s, seg) => s + seg.count, 0)), 1)
)

function segX(group: Group, segIdx: number) {
  return L + (group.segments.slice(0, segIdx).reduce((s, seg) => s + seg.count, 0) / grandMax.value) * CW
}
function segW(count: number) { return Math.max((count / grandMax.value) * CW, 4) }
function by(i: number)       { return BARS_Y.value + i * (BH + GAP) }

const legend = computed(() => {
  const seen = new Set<string>()
  return props.groups.flatMap(g => g.segments)
    .filter(s => { const ok = !seen.has(s.label); seen.add(s.label); return ok })
    .map(s => ({ label: s.label, color: s.color }))
})

const legendY    = computed(() => VH - LEG + 16)
const legendStep = computed(() => Math.min(200, CW / (legend.value.length || 1)))
const legendX0   = computed(() => L + (CW - legend.value.length * legendStep.value) / 2)
</script>

<template>
  <svg
    viewBox="0 0 1100 618"
    width="100%" height="100%"
    xmlns="http://www.w3.org/2000/svg"
    overflow="hidden"
    style="display:block"
  >
    <rect x="0" y="0" width="1100" height="618" fill="#F5F0E8"/>

    <!-- title -->
    <text x="28" y="56"
      style="font-family:'Noto Sans',Arial,sans-serif;font-size:28px;font-weight:700;fill:#1A2E3D;letter-spacing:1px">
      {{ title.toUpperCase() }}
    </text>

    <!-- grid lines -->
    <g v-for="t in [1,2,3,4,5]" :key="t">
      <line
        :x1="L + (t / 5) * CW" :y1="BARS_Y - 10"
        :x2="L + (t / 5) * CW" :y2="BARS_Y + BARS_H + 10"
        stroke="#B8A898" stroke-width="1" stroke-dasharray="4 6" opacity="0.5"/>
    </g>
    <!-- baseline -->
    <line :x1="L" :y1="BARS_Y - 10" :x2="L" :y2="BARS_Y + BARS_H + 10"
      stroke="#A09080" stroke-width="2" opacity="0.5"/>

    <!-- groups -->
    <g v-for="(group, gi) in groups" :key="group.label">
      <!-- ghost track -->
      <rect :x="L" :y="by(gi)" :width="CW" :height="BH"
        fill="white" opacity="0.14" rx="5"/>
      <!-- group label -->
      <text :x="L - 16" :y="by(gi) + BH / 2 + 6" text-anchor="end"
        style="font-family:'Noto Sans',Arial,sans-serif;font-size:18px;font-weight:700;fill:#2C3E50">
        {{ group.label }}
      </text>
      <!-- stacked segments -->
      <g v-for="(seg, si) in group.segments" :key="seg.label">
        <rect
          :x="segX(group, si)" :y="by(gi) + 4"
          :width="segW(seg.count)" :height="BH - 8"
          :fill="seg.color" rx="5" opacity="0.9"/>
        <text v-if="segW(seg.count) > 36"
          :x="segX(group, si) + segW(seg.count) / 2"
          :y="by(gi) + BH / 2 + 6"
          text-anchor="middle"
          style="font-family:'Noto Sans',Arial,sans-serif;font-size:17px;font-weight:700;fill:white">
          {{ seg.count }}
        </text>
      </g>
      <!-- row total -->
      <text
        :x="L + (group.segments.reduce((s, seg) => s + seg.count, 0) / grandMax) * CW + 16"
        :y="by(gi) + BH / 2 + 6"
        style="font-family:'Noto Sans',Arial,sans-serif;font-size:17px;font-weight:700;fill:#2C3E50">
        {{ group.segments.reduce((s, seg) => s + seg.count, 0) }}
      </text>
    </g>

    <!-- legend -->
    <g v-for="(entry, li) in legend" :key="entry.label">
      <rect
        :x="legendX0 + li * legendStep" :y="legendY"
        width="22" height="22" :fill="entry.color" rx="4" opacity="0.9"/>
      <text :x="legendX0 + li * legendStep + 30" :y="legendY + 17"
        style="font-family:'Noto Sans',Arial,sans-serif;font-size:15px;fill:#3A3028">
        {{ entry.label }}
      </text>
    </g>
  </svg>
</template>
