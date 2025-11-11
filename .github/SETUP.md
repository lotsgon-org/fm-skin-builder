# Setup Guide

Complete setup guide for the automated release system.

## Prerequisites

1. **GitHub repository** with admin access
2. **Cloudflare R2** account with bucket created
3. **Git installed** locally

## Step 1: Create Beta Branch

```bash
# Create and push beta branch
git checkout -b beta
git push -u origin beta

# Set beta as default branch in GitHub (optional but recommended)
# Settings → Branches → Default branch → beta
```

## Step 2: Configure R2 Credentials

### 2.1 Get R2 Credentials

1. Log in to Cloudflare Dashboard
2. Go to **R2** → **Overview**
3. Click **Manage R2 API Tokens**
4. Create a new API token with:
   - **Permissions**: Object Read & Write
   - **Bucket**: Your releases bucket (or all buckets)
5. Save the credentials:
   - **Account ID**: `abc123...`
   - **Access Key ID**: `xyz789...`
   - **Secret Access Key**: `secret123...`

### 2.2 Add to GitHub Secrets

Go to: **Repository Settings → Secrets and variables → Actions**

**Add these Secrets:**
```
R2_ACCOUNT_ID              = abc123...
R2_ACCESS_KEY              = xyz789...
R2_SECRET_ACCESS_KEY       = secret123...
```

**Add these Variables:**
```
R2_RELEASES_BUCKET         = your-bucket-name
```

## Step 3: Configure Branch Protection (Optional)

### For `main` branch:
1. **Settings → Branches → Add rule**
2. Branch name pattern: `main`
3. Enable:
   - ✅ Require pull request before merging
   - ✅ Require status checks to pass before merging
     - Add: `test`, `lint`
   - ✅ Require branches to be up to date before merging

### For `beta` branch:
1. **Settings → Branches → Add rule**
2. Branch name pattern: `beta`
3. Enable:
   - ✅ Require status checks to pass before merging
     - Add: `test`, `lint`

## Step 4: Test the Setup

### Test 1: CI on PR
```bash
# Create a test branch
git checkout beta
git checkout -b test/setup
git commit --allow-empty -m "test: setup verification"
git push origin test/setup

# Create PR to beta
# → CI should run (tests + linting)
# → Should take ~1 minute
```

### Test 2: Beta Build
```bash
# Merge the PR to beta
# → Build workflow should trigger
# → Should take ~10-15 minutes
# → Check R2 bucket for: /beta/0.1.0-beta.abc123/
```

### Test 3: Release
```bash
# Check what version will be created
./scripts/version.sh
# Should show: Next release: v0.1.0

# Merge beta to main
git checkout main
git merge beta
git push origin main

# → Auto-tag workflow runs
# → Creates tag v0.1.0
# → Build workflow triggers
# → Should take ~10-15 minutes
# → Check R2 bucket for: /releases/0.1.0/
# → Check GitHub Releases for new release
```

## Step 5: Verify Everything Works

Check these locations:

### R2 Bucket Structure
```
your-bucket/
├── beta/
│   └── 0.1.0-beta.abc123/
│       ├── fm-skin-builder-linux-x86_64.AppImage
│       ├── fm-skin-builder-windows-x86_64.msi
│       ├── fm-skin-builder-macos-arm64.dmg
│       └── fm-skin-builder-macos-intel.dmg
└── releases/
    └── 0.1.0/
        ├── fm-skin-builder-linux-x86_64.AppImage
        ├── fm-skin-builder-windows-x86_64.msi
        ├── fm-skin-builder-macos-arm64.dmg
        └── fm-skin-builder-macos-intel.dmg
```

### GitHub Releases
- Go to: **Releases** tab on GitHub
- Should see: **v0.1.0** with artifacts attached

## Optional: Code Signing (Recommended)

### Windows Code Signing
```bash
# Export your certificate as base64
base64 -i certificate.pfx -o certificate.txt

# Add to GitHub Secrets:
WINDOWS_CERTIFICATE         = (contents of certificate.txt)
WINDOWS_CERTIFICATE_PASSWORD = your_password
```

### Tauri Update Signing
```bash
# Generate signing key
# (Follow Tauri docs)

# Add to GitHub Secrets:
TAURI_SIGNING_PRIVATE_KEY          = your_private_key
TAURI_SIGNING_PRIVATE_KEY_PASSWORD = your_password
```

## Troubleshooting

### "R2_ACCOUNT_ID not found"
- Check secrets are added to **Actions** section (not Dependabot or Codespaces)
- Secret names must match exactly (case-sensitive)

### "Permission denied to push tag"
- Workflow needs `contents: write` permission (already configured)
- Check branch protection rules don't block workflow pushes

### Beta build not triggering
- Ensure beta branch exists: `git branch -r | grep beta`
- Check Actions tab for workflow runs
- Look for workflow file syntax errors

### Auto-tag not working
- Check `auto-tag.yml` workflow file exists
- Verify pushes to `main` trigger the workflow
- Check Actions logs for errors

### Builds failing on macOS
- This is expected on first run (expensive)
- Check that Python backend builds successfully
- Verify Cairo is installed in workflow

## Next Steps

1. Read [RELEASE_PROCESS.md](RELEASE_PROCESS.md) for daily workflow
2. Start developing with conventional commits
3. Create first beta build by pushing to beta
4. When stable, create first release via PR to main

## Getting Help

- Check [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) for workflow details
- Check [VERSIONING.md](VERSIONING.md) for version calculation
- Check [WORKFLOW_STRATEGY.md](WORKFLOW_STRATEGY.md) for CI/CD details
- Open an issue if you're stuck
