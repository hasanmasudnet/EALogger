# Publishing EALogger to PyPI

## Prerequisites

1. **Create PyPI accounts:**

   - Production: https://pypi.org/account/register/
   - Test: https://test.pypi.org/account/register/

2. **Install build tools:**
   ```bash
   pip install build twine
   ```

## Before Publishing

### 1. Verify Package Details

Check `pyproject.toml`:

- ✅ Package name: `EALogger` (available on PyPI)
- ✅ Author info (name + real email)
- ✅ Version number (not duplicate of existing releases)
- ✅ Description, keywords, classifiers
- ✅ GitHub URL

### 2. Create Test PyPI Account & API Token

Go to https://test.pypi.org/manage/account/token/ and create:

- **Scope:** Project scope, select "EALogger"
- **Token name:** `ealogger-test-upload`
- Copy the token: `pypi-AgEIc...` (starts with `pypi-`)

### 3. Create Production PyPI API Token

Go to https://pypi.org/manage/account/token/ and create:

- **Scope:** Project scope, select "EALogger" (will be created)
- **Token name:** `ealogger-prod-upload`
- Copy the token

## Publishing to Test PyPI (Optional but Recommended)

```bash
cd D:\Projects\PG.AI\EALogger

# 1. Clean previous builds
Remove-Item dist\* -Force
Remove-Item build\* -Recurse -Force

# 2. Build package
python -m build

# 3. Check package
python -m twine check dist\*

# 4. Upload to Test PyPI
python -m twine upload --repository testpypi dist\*
# Username: __token__
# Password: pypi-AgEIc... (your test PyPI token)
```

### Test Installation from Test PyPI

```bash
# Uninstall local version first
pip uninstall EALogger -y

# Install from Test PyPI
pip install -i https://test.pypi.org/simple/ "EALogger[fast]"

# Test it
python -c "import EALogger; print(EALogger.__version__)"
```

## Publishing to Production PyPI

```bash
cd D:\Projects\PG.AI\EALogger

# 1. Update version numbers
# Edit: src/EALogger/__init__.py (line 17)
# Edit: pyproject.toml (line 7)

# 2. Commit changes
git add .
git commit -m "Release v0.2.0"
git tag v0.2.0
git push origin main --tags

# 3. Clean previous builds
Remove-Item dist\* -Force
Remove-Item build\* -Recurse -Force

# 4. Build package
python -m build

# 5. Check package
python -m twine check dist\*

# 6. Upload to PyPI
python -m twine upload dist\*
# Username: __token__
# Password: pypi-AgEIc... (your production PyPI token)
```

## After Publishing

### 1. Verify on PyPI

- Check: https://pypi.org/project/EALogger/
- Verify all fields display correctly
- Check "Homepage" links to your GitHub repo

### 2. Test Installation

```bash
# Create clean virtual environment
python -m venv test_env
test_env\Scripts\activate

# Install from PyPI
pip install "EALogger[fast]"

# Test it
python -c "from EALogger import get_logger; print('Success!')"
```

### 3. Update Documentation

- Update README with PyPI badge
- Add installation instructions
- Create GitHub release with changelog

### 4. Announce

- Post on GitHub Discussions/Releases
- Update any project docs that reference EALogger

## Troubleshooting

### Error: "Package already exists"

- This version was already published
- Increment version number in `__init__.py` and `pyproject.toml`

### Error: "Invalid username"

- Use `__token__` as username (literal)
- Use your API token as password

### Error: "Package name not available"

- Name `EALogger` already taken
- Change name in `pyproject.toml` and `setup.py`

### Error: "Repository does not exist"

- First publish to production creates the repository
- Or manually reserve name on PyPI first

## Security Notes

⚠️ **Never commit tokens to git!** Store them in:

- Environment variables
- Encrypted password manager
- CI/CD secrets (for automated publishing)

## Common Commands

```bash
# Build only
python -m build

# Check without uploading
python -m twine check dist\*

# Upload to Test PyPI
python -m twine upload --repository testpypi dist\*

# Upload to Production PyPI
python -m twine upload dist\*

# View package on PyPI
start https://pypi.org/project/EALogger/
```

## Version Numbering

Use [SemVer](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (e.g., 1.0.0 → 2.0.0)
- **MINOR**: New features (e.g., 0.2.0 → 0.3.0)
- **PATCH**: Bug fixes (e.g., 0.2.0 → 0.2.1)

Example releases:

- `0.2.0` - Current version
- `0.2.1` - Bug fix
- `0.3.0` - New features
- `1.0.0` - Stable production release
