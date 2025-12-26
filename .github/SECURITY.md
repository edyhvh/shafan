# Security Configuration

## Current Protection

### Branch Protection (`main`)
- ✅ Require PR before merging (1 approval)
- ✅ Require Code Owner review
- ✅ Require status checks: `Validate JSON Files`, `Frontend Checks`, `Security Scan`
- ✅ Require conversation resolution
- ✅ No bypass allowed (includes administrators)

### Code Owners
Defined in `.github/CODEOWNERS`. `@edyhvh` must approve changes to:
- `/output/` - JSON source files
- `/frontend/` - Frontend code
- `/scripts/` - Processing scripts
- Configuration files

### Automated Security
- ✅ **Dependabot**: Weekly dependency updates (`.github/dependabot.yml`)
- ✅ **Security Scan**: npm audit + pip-audit in PR checks workflow
- ✅ **Workflow Permissions**: Restricted to read-only + PR comments/checks

### Workflow Approval
- ✅ **First-time contributors**: Require approval for workflows
- ⚠️ **Workflow permissions**: Set to "Read and write" in GitHub Settings → Actions

## Manual Setup Required

### 1. Workflow Permissions
Go to: `https://github.com/edyhvh/shafan/settings/actions`

- **Workflow permissions**: Select "Read and write permissions"
- **Save**

### 2. Signed Commits (Optional)
1. Generate GPG key: `gpg --full-generate-key`
2. Export: `gpg --armor --export YOUR_KEY_ID`
3. Add to GitHub: Settings → SSH and GPG keys
4. Configure Git: `git config --global commit.gpgsign true`
5. Enable in branch protection: Settings → Branches → Require signed commits

## Security Checklist

- [x] Branch protection enabled
- [x] CODEOWNERS configured
- [x] Automated security scanning
- [x] Dependabot enabled
- [x] Restrictive workflow permissions
- [x] Workflow approval for first-time contributors
- [ ] Workflow permissions: "Read and write" (needs update)
- [ ] Signed commits required (optional)
- [x] Secrets properly managed

## Reporting Security Issues

**Do NOT** create public issues. Email security concerns directly.
