#!/usr/bin/env node
import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const path = resolve(process.argv[2] ?? 'demo-blueprint.yaml')
const blueprint = await readFile(path, 'utf8')
const errors = []
const required = ['source:', 'intent:', 'architecture:', 'operational_pattern:', 'evidence:', 'decisions:', 'ai_assessment:', 'story_mapping:']
for (const section of required) if (!blueprint.includes(`\n${section}`) && !blueprint.startsWith(section)) errors.push(`Missing ${section}`)
if (!/operational_pattern:[\s\S]*?steps:\s*\n\s+-\s+/m.test(blueprint)) errors.push('Operational pattern needs steps.')
if (!/architecture:[\s\S]*?flows:\s*\n\s+-\s+/m.test(blueprint)) errors.push('Architecture needs flows.')
for (const term of ['identity-boundary', 'network-boundary', 'placement-boundary', 'observability-boundary', 'authority-boundary', 'REFUSE', 'ABSTAIN', 'HUMAN_REVIEW_REQUIRED']) if (!blueprint.includes(term)) errors.push(`Missing governance term: ${term}`)
for (const error of errors) console.error(`ERROR ${error}`)
if (errors.length) process.exit(1)
console.log(`Blueprint structure is valid: ${path}`)
