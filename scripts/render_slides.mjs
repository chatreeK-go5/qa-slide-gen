#!/usr/bin/env node
/**
 * render_slides.mjs
 *
 * Runs:
 *   1. prepare_data.mjs   — copies latest JSON to data/current/
 *   2. slidev export       — renders slides as PNG
 *   3. rename step         — maps slide-NNN.png → PRD-compliant names
 *
 * Architecture note (per PRD):
 *   GitHub Actions ONLY reads JSON and renders images — no Jira API calls.
 *
 * Usage:
 *   node scripts/render_slides.mjs [--date YYYY-MM-DD]
 *
 * When --date is provided it is forwarded to prepare_data.mjs so the exact
 * date folder is used instead of the latest one.  This is how the
 * repository_dispatch trigger passes the date from n8n.
 */

import { execSync } from 'child_process'
import { readdir, rename, mkdir, rm } from 'fs/promises'
import { existsSync } from 'fs'
import { join, resolve } from 'path'
import { fileURLToPath } from 'url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const repoRoot = resolve(__dirname, '..')
const dataRoot = join(repoRoot, 'data')
const artifactsRoot = join(repoRoot, 'artifacts')
const TMP_EXPORT = join(repoRoot, '.slidev-export-tmp')

const argDate = process.argv.find((a, i) => process.argv[i - 1] === '--date')

// Slide index → PRD output filename (1-based)
// Slide 1 = Production Issues, 2 = Beauty in Sprint, etc.
const SLIDE_MAP = {
  1: 'production_issues',
  2: 'beauty_in_sprint',
  3: 'over_14_days',
  4: 'summary_by_priority',
}

// ---------------------------------------------------------
// Resolve the active date from data/current/meta.json
// ---------------------------------------------------------
async function resolveDate() {
  const metaPath = join(dataRoot, 'current', 'meta.json')
  if (!existsSync(metaPath)) {
    console.error('ERROR: data/current/meta.json not found — run prepare_data.mjs first')
    process.exit(1)
  }
  const meta = JSON.parse(await (await import('fs/promises')).readFile(metaPath, 'utf8'))
  return meta.date
}

async function main() {
  // Step 1: prepare data
  console.log('\n── Step 1: Prepare data ──')
  const dateArg = argDate ? ` --date ${argDate}` : ''
  execSync(`node ${join(__dirname, 'prepare_data.mjs')}${dateArg}`, { stdio: 'inherit' })

  const dateStr = await resolveDate()
  const outputDir = join(artifactsRoot, dateStr)
  await mkdir(outputDir, { recursive: true })

  // Step 2: export slides
  console.log('\n── Step 2: Export slides via Slidev ──')
  await rm(TMP_EXPORT, { recursive: true, force: true })
  await mkdir(TMP_EXPORT, { recursive: true })

  const slidevBin = join(repoRoot, 'node_modules', '.bin', 'slidev')
  const cmd = [
    slidevBin,
    'export',
    join(repoRoot, 'slides.md'),
    '--format', 'png',
    '--output', join(TMP_EXPORT, 'slide'),
    '--timeout', '60000',
  ].join(' ')

  console.log(`Running: ${cmd}`)
  execSync(cmd, { stdio: 'inherit', cwd: repoRoot })

  // Step 3: rename exports
  console.log('\n── Step 3: Rename exports ──')
  // Slidev creates a subdirectory named after the --output basename
  // e.g., --output /tmp/slide  →  /tmp/slide/1.png, 2.png, ...
  const exportedDir = TMP_EXPORT + '/slide'
  const actualDir = existsSync(exportedDir) ? exportedDir : TMP_EXPORT

  const exported = (await readdir(actualDir))
    .filter(f => f.endsWith('.png'))
    .sort((a, b) => {
      const na = parseInt(a, 10)
      const nb = parseInt(b, 10)
      return na - nb
    })

  if (exported.length === 0) {
    console.error('ERROR: No PNG files found in export output.')
    process.exit(1)
  }

  const expectedCount = Object.keys(SLIDE_MAP).length
  let rendered = 0

  for (const file of exported) {
    // Slidev names files 1.png, 2.png, ...
    const match = file.match(/^(\d+)\.png$/)
    if (!match) continue
    const slideNum = parseInt(match[1], 10)
    const chartName = SLIDE_MAP[slideNum]
    if (!chartName) {
      console.log(`  ⚠  no mapping for slide ${slideNum} (${file}) — skipping`)
      continue
    }
    const dst = join(outputDir, `${chartName}.png`)
    await rename(join(actualDir, file), dst)
    console.log(`  ✓  ${file} → artifacts/${dateStr}/${chartName}.png`)
    rendered++
  }

  if (rendered < expectedCount) {
    console.error(`ERROR: Expected ${expectedCount} slides but only ${rendered} were exported. Aborting.`)
    process.exit(1)
  }

  // Cleanup
  await rm(TMP_EXPORT, { recursive: true, force: true })

  console.log(`\nAll slides rendered → artifacts/${dateStr}/`)
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
