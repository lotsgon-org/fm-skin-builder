# Branch Strategy

This document explains our branch model and workflow.

## Branch Model

```
main (stable releases only)
  ↑
  │ merge when stable
  │
beta (active development, auto-builds)
  ↑
  │ PR merges
  │
feature branches (development)
```

## Key Principles

1. **`beta` is the primary development branch**
   - All features merge here first
   - Automatically builds beta versions for testing
   - Can be unstable, that's OK!

2. **`main` is the stable branch**
   - Only receives code from `beta` when stable
   - Never build on push (just tests)
   - Only builds when tagged for release

3. **Test before promoting**
   - Code must be tested in beta builds before reaching main
   - Prevents untested code from reaching stable branch

## Workflows

### 1. Developing a Feature

```bash
# Start from beta
git checkout beta
git pull
git checkout -b feat/user-profiles

# Develop using conventional commits
git commit -m "feat: add user profile page"
git commit -m "feat: add profile editing"
git commit -m "fix: validation bug"

# Push and create PR to beta
git push origin feat/user-profiles
# Create PR: feat/user-profiles → beta
```

**What happens:**
- CI runs tests on PR ✓
- No builds (cheap & fast) ✓

### 2. Merging to Beta

```bash
# Merge PR to beta via GitHub
# or locally:
git checkout beta
git merge feat/user-profiles
git push origin beta
```

**What happens:**
- Full build triggered automatically ✓
- Version: `0.2.0-beta.abc123` (calculated automatically)
- Uploads to R2: `/beta/0.2.0-beta.abc123/`
- Test these builds!

### 3. Testing Beta

```bash
# Download from R2: /beta/0.2.0-beta.abc123/
# Test on Windows, macOS, Linux

# Found a bug?
git checkout beta
git commit -m "fix: issue found in testing"
git push origin beta
# → New beta build: 0.2.0-beta.def456
```

### 4. Release (When Beta is Stable)

**Option A: Pull Request (Recommended)**

```bash
# Create PR from beta to main on GitHub
# → Review what's being released
# → Merge PR
# → Auto-tags and triggers release build ✨
```

**Option B: Direct Merge**

```bash
# Merge beta to main
git checkout main
git pull
git merge beta
git push origin main

# → Auto-tags (e.g., v0.2.0) ✨
# → Full build triggered automatically
# → Uploads to R2: /releases/0.2.0/
# → Creates GitHub Release
```

**No manual tagging needed!** The version is calculated automatically from your conventional commits.

## Visual Flow

```
┌─────────────────┐
│ feat/my-feature │ ← Develop here
└────────┬────────┘
         │ PR (tests only)
         ↓
    ┌────────┐
    │  beta  │ ← Merge & auto-build beta
    └────┬───┘   (0.2.0-beta.abc123)
         │
         │ Test beta build
         │
         │ When stable
         ↓
    ┌────────┐
    │  main  │ ← PR: beta → main
    └────┬───┘   (or direct merge)
         │
         │ Auto-tag ✨
         ↓
   🚀 Release Build
   (uploads to /releases/)
```

## Branch Protection Rules

### Recommended Settings

**`main` branch:**
- Require pull request reviews
- Require status checks to pass (CI tests)
- Require branches to be up to date
- Restrict who can push (maintainers only)

**`beta` branch:**
- Require status checks to pass (CI tests)
- Allow direct pushes for quick fixes (optional)
- More relaxed than main

**Feature branches:**
- No special protection needed

## FAQ

### Q: Can I push directly to beta?

**A:** Yes, for small fixes. For features, use PRs for code review.

```bash
# Quick fix on beta
git checkout beta
git pull
git commit -m "fix: typo in error message"
git push  # Triggers beta build
```

### Q: What if beta and main diverge?

**A:** They shouldn't diverge if you follow the workflow:
- `beta` is always ahead of `main` (or equal)
- `main` only receives commits from `beta` merges
- Never commit directly to `main`

If they do diverge, you need to reconcile:
```bash
git checkout main
git merge beta  # Resolve conflicts if any
```

### Q: Can I hotfix main directly?

**A:** No, follow this pattern:

```bash
# 1. Fix in beta
git checkout beta
git commit -m "fix: critical bug"
git push  # Creates beta build to verify

# 2. Test beta build

# 3. Merge to main (auto-tags)
git checkout main
git merge beta
git push  # Auto-tags v0.2.1 and triggers release
```

### Q: What about feature flags?

**A:** Great idea! Use feature flags in beta to hide incomplete features:

```typescript
if (process.env.ENABLE_NEW_FEATURE === 'true') {
  // New feature code
}
```

This lets you merge partial features to beta without affecting stability.

### Q: Should I delete old beta builds from R2?

**A:** Yes, periodically clean up old beta builds:

```bash
# Keep last 10 betas, delete older ones
# (Create a cleanup script later)
```

## Comparison with Other Models

### vs. Git Flow
- **Git Flow**: `main`, `develop`, `release/*`, `hotfix/*`, `feature/*`
- **Our Model**: `main`, `beta`, `feature/*`
- **Why Simpler**: Pre-1.0 projects don't need release branches yet

### vs. GitHub Flow
- **GitHub Flow**: Just `main` + feature branches
- **Our Model**: Adds `beta` for testing before stable
- **Why Better**: Can test builds before promoting to stable

### vs. Trunk-Based Development
- **Trunk-Based**: Everyone commits to `main`, very short-lived branches
- **Our Model**: `beta` as trunk, `main` as release branch
- **Why Different**: We need pre-release testing

## When to Reconsider

After reaching v1.0.0, you might want to add:
- Release branches (`release/1.x`)
- Hotfix branches
- Multiple support versions

But for pre-1.0, this model is perfect!
