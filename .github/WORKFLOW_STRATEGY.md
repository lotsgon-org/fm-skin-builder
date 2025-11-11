# GitHub Actions Workflow Strategy

This document outlines our build and release strategy designed to minimize costs while maintaining quality.

## Overview

We use a multi-tiered approach:
- **CI Tests**: Run on all PRs and pushes to `main`/`beta` (lightweight, fast)
- **Builds**: Only run on `beta` branch and version tags (expensive, controlled)
- **Releases**: Automatic R2 upload + GitHub release when all platforms succeed

## Branch Strategy

### `beta` branch (PRIMARY DEVELOPMENT)
- **Purpose**: Active development + testing builds
- **What runs**: Full build pipeline for all platforms
- **Versioning**: `0.x.y-beta.<commit-sha>` (automatic)
- **Upload**: Artifacts uploaded to R2 at `/beta/0.x.y-beta.abc123/`
- **When**: Every push to beta
- **Flow**: Feature branches → `beta` (for testing)

### `main` branch (STABLE RELEASES)
- **Purpose**: Stable, release-ready code
- **What runs**: Tests + Linting only (no builds on push)
- **Flow**: `beta` → `main` (when stable)
- **Releases**: Tag `main` to create official releases

### Feature branches / Pull Requests
- **Purpose**: Development and review
- **Target**: Merge to `beta` (not `main`)
- **What runs**: Tests + Linting only
- **No builds**: Keeps PR validation fast and cheap

### Version Tags (`v*`)
- **Purpose**: Official releases
- **Applied to**: `main` branch (after merging from `beta`)
- **What runs**: Full build pipeline + release creation
- **Versioning**: `v0.x.y` or `v0.x.y-alpha.N`
- **Upload**: Artifacts uploaded to R2 at `/releases/0.x.y/` + GitHub Release

## Cost Optimization Features

### 1. Tests Must Pass First
All builds have `needs: test` dependency, so expensive builds never run if tests fail.

### 2. Fail-Fast Strategy
```yaml
strategy:
  fail-fast: true  # Stop all jobs if one fails
```
If Linux build fails, macOS/Windows builds are cancelled immediately.

### 3. Minimal Build Triggers
Builds only run on:
- `beta` branch pushes
- `v*` version tags
- Manual workflow dispatch

### 4. Comprehensive Caching
- pip dependencies cached
- npm dependencies cached
- Cargo/Rust build cache
- Artifact sharing between jobs

## Automatic Versioning with Conventional Commits

We use **semantic versioning** with automatic version bumping based on conventional commits.

### How It Works

The version is automatically determined by analyzing commit messages since the last tag:

| Commit Type | Example | Version Bump |
|-------------|---------|--------------|
| `feat:` | `feat: add dark mode` | Minor (0.1.0 → 0.2.0) |
| `fix:` | `fix: button alignment` | Patch (0.1.0 → 0.1.1) |
| `feat!:` or `BREAKING CHANGE` | `feat!: redesign API` | Minor for 0.x (0.1.0 → 0.2.0) |
| `docs:`, `chore:`, etc. | `docs: update README` | No bump |

**Note**: For pre-1.0.0 versions, breaking changes bump the minor version (not major), following semver conventions.

### Version Formats

- **Beta builds** (from `beta` branch): `0.x.y-beta.<commit-sha>`
  - Example: `0.2.0-beta.abc123`
  - Version calculated automatically from commits

- **Release builds** (from tags): `0.x.y`
  - Example: `v0.2.0`
  - You tag manually when ready to release

### Examples

**Scenario 1: First release**
```bash
# No tags yet
git log:
  - feat: initial commit

→ Next version: 0.1.0
→ Beta version: 0.1.0-beta.abc123
```

**Scenario 2: After v0.1.0 tag**
```bash
# Latest tag: v0.1.0
git log since v0.1.0:
  - feat: add user settings
  - fix: save button bug

→ Next version: 0.2.0 (feat bumps minor)
→ Beta version: 0.2.0-beta.def456
```

**Scenario 3: Only bug fixes**
```bash
# Latest tag: v0.2.0
git log since v0.2.0:
  - fix: memory leak
  - fix: crash on startup

→ Next version: 0.2.1 (fix bumps patch)
→ Beta version: 0.2.1-beta.xyz789
```

### Checking Versions Locally

Use the helper script to see what version will be created:

```bash
# Show full version info
./scripts/version.sh

# Show only next release version
./scripts/version.sh --next

# Show next beta version
./scripts/version.sh --beta
```

### Creating a Release

When you're ready to create a release:

```bash
# Check what version will be created
./scripts/version.sh

# Tag the release (use the version shown above)
git tag v0.2.0
git push origin v0.2.0

# GitHub Actions will automatically build and publish
```

### Pre-1.0.0 vs Post-1.0.0

**Before 1.0.0** (current):
- `feat:` → Minor bump (0.1.0 → 0.2.0)
- `feat!:` → Minor bump (0.1.0 → 0.2.0)
- `fix:` → Patch bump (0.1.0 → 0.1.1)

