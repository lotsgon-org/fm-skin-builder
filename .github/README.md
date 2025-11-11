# GitHub Workflows & Release Process

This directory contains GitHub Actions workflows and release documentation.

## Quick Links

### 📖 Start Here
- **[Release Process](RELEASE_PROCESS.md)** - Quick guide for creating releases (TL;DR)
- **[Branch Strategy](BRANCH_STRATEGY.md)** - Complete branching model and workflow

### 📚 Detailed Docs
- **[Versioning Guide](VERSIONING.md)** - How automatic versioning works
- **[Workflow Strategy](WORKFLOW_STRATEGY.md)** - CI/CD implementation details

## TL;DR

### Daily Development
```bash
# Work in beta, use conventional commits
git checkout beta
git checkout -b feat/my-feature
git commit -m "feat: add awesome feature"
git push
# → PR to beta → merge → auto beta build
```

### Creating a Release
```bash
# Just create a PR: beta → main, then merge
# → Auto-tags with correct version
# → Auto-builds and publishes to R2
```

That's it! No manual tagging, no manual versioning.

## Key Concepts

### Automatic Versioning
Version is calculated from conventional commits:
- `feat:` → Minor bump (0.1.0 → 0.2.0)
- `fix:` → Patch bump (0.1.0 → 0.1.1)
- `docs:` → No bump

### Branch Model
```
beta (development, auto-builds) → main (stable, auto-tags)
```

### Build Triggers
- **Beta branch**: Auto-builds on every push
- **Main branch**: Auto-tags on push, then builds
- **PRs**: Only run tests (fast & cheap)

## Workflows

### `ci.yml`
Runs on: PRs to `main`/`beta`, pushes to `main`/`beta`
Does: Tests + linting
Cost: ~$0.01 per run

### `auto-tag.yml`
Runs on: Pushes to `main`
Does: Calculates version, creates tag
Cost: ~$0.01 per run

### `build-app.yml`
Runs on: Pushes to `beta`, tags (`v*`)
Does: Full platform builds + R2 upload
Cost: ~$0.80 per run

### `build-catalogue.yml`
Runs on: Manual trigger
Does: FM asset catalogue extraction
Cost: Variable

## Cost Optimization

- Tests run on every PR: **$0.01** ✅
- Builds only on beta/releases: **$0.80** ✅
- **98% cost reduction** vs building on every PR ✅

## Getting Started

1. Read [RELEASE_PROCESS.md](RELEASE_PROCESS.md)
2. Create `beta` branch if it doesn't exist
3. Set up R2 credentials in repository secrets
4. Start developing!

## Questions?

Check the detailed docs above, or open an issue.
