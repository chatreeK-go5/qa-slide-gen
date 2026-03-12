<!-- StackedHBar.vue
     Stacked horizontal bar chart (SVG-based, no external dependencies).
     Used by: Over 14 Days slide.
-->
<script setup lang="ts">
import { computed } from 'vue'

interface Segment {
  label: string
  count: number
  color: string
}

interface Group {
  label: string
  segments: Segment[]
}

const props = defineProps<{
  title: string
  groups: Group[]
  legendTitle?: string
}>()

const BG = '#F5F0E8'
const LEFT_PAD = 140
const RIGHT_PAD = 60
const TOP_PAD = 90
const BOTTOM_PAD = 90
const BAR_H = 52
const BAR_GAP = 30
const CHART_W = 860

const SVG_W = LEFT_PAD + CHART_W + RIGHT_PAD

const grandMax = computed(() =>
  Math.max(...props.groups.map(g => g.segments.reduce((s, seg) => s + seg.count, 0)), 1)
)

const svgH = computed(() =>
  TOP_PAD + props.groups.length * (BAR_H + BAR_GAP) - BAR_GAP + BOTTOM_PAD
)

function segX(group: Group, segIdx: number) {
  const left = LEFT_PAD
  const prev = group.segments.slice(0, segIdx).reduce((s, seg) => s + seg.count, 0)
  return left + (prev / grandMax.value) * CHART_W
}

function segW(count: number) {
  return Math.max((count / grandMax.value) * CHART_W, 2)
}

function by(i: number) {
  return TOP_PAD + i * (BAR_H + BAR_GAP)
}

// Collect unique legend entries from all groups
const legendEntries = computed(() => {
  const seen = new Set<string>()
  const entries: Array<{ label: string; color: string }> = []
  for (const g of props.groups) {
    for (const seg of g.segments) {
      if (!seen.has(seg.label)) {
        seen.add(seg.label)
        entries.push({ label: seg.label, color: seg.color })
      }
    }
  }
  return entries
})

const legendY = computed(() =>
  TOP_PAD + props.groups.length * (BAR_H + BAR_GAP) - BAR_GAP + 20
)
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

    <!-- Grid lines -->
    <g v-for="t in [1,2,3,4,5]" :key="t">
      <line
        :x1="LEFT_PAD + (t / 5) * CHART_W"
        :y1="TOP_PAD - 8"
        :x2="LEFT_PAD + (t / 5) * CHART_W"
        :y2="TOP_PAD + groups.length * (BAR_H + BAR_GAP) - BAR_GAP + 8"
        stroke="#C0B090" stroke-width="1" stroke-dasharray="5,5" opacity="0.4"
      />
    </g>

    <!-- Bars -->
    <g v-for="(group, gi) in groups" :key="group.label">
      <!-- Row background -->
      <rect
        :x="LEFT_PAD" :y="by(gi)"
        :width="CHART_W" :height="BAR_H"
        fill="white" opacity="0.2" rx="3"
      />
      <!-- Group label -->
      <text
        :x="LEFT_PAD - 12" :y="by(gi) + BAR_H / 2 + 6"
        font-family="'Noto Sans', sans-serif" font-size="15" font-weight="bold"
        fill="#2C3E50" text-anchor="end"
      >{{ group.label }}</text>

      <!-- Stacked segments -->
      <g v-for="(seg, si) in group.segments" :key="seg.label">
        <rect
          :x="segX(group, si)" :y="by(gi)"
          :width="segW(seg.count)" :height="BAR_H"
          :fill="seg.color" rx="3" opacity="0.88"
        />
        <!-- Segment label (only if wide enough) -->
        <text
          v-if="segW(seg.count) > 28"
          :x="segX(group, si) + segW(seg.count) / 2"
          :y="by(gi) + BAR_H / 2 + 6"
          font-family="'Noto Sans', sans-serif" font-size="13" font-weight="bold"
          fill="white" text-anchor="middle"
        >{{ seg.count }}</text>
      </g>

      <!-- Total label at end -->
      <text
        :x="segX(group, group.segments.length - 1) + segW(group.segments[group.segments.length - 1]?.count ?? 0) + 10"
        :y="by(gi) + BAR_H / 2 + 6"
        font-family="'Noto Sans', sans-serif" font-size="13" font-weight="bold"
        fill="#333" text-anchor="start"
      >{{ group.segments.reduce((s, seg) => s + seg.count, 0) }}</text>
    </g>

    <!-- Legend -->
    <g v-for="(entry, li) in legendEntries" :key="entry.label">
      <rect
        :x="LEFT_PAD + li * 180" :y="legendY"
        width="18" height="18"
        :fill="entry.color" rx="3" opacity="0.88"
      />
      <text
        :x="LEFT_PAD + li * 180 + 26" :y="legendY + 14"
        font-family="'Noto Sans', sans-serif" font-size="13" fill="#333"
      >{{ entry.label }}</text>
    </g>
  </svg>
</template>
