# Publishing Guide for rapid-mcp-server

This guide explains how to publish the rapid-mcp-server package to PyPI so anyone can install it with `pip install rapid-mcp-server`.

## Publishing Options

### Option 1: Automated Publishing via GitHub Actions (Recommended)

This is the easiest method for ongoing releases.

#### Setup (One-time)

1. **Create a GitHub repository**
   ```bash
   # From the mcp-server directory
   git init
   git add .
   git commit -m "Initial commit of rapid-mcp-server"

   # Create a new repo at github.com/no10ds/rapid-mcp-server
   git remote add origin https://github.com/no10ds/rapid-mcp-server.git
   git push -u origin main
   ```

2. **Configure PyPI Trusted Publishing** (No API tokens needed!)

   a. Go to [https://pypi.org](https://pypi.org) and log in

   b. Navigate to: Account Settings → Publishing → Add a new pending publisher

   c. Fill in:
   - PyPI Project Name: `rapid-mcp-server`
   - Owner: `no10ds`
   - Repository name: `rapid-mcp-server`
   - Workflow name: `publish.yml`
   - Environment name: (leave empty)

   d. Click "Add"

3. **Create a GitHub Release**
   ```bash
   # Tag the release
   git tag v0.1.0
   git push origin v0.1.0

   # Or create a release via GitHub UI:
   # Go to: github.com/no10ds/rapid-mcp-server/releases/new
   # - Tag: v0.1.0
   # - Title: v0.1.0 - Initial Release
   # - Description: (add release notes)
   # - Publish release
   ```

4. **GitHub Actions will automatically**:
   - Build the package
   - Run checks
   - Publish to PyPI

### Option 2: Manual Publishing

For one-off releases or testing.

#### Prerequisites

```bash
pip install build twine
```

#### Steps

1. **Update version number** in `setup.py` and `pyproject.toml`

2. **Build the package**
   ```bash
   cd /Users/abigail.muller/Code/rapid/mcp-server
   python -m build
   ```

   This creates files in `dist/`:
   - `rapid_mcp_server-0.1.0.tar.gz` (source distribution)
   - `rapid_mcp_server-0.1.0-py3-none-any.whl` (wheel)

3. **Check the package**
   ```bash
   twine check dist/*
   ```

4. **Test with TestPyPI** (recommended first time)
   ```bash
   # Create account at test.pypi.org
   twine upload --repository testpypi dist/*

   # Test installation
   pip install --index-url https://test.pypi.org/simple/ rapid-mcp-server
   ```

5. **Publish to PyPI**
   ```bash
   # You'll need PyPI credentials
   twine upload dist/*
   ```

## For New Releases

### Versioning

Follow [Semantic Versioning](https://semver.org/):
- `0.1.0` → `0.1.1` for bug fixes
- `0.1.0` → `0.2.0` for new features
- `0.1.0` → `1.0.0` for breaking changes

### Release Checklist

1. **Update version numbers**
   - `setup.py` (line 8)
   - `pyproject.toml` (line 4)
   - `rapid_mcp_server/__init__.py` (line 3)

2. **Update CHANGELOG** (create if doesn't exist)
   ```markdown
   ## [0.2.0] - 2025-01-15
   ### Added
   - New tool for xyz

   ### Fixed
   - Bug in abc
   ```

3. **Test locally**
   ```bash
   pip install -e .
   python -m rapid_mcp_server.server
   ```

4. **Commit and tag**
   ```bash
   git add .
   git commit -m "Release v0.2.0"
   git tag v0.2.0
   git push origin main --tags
   ```

5. **Create GitHub release** (triggers auto-publish)

## Verification

After publishing, verify:

1. **Package appears on PyPI**
   - Visit: https://pypi.org/project/rapid-mcp-server/

2. **Installation works**
   ```bash
   # In a fresh environment
   pip install rapid-mcp-server
   python -c "import rapid_mcp_server; print(rapid_mcp_server.__version__)"
   ```

3. **MCP server runs**
   ```bash
   rapid-mcp-server --help  # Should show usage
   ```

## Repository Structure

After creating the GitHub repository, it should NOT be inside the main rapid repo. The structure should be:

```
~/Code/
├── rapid/                    # Main rapid platform repo
│   └── ...
└── rapid-mcp-server/         # Separate standalone repo
    ├── .github/
    ├── rapid_mcp_server/
    ├── tests/
    ├── setup.py
    ├── README.md
    └── ...
```

## Moving to Standalone Repository

If currently inside the rapid repo, extract it:

```bash
# Copy to new location
cp -r /Users/abigail.muller/Code/rapid/mcp-server /Users/abigail.muller/Code/rapid-mcp-server

# Initialize as new repo
cd /Users/abigail.muller/Code/rapid-mcp-server
git init
git add .
git commit -m "Initial commit of rapid-mcp-server"

# Push to GitHub
git remote add origin https://github.com/no10ds/rapid-mcp-server.git
git push -u origin main
```

## PyPI Authentication Methods

### Method 1: Trusted Publishing (Recommended)
- No secrets needed
- Most secure
- Works automatically with GitHub Actions
- Setup once via PyPI web interface

### Method 2: API Token
- Generate at: https://pypi.org/manage/account/token/
- Add as GitHub secret: `PYPI_API_TOKEN`
- Update workflow to use: `password: ${{ secrets.PYPI_API_TOKEN }}`

## Troubleshooting

### "Package name already taken"
- The name `rapid-mcp-server` must be available on PyPI
- Check: https://pypi.org/project/rapid-mcp-server/
- If taken, choose a different name in `setup.py`

### "Trusted publishing not configured"
- Ensure you've added the pending publisher on PyPI
- Check the workflow name matches exactly
- Wait a few minutes after setup

### "Build failed"
- Run `python -m build` locally to see errors
- Check all imports work
- Verify `MANIFEST.in` includes all needed files

## Support

For questions about publishing:
- PyPI docs: https://packaging.python.org/
- GitHub Actions: https://docs.github.com/actions
- Open an issue: https://github.com/no10ds/rapid-mcp-server/issues
