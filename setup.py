#!/usr/bin/env python3
"""
shafan Setup Script - One-command environment setup for OCR Project
Run: python setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None, check=True, capture_output=True):
    """Run a command and return the result"""
    try:
        # If capture_output is False, stdout/stderr are inherited (printed to terminal)
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True if capture_output else False,
            check=check
        )

        stdout = ""
        stderr = ""

        if capture_output:
            stdout = result.stdout.strip() if result.stdout else ""
            stderr = result.stderr.strip() if result.stderr else ""

        return result.returncode == 0, stdout, stderr
    except subprocess.CalledProcessError as e:
        return False, "", str(e)

def print_status(message):
    print(f"🔧 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def check_requirements():
    """Check if required tools are available"""
    required_tools = ['python3', 'pip3']
    missing = []

    for tool in required_tools:
        if not shutil.which(tool):
            missing.append(tool)

    if missing:
        print_error(f"Missing required tools: {', '.join(missing)}")
        print("Please install them and try again.")
        return False

    return True

def setup_mise():
    """Setup mise if available"""
    if shutil.which('mise'):
        print_status("Setting up mise (installing tools defined in .mise.toml)...")
        success, _, _ = run_command("mise install", capture_output=False)
        if success:
            print_success("Tools installed via mise")
            return True
        else:
            print_status("Failed to install tools via mise")
    return False

def setup_nodejs():
    """Setup Node.js if available"""
    if shutil.which('mise'):
        print_status("Setting up Node.js...")
        success, _, _ = run_command("mise install node@20", capture_output=False)
        if success:
            print_success("Node.js 20 installed via mise")
            return True
        else:
            print_status("Using system Node.js")
    return False

def create_venv():
    """Create virtual environment"""
    print_status("Creating virtual environment...")

    # Use mise Python if available, otherwise system Python
    python_cmd = "mise exec python -- python"
    if not run_command(f"{python_cmd} --version")[0]:
        python_cmd = "python3"

    success, _, _ = run_command(f"{python_cmd} -m venv .venv")
    if not success:
        print_error("Failed to create virtual environment")
        return False

    print_success("Virtual environment created")
    return True

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print_status("Installing OCR and computer vision dependencies...")

    # Check for uv (globally or via mise)
    uv_executable = "uv"
    use_uv = shutil.which('uv') is not None

    # If uv not found globally, try via mise
    if not use_uv and shutil.which('mise'):
        # Check if mise can run uv
        success, _, _ = run_command("mise exec -- uv --version")
        if success:
            use_uv = True
            uv_executable = "mise exec -- uv"

    if use_uv:
        print_status(f"Using uv for faster installation 🚀 ({uv_executable})")
        # uv pip install requires targeting the venv explicitly or being active
        # using --python .venv targets the specific environment
        base_cmd = f"{uv_executable} pip install --python .venv"
    else:
        pip_cmd = ".venv/bin/pip"
        # Upgrade pip first if using standard pip
        run_command(f"{pip_cmd} install --upgrade pip", capture_output=False)
        base_cmd = f"{pip_cmd} install"

    if os.path.exists("requirements.txt"):
        # Install dependencies from requirements.txt
        success, _, _ = run_command(
            f"{base_cmd} -r requirements.txt",
            capture_output=False
        )
        if success:
            print_success("OCR dependencies installed successfully")
            print("📦 Installed: PaddlePaddle, PaddleOCR, pdf2image, OpenCV, and utilities")
            if not use_uv:
                print("💡 Tip: Install 'uv' for 10-100x faster installations: https://github.com/astral-sh/uv")
            return True
        else:
            print_error("Failed to install dependencies")
            return False
    else:
        print_status("No requirements.txt found, skipping dependency installation")
        return True

def setup_direnv():
    """Setup direnv if available"""
    if shutil.which('direnv'):
        print_status("Setting up direnv...")

        # Create .envrc if it doesn't exist
        if not os.path.exists(".envrc"):
            with open(".envrc", "w") as f:
                f.write("source .venv/bin/activate\n")
            print_status("Created .envrc file")

        success, _, _ = run_command("direnv allow")
        if success:
            print_success("direnv configured - environment will activate automatically")
        else:
            print_status("direnv available but configuration failed")
    else:
        print_status("direnv not found - install it for automatic environment activation")

def create_project_structure():
    """Create basic project structure"""
    print_status("Creating project structure...")

    dirs_to_create = ['scripts', 'src', 'data', 'models', 'output']

    for dir_name in dirs_to_create:
        os.makedirs(dir_name, exist_ok=True)

    # Create a basic __init__.py in src
    init_file = "src/__init__.py"
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write('"""shafan OCR Project"""\n')

    # Create a basic example script
    example_script = """#!/usr/bin/env python3
\"\"\"
shafan OCR Example Script
Basic OCR functionality using PaddleOCR and OpenCV
\"\"\"

import cv2
import numpy as np
from paddleocr import PaddleOCR
import json
import re
from pathlib import Path

def main():
    print("🔍 shafan OCR System Ready")
    print("Available functions:")
    print("- OCR processing with PaddleOCR")
    print("- PDF to image conversion with pdf2image")
    print("- Image processing with OpenCV")
    print("- Text processing with regex and json")

    # Initialize OCR (this will download models on first run)
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        print("✅ PaddleOCR initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize PaddleOCR: {e}")
        return

    print("\\n🎯 Ready to process images and PDFs!")
    print("Create your OCR scripts in the scripts/ directory")

if __name__ == "__main__":
    main()
"""
    with open('scripts/example_ocr.py', 'w') as f:
        f.write(example_script)
    os.chmod('scripts/example_ocr.py', 0o755)

    print_success("Project structure created")

def main():
    """Main setup function"""
    print("🚀 shafan Environment Setup - OCR Project")
    print("=" * 50)

    if not check_requirements():
        return 1

    # Setup components
    setup_mise()
    setup_nodejs()
    create_venv()
    install_dependencies()
    setup_direnv()
    create_project_structure()

    print("\n" + "=" * 50)
    print_success("shafan setup complete!")
    print("\n🎯 How to use shafan:")
    print("1. Environment activates automatically (if direnv installed)")
    print("2. Or manually: source .venv/bin/activate")
    print("3. Run example: python scripts/example_ocr.py")
    print("\n📚 Standard commands (Makefile):")
    print("- make setup        # Run setup again")
    print("- make clean        # Clean environment")
    print("- make example      # Run example script")
    print("\n🔧 Technologies configured:")
    print("- Python 3.12 (OCR backend)")
    print("- Node.js 20 (Next.js frontend)")
    print("- PaddleOCR, OpenCV, pdf2image")

    return 0

if __name__ == "__main__":
    sys.exit(main())
