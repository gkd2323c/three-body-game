# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Interactive fiction game adapting Liu Cixin's "Three-Body Problem" trilogy into branching narrative games. Pure frontend, runs in browser, deployed via Cloudflare Pages.

**Live**: https://threebody.gkd2323c.in

## Commands

```bash
# Validate (run before any commit)
python scripts/merge-game.py --validate    # Book 1
python scripts/merge-game-2.py --validate  # Book 2

# Strict validation (all nodes must be reachable)
python scripts/merge-game.py --strict
python scripts/merge-game-2.py --strict

# Merge batch files into game.json (runs automatically on Cloudflare Pages deploy)
python scripts/merge-game.py
python scripts/merge-game-2.py

# Standalone JSON validation
python skills/scripts/validate.py <json-file-path>
```

## Architecture

### Data Flow

```
output/three-body-{1,2}/*.json  (batch JSONs, one per chapter)
        ↓ merge scripts
site/three-body-{1,2}/game.json (merged game data)
        ↓ loaded by
site/play/launcher.html         (game engine, single-file HTML/JS)
```

### Directory Structure

- `output/three-body-1/` — Book 1 batch JSONs (18 batches)
- `output/three-body-2/` — Book 2 batch JSONs (13 batches)
- `site/` — Website root (Cloudflare Pages)
- `site/play/launcher.html` — Game engine (山音 · Story-to-game)
- `docs/{three-body-1,three-body-2}/` — Planning docs: index, style, topology, state design
- `skills/SKILL.md` — 9-step writing workflow rules
- `skills/references/` — Detailed rule docs (7 files)
- `skills/scripts/validate.py` — JSON validation script
- `novel/` — Original novel text (local reference, not committed)

### JSON Format

Each game.json contains: `meta`, `startNodeId`, `variables`, `achievements`, `nodes`. Nodes have `segments` (text), `choices` (player options), `routes` (conditional branching), `next` (auto-advance), `isEnding`, `progress`.

### Merge Scripts

- `scripts/merge-game.py` — Book 1: reads `output/three-body-1/三体1-第*批-*.json`
- `scripts/merge-game-2.py` — Book 2: reads `output/three-body-2/三体2-第*批-*.json`

Both handle batch transitions (removing end-of-batch nodes, redirecting references), sort main batches before bridge batches, and write merged output to `site/three-body-{1,2}/game.json`.

`BATCH_TRANSITIONS` dict in each script maps end-of-batch node IDs to start-of-next-batch node IDs.

### Validation Rules

The validator checks: node reachability (BFS), reference integrity, no dead ends, endings reachable, achievement count > ending count, no meta-narrative vocabulary, routes have default fallback, choices don't directly jump to non-rash endings, same-direction choices require independent callback nodes.

## Key Conventions

- Batch JSONs are named `三体1-第N批-章节名.json` / `三体2-第N批-章节名.json`
- Bridge/interface batches have `meta.batchInterface.type != "main"` and sort after main batches
- Node IDs follow pattern: `ch{chapter}_{scene}_{number}` (e.g., `ch1_cd_001`)
- `progress` values range 0-100, monotonically increasing along any path
- Ending types: TRUE, NORMAL, BRANCH, HIDDEN, SPECIAL, RASH
- variableName should be dramatic/tension-loaded, not generic (e.g., "灼见" not "勇气")
