---
theme: default
layout: default
background: "#F5F0E8"
fonts:
  sans: "Noto Sans"
canvasWidth: 1100
export:
  format: png
  timeout: 60000
---

<script setup>
import meta from './data/current/meta.json'
import d from './data/current/production_issues.json'
</script>

<HBarChart
  :title="d.title"
  :total="d.total"
  :statuses="d.statuses"
  :subtitle="`Date: ${d.date ?? meta.date}`"
/>

---

layout: default
background: '#F5F0E8'

---

<script setup>
import d from './data/current/beauty_in_sprint.json'
</script>

<HBarChart
  :title="d.title"
  :total="d.total"
  :statuses="d.statuses"
  :sprint-badge="d.sprint_name"
/>

---

layout: default
background: '#F5F0E8'

---

<script setup>
import d from './data/current/over_14_days.json'

const COLORS = { Highest: '#C0392B', High: '#E67E22', Medium: '#27AE60' }

const groups = d.groups.map(g => ({
  label: g.label,
  segments: g.priorities.map(p => ({
    label: p.label,
    count: p.count,
    color: COLORS[p.label] ?? '#888888',
  })),
}))
</script>

<StackedHBar :title="d.title" :groups="groups" />

---

layout: default
background: '#F5F0E8'

---

<script setup>
import d from './data/current/summary_by_priority.json'
</script>

<DonutPair :title="d.title" :charts="d.charts" />
