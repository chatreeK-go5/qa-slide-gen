#!/usr/bin/env node
/**
 * prepare_data.mjs
 *
 * Architecture note (per PRD):
 *   n8n writes JSON to data/YYYY-MM-DD/ — this script merely copies the most
 *   recent date folder into data/current/ so that Slidev's Vite build can
 *   import the JSON files with a stable, well-known path.
 *
 *   No Jira API calls. No authentication. Pure file copy.
 *
 * Usage:
 *   node scripts/prepare_data.mjs [--date YYYY-MM-DD]
 */

import { readdir, copyFile, mkdir, writeFile } from 'fs/promises'
import { existsSync } from 'fs'
import { join, resolve } from 'path'
import { fileURLToPath } from 'url'

const __dirname = fileURLToPath(new URL('.', import.meta.url))
const repoRoot = resolve(__dirname, '..')
const dataRoot = join(repoRoot, 'data')

// ---------------------------------------------------------
// Resolve the target date
// ---------------------------------------------------------
const argDate = process.argv.find((a, i) => process.argv[i - 1] === '--date')

async function resolveDate(requested) {
  if (requested) {
    const dir = join(dataRoot, requested)
    if (!existsSync(dir)) {
      console.error(`ERROR: data directory not found: ${dir}`)
      process.exit(1)
    }
    return requested
  }

  const entries = await readdir(dataRoot, { withFileTypes: true })
  const dateDirs = entries
    .filter(e => e.isDirectory() && /^\d{4}-\d{2}-\d{2}$/.test(e.name))
    .map(e => e.name)
    .sort()
    .reverse()

  if (dateDirs.length === 0) {
    console.error(`ERROR: no date folders found under ${dataRoot}`)
    process.exit(1)
  }
  return dateDirs[0]
}

const CHART_FILES = [
  'production_issues',
  'beauty_in_sprint',
  'over_14_days',
  'summary_by_priority',
]

async function main() {
  const dateStr = await resolveDate(argDate)
  const sourceDir = join(dataRoot, dateStr)
  const targetDir = join(dataRoot, 'current')

  await mkdir(targetDir, { recursive: true })

  const missing = []
  for (const name of CHART_FILES) {
    const src = join(sourceDir, `${name}.json`)
    const dst = join(targetDir, `${name}.json`)
    if (!existsSync(src)) {
      console.warn(`  ⚠  ${name}.json not found in ${sourceDir} — skipping`)
      missing.push(name)
      continue
    }
    await copyFile(src, dst)
    console.log(`  ✓  ${name}.json → data/current/`)
  }

  // Write a meta file so slides know which date is active
  await writeFile(
    join(targetDir, 'meta.json'),
    JSON.stringify({ date: dateStr }, null, 2),
    'utf8',
  )

  if (missing.length > 0) {
    console.warn(`\nWarning: ${missing.length} file(s) missing — some slides may be incomplete.`)
  }

  console.log(`\nData prepared from: ${dateStr}`)
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
