"""قالب‌های `.gitignore` برای زبان‌ها و ابزارهای رایج."""

GITIGNORES: dict[str, str] = {
    "python": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtualenv
.venv
venv/
ENV/
env/

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
.mypy_cache/
.ruff_cache/

# Distribution
*.whl

# IDE
.idea/
.vscode/
""",
    "node": """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*
.pnpm-debug.log*

# Build
dist/
build/
.next/
.nuxt/
out/

# Cache
.cache/
.parcel-cache/
.eslintcache

# Env
.env
.env.local
.env.*.local

# IDE
.idea/
.vscode/
""",
    "go": """# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out

# Vendor
vendor/

# Binary
/bin/
main
""",
    "rust": """# Rust
/target/
**/*.rs.bk
Cargo.lock

# Debug
*.pdb
""",
    "java": """# Java
*.class
*.jar
*.war
*.ear
*.nar
hs_err_pid*
replay_pid*

# Maven
target/

# Gradle
.gradle/
build/

# IDE
.idea/
*.iml
""",
    "cpp": """# C/C++
*.o
*.obj
*.exe
*.out
*.app
*.so
*.dylib
*.dll

# Build directories
build/
cmake-build-*/

# Debug
*.dSYM/
""",
    "macos": """# macOS
.DS_Store
.AppleDouble
.LSOverride
._*

# Thumbnails
**/.Spotlight-V100
**/.Trashes
**/.fseventsd
""",
    "windows": """# Windows
Thumbs.db
Thumbs.db:encryptable
ehthumbs.db
ehthumbs_vista.db
Desktop.ini
$RECYCLE.BIN/
*.lnk
""",
    "linux": """# Linux
*~
.fuse_hidden*
.directory
.Trash-*
.nfs*
""",
    "vscode": """# VS Code
.vscode/*
!.vscode/settings.json
!.vscode/tasks.json
!.vscode/launch.json
!.vscode/extensions.json
!.vscode/*.code-snippets
.history/
*.vsix
""",
    "jetbrains": """# JetBrains IDEs
.idea/
*.iml
*.iws
*.ipr
out/
""",
    "vim": """# Vim
[._]*.s[a-v][a-z]
[._]*.sw[a-p]
[._]s[a-rt-v][a-z]
[._]ss[a-gi-z]
[._]sw[a-p]
Session.vim
.netrwhist
*~
""",
}


def combine_gitignores(langs: list[str]) -> str:
    """ترکیب چند .gitignore با جداکننده."""
    parts: list[str] = []
    for lang in langs:
        key = lang.lower()
        if key not in GITIGNORES:
            raise ValueError(
                f"زبان ناشناخته: {lang}. "
                f"موارد مجاز: {', '.join(GITIGNORES.keys())}"
            )
        parts.append(GITIGNORES[key].rstrip())
    return "\n\n".join(parts) + "\n"


def list_gitignores() -> list[str]:
    """لیست همهٔ زبان‌ها و ابزارها."""
    return sorted(GITIGNORES.keys())
