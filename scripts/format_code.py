#!/usr/bin/env python3
"""
Auto-format code with Black, isort, and flake8
Fixes common formatting issues automatically
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n{'=' * 60}")
    print(f"🔧 {description}")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if result.stdout:
            print(result.stdout)

        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"⚠️  {description} - Issues found")
            if result.stderr:
                print(result.stderr)
            return False

    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        print(f"Install with: pip install {cmd[0]}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def install_formatters():
    """Install required formatters if not present"""
    print("\n📦 Installing code formatters...")

    packages = ["black", "isort", "flake8"]

    for package in packages:
        try:
            subprocess.run([package, "--version"], capture_output=True, check=True)
            print(f"✓ {package} already installed")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print(f"Installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)


def main():
    """Main formatting execution"""
    print("=" * 60)
    print("🎨 Python Code Formatter")
    print("=" * 60)

    project_root = Path.cwd()
    print(f"\n📁 Project: {project_root}")

    # Install formatters if needed
    install_formatters()

    # 1. Format imports with isort
    isort_success = run_command(
        ["isort", ".", "--profile", "black", "--line-length", "120"],
        "Sorting imports with isort"
    )

    # 2. Format code with black
    black_success = run_command(
        ["black", ".", "--line-length", "120"],
        "Formatting code with black"
    )

    # 3. Check with flake8 (but don't fail)
    flake8_success = run_command(
        ["flake8", ".", "--max-line-length", "120", "--ignore", "E203,W503,E501"],
        "Checking code style with flake8"
    )

    # Summary
    print("\n" + "=" * 60)
    print("📊 Formatting Summary")
    print("=" * 60)

    results = {
        "isort (import sorting)": isort_success,
        "black (code formatting)": black_success,
        "flake8 (style checking)": flake8_success
    }

    for tool, success in results.items():
        status = "✅" if success else "⚠️"
        print(f"{status} {tool}")

    print("\n" + "=" * 60)

    if black_success and isort_success:
        print("✅ Code formatting complete!")
        print("\n💡 Next steps:")
        print("   1. Review changes: git diff")
        print("   2. Stage changes: git add .")
        print("   3. Commit: git commit -m 'style: format code with black and isort'")
        return 0
    else:
        print("⚠️  Some issues remain - review the output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())