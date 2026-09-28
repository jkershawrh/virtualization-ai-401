#!/usr/bin/env node
import { readFile } from 'node:fs/promises'
import { resolve } from 'node:path'

const path = resolve(process.argv[2] ?? 'demo-blueprint.yaml')
const blueprint = await readFile(path, 'utf8')
const errors = []
const required = ['identity:', 'sources:', 'story:', 'architecture:', 'authority:', 'evidence:', 'runtime:']
for (const section of required) if (!blueprint.includes(`\n${section}`) && !blueprint.startsWith(section)) errors.push(`Missing ${section}`)
for (const state of ['OBSERVE', 'PREFLIGHT', 'PROPOSE', 'APPROVE', 'EXECUTE', 'VALIDATE', 'LEARN']) if (!blueprint.includes(state)) errors.push(`Missing journey state: ${state}`)
for (const term of ['ALLOW_REVIEW', 'REFUSE', 'ABSTAIN', 'human_approval_required', 'automated_remediation', 'llm_may_execute', 'LIVE', 'REHEARSAL', 'OFFLINE']) if (!blueprint.includes(term)) errors.push(`Missing governance term: ${term}`)
for (const error of errors) console.error(`ERROR ${error}`)
if (errors.length) process.exit(1)
console.log(`Blueprint structure is valid: ${path}`)
