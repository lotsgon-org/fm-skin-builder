# Automatic Versioning Guide

This project uses **automatic semantic versioning** based on [Conventional Commits](https://www.conventionalcommits.org/).

## Quick Start

### Check Current Version
```bash
./scripts/version.sh
```

This shows:
- Current version from latest tag
- Recent commits
- What the next version will be
- Next beta version

### Create a Release

1. **Check what version will be created:**
   ```bash
   ./scripts/version.sh
   ```

2. **Tag and push:**
   ```bash
   git tag v0.2.0  # Use the version shown above
   git push origin v0.2.0
   ```

3. **GitHub Actions automatically:**
   - Builds for all platforms
   - Uploads to R2
   - Creates GitHub Release

## How Versioning Works

Version is automatically calculated from your commit messages since the last tag.

### Commit Types

| Commit Message | Version Change | Example |
|---------------|----------------|---------|
| `feat: add user profile` | Minor bump | 0.1.0 → 0.2.0 |
| `fix: save button bug` | Patch bump | 0.1.0 → 0.1.1 |
| `feat!: redesign API` | Minor bump (0.x) | 0.1.0 → 0.2.0 |
| `docs: update README` | No change | - |
| `chore: update deps` | No change | - |

**Note**: For 0.x versions, breaking changes bump the minor version (following semver spec).

## Examples

### Example 1: First Release

```bash
# No tags exist yet
$ ./scripts/version.sh
Current version: v0.1.0
Next release: v0.1.0
Next beta: 0.1.0-beta.abc123

# Create first release
$ git tag v0.1.0
$ git push origin v0.1.0
```

### Example 2: Adding Features

```bash
# Latest tag: v0.1.0
$ git commit -m "feat: add dark mode"
$ git commit -m "feat: add export functionality"

$ ./scripts/version.sh
Current version: v0.1.0
Next release: v0.2.0  # Features bump minor
Next beta: 0.2.0-beta.def456

# When ready to release
$ git tag v0.2.0
$ git push origin v0.2.0
```

### Example 3: Bug Fixes Only

```bash
# Latest tag: v0.2.0
$ git commit -m "fix: memory leak"
$ git commit -m "fix: crash on startup"

$ ./scripts/version.sh
Current version: v0.2.0
Next release: v0.2.1  # Fixes bump patch
Next beta: 0.2.1-beta.xyz789

# When ready to release
$ git tag v0.2.1
$ git push origin v0.2.1
```

## Beta Builds

Beta builds are created automatically when you push to the `beta` branch.

### Creating a Beta Build

```bash
# 1. Create feature from beta
$ git checkout beta
$ git pull
$ git checkout -b feat/my-feature

# 2. Develop with conventional commits
$ git commit -m "feat: add awesome feature"
$ git commit -m "fix: resolve bug"

# 3. Open PR to beta (not main!)
# → Tests run, no builds yet

# 4. Merge PR to beta
# → Triggers automatic beta build
```

GitHub Actions will:
1. Calculate next version automatically (e.g., `0.2.0-beta.abc123`)
2. Build all platforms
3. Upload to R2 at `/beta/0.2.0-beta.abc123/`

### Testing Beta Builds

1. Download from R2
2. Test on all platforms
3. If issues found:
   ```bash
   git checkout beta
   git commit -m "fix: issue found in beta"
   git push  # Creates new beta build
   ```

### Promoting to Release

When beta is stable, just merge to main:

**Option 1: Pull Request (Recommended)**
```bash
# Create PR from beta to main on GitHub
# Review → Merge
# → Auto-tags and builds! ✨
```

**Option 2: Direct Merge**
```bash
$ git checkout main
$ git merge beta
$ git push origin main
# → Auto-tags (e.g., v0.2.0) ✨
# → Triggers release build automatically
```

**Check version first (optional):**
```bash
$ ./scripts/version.sh  # Shows what version will be created
```

## Best Practices

### Use Conventional Commits

Always format commits as: `<type>: <description>`

```bash
feat: add new feature
fix: resolve bug
docs: update documentation
chore: update dependencies
refactor: improve code structure
test: add tests
perf: improve performance
```

### When to Use Each Type

- **feat**: New functionality users can see
- **fix**: Bug fixes users will notice
- **perf**: Performance improvements
- **refactor**: Code changes with no user impact
- **docs**: Documentation only
- **chore**: Maintenance (deps, config, etc.)
- **test**: Test additions or changes

### Breaking Changes

For 0.x versions, use `feat!:` or include `BREAKING CHANGE` in the commit body:

```bash
# Option 1: Add ! after type
git commit -m "feat!: redesign API"

# Option 2: Include BREAKING CHANGE in body
git commit -m "feat: redesign API

BREAKING CHANGE: Old API endpoints removed"
```

Both result in a minor version bump for 0.x versions.

## Common Questions

### Q: What if I make a mistake?

**A:** If auto-tag created wrong version, delete it quickly:
```bash
git tag -d v0.2.0          # Delete locally
git push origin :v0.2.0     # Delete remotely (if pushed)
```

Then fix your commits in beta and re-merge to main.

### Q: Can I manually override the version?

**A:** Yes, but not recommended. The version script supports:
```bash
python3 scripts/get_next_version.py --bump-type major
python3 scripts/get_next_version.py --bump-type minor
python3 scripts/get_next_version.py --bump-type patch
```

### Q: What happens if I don't use conventional commits?

**A:** Commits without conventional format (feat, fix, etc.) won't bump the version. The next release will have the same version as the last tag.

### Q: When should I create a release vs push to beta?

- **Beta**: For testing, preview builds, continuous deployment
- **Release**: When stable and ready for users

### Q: How do I transition to 1.0.0?

When you're ready for production:
```bash
git tag v1.0.0
git push origin v1.0.0
```

After 1.0.0:
- `feat!:` and `BREAKING CHANGE` bump major (1.0.0 → 2.0.0)
- `feat:` bumps minor (1.0.0 → 1.1.0)
- `fix:` bumps patch (1.0.0 → 1.0.1)

## Troubleshooting

### Version script not working

Make sure you have Python 3:
```bash
python3 --version  # Should be 3.7+
```

### Git tags not showing

Fetch tags from remote:
```bash
git fetch --tags
```

### Wrong version calculated

Check your commit messages:
```bash
git log --oneline $(git describe --tags --abbrev=0)..HEAD
```

Make sure they follow conventional commit format.

## Resources

- [Conventional Commits Spec](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Workflow Strategy](.github/WORKFLOW_STRATEGY.md)
