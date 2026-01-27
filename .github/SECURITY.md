# Security Policy

## Current Security Configuration

### Branch Protection (`main`)

Our main branch is protected with the following rules:

- ✅ **Pull Request Required** — All changes must go through PR with at least 1 approval
- ✅ **Code Owner Review** — Changes to critical paths require `@edyhvh` approval (see [CODEOWNERS](.github/CODEOWNERS))
- ✅ **Status Checks** — Must pass before merging:
  - `Validate JSON Files` — Ensures data integrity
  - `Frontend Checks` — Linting and type checking
  - `Security Scan` — Dependency vulnerability checks
- ✅ **Conversation Resolution** — All PR comments must be resolved
- ✅ **No Bypass** — Administrators cannot bypass these rules

### Code Ownership

Defined in [`.github/CODEOWNERS`](.github/CODEOWNERS). The following paths require review by `@edyhvh`:

- `/output/` — JSON source files (single source of truth for all texts)
- `/frontend/` — Web application code
- `/scripts/` — Text processing and AI transcription pipelines
- Configuration files (`setup.py`, `requirements.txt`, `Makefile`)

### Automated Security

- ✅ **Dependabot** — Weekly automated dependency updates (configured in [`.github/dependabot.yml`](.github/dependabot.yml))
- ✅ **Security Scanning** — Both `npm audit` (frontend) and `pip-audit` (Python) run on every PR
- ✅ **Workflow Permissions** — GitHub Actions restricted to read-only access + PR comments/checks only

### Workflow Approval

- ✅ **First-time Contributors** — Workflow runs require manual approval for new contributors
- ⚠️ **Workflow Permissions** — Currently set to "Read and write" (required for automated PR updates)

## Manual Setup (For Repository Admins)

### 1. Workflow Permissions

Navigate to: `https://github.com/edyhvh/shafan/settings/actions`

- Set **Workflow permissions** to "Read and write permissions"
- Enable "Allow GitHub Actions to create and approve pull requests"
- Click **Save**

### 2. Signed Commits (Recommended but Optional)

```bash
# Generate GPG key
gpg --full-generate-key

# Export public key
gpg --armor --export YOUR_KEY_ID

# Add to GitHub: Settings → SSH and GPG keys

# Configure Git to sign commits
git config --global commit.gpgsign true
```

Then enable in GitHub: Settings → Branches → Edit rule → Require signed commits

## Security Checklist

- [x] Branch protection enabled on `main`
- [x] CODEOWNERS configured for critical paths
- [x] Automated security scanning (npm audit + pip-audit)
- [x] Dependabot enabled with weekly checks
- [x] Restrictive workflow permissions (read-only by default)
- [x] Workflow approval required for first-time contributors
- [x] Secrets properly managed (no credentials in code)
- [ ] Signed commits required (optional, not yet enforced)

## Reporting Security Vulnerabilities

**Please do NOT create public issues for security vulnerabilities.**

If you discover a security issue, please report it privately:

1. **Email:** Contact `@edyhvh` directly through GitHub
2. **Security Advisory:** Use GitHub's [private vulnerability reporting](https://github.com/edyhvh/shafan/security/advisories/new)

You will receive a response within 48 hours. We appreciate responsible disclosure.

## Data Integrity

This project contains historical religious texts. Data integrity is critical:

- All text corrections must be verified against [original manuscript images](https://huggingface.co/datasets/edyhvh/hutter)
- JSON files in `/output/` are the single source of truth
- See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for the proper correction workflow

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | ✅ Active development |
| other branches | ⚠️ Not monitored for security |

---

**Last Updated:** January 2026
