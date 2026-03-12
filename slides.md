---
# Jira Metrics Visualization — Slidev Presentation
# Architecture (PRD): n8n → JSON → GitHub Actions → Slidev export → PNG
theme: default
background: '#F5F0E8'
class: 'text-center'
fonts:
  sans: 'Noto Sans'
  mono: 'Fira Code'
canvasWidth: 1100
---

<script setup>
import meta from './data/current/meta.json'
import productionData from './data/current/production_issues.json'
</script>

<HBarChart
  :title="productionData.title"
  :total="productionData.total"
  :items="productionData.statuses"
  :subtitle="`Date: ${productionData.date ?? meta.date}`"
/>

---
background: '#F5F0E8'
---

<script setup>
import beautyData from './data/current/beauty_in_sprint.json'
</script>

<HBarChart
  :title="`${beautyData.title} – ${beautyData.sprint_name}`"
  :total="beautyData.total"
  :items="beautyData.items"
  badge-label="TOTAL"
/>

---
background: '#F5F0E8'
---

<script setup>
import over14Data from './data/current/over_14_days.json'

const groups = [
  {
    label: over14Data.pi.label,
    segments: [
      { label: 'Highest', count: over14Data.pi.highest,  color: '#C0392B' },
      { label: 'High',    count: over14Data.pi.high,     color: '#E67E22' },
      { label: 'Medium',  count: over14Data.pi.medium,   color: '#27AE60' },
    ],
  },
  {
    label: over14Data.beauty.label,
    segments: [
      { label: 'Highest', count: over14Data.beauty.highest, color: '#C0392B' },
      { label: 'High',    count: over14Data.beauty.high,    color: '#E67E22' },
      { label: 'Medium',  count: over14Data.beauty.medium,  color: '#27AE60' },
    ],
  },
]
</script>

<StackedHBar
  :title="over14Data.title"
  :groups="groups"
/>

---
background: '#F5F0E8'
---

<script setup>
import summaryData from './data/current/summary_by_priority.json'
</script>

<DonutPair
  :title="summaryData.title"
  :left="summaryData.beauty"
  :right="summaryData.pi"
/>
