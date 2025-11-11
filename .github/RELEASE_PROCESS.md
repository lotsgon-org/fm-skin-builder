# Release Process (Quick Guide)

This is the TL;DR for releasing. See [BRANCH_STRATEGY.md](BRANCH_STRATEGY.md) for details.

## Daily Development

```bash
# Work in beta
git checkout beta
git checkout -b feat/my-feature
git commit -m "feat: add feature"
git push

# Create PR to beta → merge
# → Beta build auto-created: 0.2.0-beta.abc123
```

## Creating a Release

When beta is stable and ready:

### Step 1: Create PR (Recommended)

1. Go to GitHub
2. Create Pull Request: `beta` → `main`
3. Review what's being released
4. Merge the PR

**That's it!** Everything else is automatic.

### Step 2: Auto-Magic Happens ✨

When you merge to `main`:

1. **Auto-tag workflow runs**
   - Analyzes conventional commits
   - Calculates next version (e.g., `v0.2.0`)
   - Creates and pushes tag

2. **Release build triggers**
   - Builds all platforms (Linux, Windows, macOS x2)
   - Tests pass → builds succeed
   - Uploads to R2: `/releases/0.2.0/`
   - Creates GitHub Release with artifacts

### Alternative: Direct Merge

If you prefer command line:

```bash
git checkout main
git merge beta
git push
# → Same auto-magic as above
```

## Preview Version Before Release

Want to know what version will be created?

```bash
./scripts/version.sh
```

Shows:
```
Current version: v0.1.0
Next release: v0.2.0
Next beta: 0.2.0-beta.abc123
```

## Version Calculation Rules

Your commits determine the version:

| Commits Since Last Tag | Next Version |
|------------------------|--------------|
| `feat: add feature` | 0.1.0 → **0.2.0** (minor) |
| `fix: bug fix` | 0.1.0 → **0.1.1** (patch) |
| `feat: x` + `fix: y` | 0.1.0 → **0.2.0** (highest wins) |
| `docs:` / `chore:` only | 0.1.0 → **0.1.0** (no bump) |

## Complete Example

```bash
# 1. Develop features in beta
git checkout beta
git commit -m "feat: add user profiles"
git commit -m "feat: add dark mode"
git commit -m "fix: save button bug"
git push
# → Beta build: 0.2.0-beta.abc123

# 2. Test beta build
# Download from R2, test on all platforms

# 3. When stable, create PR: beta → main
# On GitHub: Create PR → Review → Merge

# 4. Auto-magic!
# → Auto-tagged as v0.2.0
# → Release build starts
# → Artifacts uploaded to R2 /releases/0.2.0/
# → GitHub Release created
```

## Workflow Diagram

```
┌──────────────┐
│ Development  │  feat/*, fix/* branches
│   (beta)     │  → PR to beta → merge
└──────┬───────┘  → Auto-build beta
       │
       │ Test beta builds
       │
       ↓
┌──────────────┐
│   Release    │  PR: beta → main
│   (main)     │  → Merge PR
└──────┬───────┘  → Auto-tag ✨
       │
       ↓
  🚀 Published
```

## Troubleshooting

### Wrong version calculated?

Check your commit messages:
```bash
git log $(git describe --tags --abbrev=0)..HEAD --oneline
```

Make sure they follow conventional commit format:
- `feat:` for features
- `fix:` for bug fixes
- `docs:` for documentation
- etc.

### Need to skip a release?

If you merged to main by accident:
```bash
# Delete the auto-created tag
git tag -d v0.2.0
git push origin :v0.2.0
```

### Want to manually tag?

You can disable auto-tagging and manually tag:

1. Merge beta to main (wait for auto-tag workflow)
2. Delete auto-created tag (if you want different version)
3. Create your own tag:
   ```bash
   git tag v0.3.0
   git push origin v0.3.0
   ```

## Benefits of This Workflow

✅ **No manual tagging** - Version calculated automatically
✅ **Review releases** - Use PR to see what's being released
✅ **Test first** - All code tested in beta before release
✅ **Consistent** - Conventional commits enforce versioning rules
✅ **Fast** - No manual steps, just merge and go

## Related Documentation

- [Branch Strategy](BRANCH_STRATEGY.md) - Complete branching model
- [Versioning Guide](VERSIONING.md) - Detailed versioning explanation
- [Workflow Strategy](WORKFLOW_STRATEGY.md) - CI/CD details