**After 1.0.0** (future):
- `feat:` → Minor bump (1.0.0 → 1.1.0)
- `feat!:` → Major bump (1.0.0 → 2.0.0)
- `fix:` → Patch bump (1.0.0 → 1.0.1)

## R2 Upload Strategy

### Release Builds (from tags)
```
/releases/
  ├── 0.1.0/
  │   ├── fm-skin-builder-linux-x86_64.AppImage
  │   ├── fm-skin-builder-windows-x86_64.msi
  │   ├── fm-skin-builder-macos-arm64.dmg
  │   └── fm-skin-builder-macos-intel.dmg
  └── 0.2.0/
      └── ...
```

### Beta Builds (from beta branch)
```
/beta/
  ├── 0.1.0-beta.abc123/
  │   ├── fm-skin-builder-linux-x86_64.AppImage
  │   └── ...
  └── 0.1.0-beta.def456/
      └── ...
```

### Upload Behavior
- **Atomic**: All platforms must build successfully before ANY upload occurs
- **Fail-safe**: If macOS build fails, nothing gets uploaded to R2
- **Metadata**: Each file includes version and build-type in R2 metadata

## Required Secrets & Variables

### Secrets (Repository Settings → Secrets)
```
R2_ACCOUNT_ID              # Cloudflare account ID
R2_ACCESS_KEY              # R2 access key ID
R2_SECRET_ACCESS_KEY       # R2 secret access key
TAURI_SIGNING_PRIVATE_KEY  # Optional: Tauri update signing
TAURI_SIGNING_PRIVATE_KEY_PASSWORD
WINDOWS_CERTIFICATE        # Optional: Windows code signing
WINDOWS_CERTIFICATE_PASSWORD
```

### Variables (Repository Settings → Variables)
```
R2_RELEASES_BUCKET         # R2 bucket name for releases (e.g., "fm-skin-builder-releases")
```

## Workflow Files

- **`ci.yml`**: Fast tests + linting (runs on all PRs)
- **`auto-tag.yml`**: Auto-create version tags on main pushes
- **`build-app.yml`**: Full build pipeline (beta + tags only)
- **`build-catalogue.yml`**: Asset catalogue builds (manual trigger)

## Development Workflow

### Working on Features
1. Create feature branch from `beta`
   ```bash
   git checkout beta
   git pull
   git checkout -b feat/my-feature
   ```

2. Develop and commit using conventional commits
   ```bash
   git commit -m "feat: add awesome feature"
   git commit -m "fix: resolve edge case"
   ```

3. Open PR to `beta` (not `main`)
   - Tests run automatically
   - No builds (fast and cheap)

4. Merge to `beta`
   - Full builds triggered automatically
   - Beta version created (e.g., `0.2.0-beta.abc123`)
   - Uploaded to R2 `/beta/` path

### Testing Beta Builds
1. Download from R2 `/beta/0.2.0-beta.abc123/`
2. Test thoroughly on all platforms
3. If issues found, fix in `beta` branch → new beta build
4. Repeat until stable

### Promoting to Stable Release

**Recommended: Use Pull Request**
1. Create PR: `beta` → `main` on GitHub
2. Review the changes being released
3. Merge PR
4. **Auto-magic happens:**
   - Version calculated automatically (e.g., `v0.2.0`)
   - Tag created automatically
   - Full builds triggered for all platforms
   - If all succeed:
     - Artifacts uploaded to R2 `/releases/0.2.0/`
     - GitHub Release created with artifacts
     - Release notes auto-generated

**Alternative: Direct Merge**
```bash
git checkout main
git pull
git merge beta
git push origin main
# → Same auto-magic as above ✨
```

**Check version first (optional):**
```bash
./scripts/version.sh  # Shows what version will be created
```

### Quick Reference

```
Feature → beta (PR, tests only)
       ↓
     Merge (auto-build beta)
       ↓
   Test beta build
       ↓
  beta → main (PR or merge)
       ↓
  Auto-tag ✨ (auto-build release)
```

## Cost Estimates

Based on GitHub Actions pricing (macOS is 10x Linux cost):

### Before Optimization
- Every PR: 2 macOS builds (~$0.80)
- Every main push: 2 macOS builds (~$0.80)
- **~$1.60 per PR/push**

### After Optimization
- PRs: Only tests on Linux (~$0.01)
- Main pushes: Only tests on Linux (~$0.01)
- Beta pushes: Full builds (~$0.80)
- **~$0.01 per PR, ~$0.80 per beta/release**

**Savings**: ~98% reduction in build costs for normal development workflow!

## Future Enhancements

### Automatic Semantic Versioning (Post-1.0.0)
Once we reach v1.0.0, we can implement:
- Conventional Commits parsing
- Automatic version bumping
- Changelog generation

### Advanced R2 Features
- CDN integration for fast downloads
- Automatic cleanup of old beta builds
- Download statistics tracking

### Additional Optimizations
- Split builds by urgency (fast vs. complete)
- Scheduled builds for nightly releases
- Matrix reduction (e.g., only ARM64 macOS for betas)
