#!/usr/bin/env python3
"""
Build script for creating executable from Order Management System
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def clean_build_directories():
    """Clean previous build artifacts"""
    print("\n🧹 Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed {dir_name}/")
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))
    
    # Clean __pycache__ directories
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                shutil.rmtree(os.path.join(root, dir_name))
    
    print("✅ Cleanup complete!")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found!")
        return False
    
    # Install requirements
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies from requirements.txt"
    )
    
    return success

def build_executable():
    """Build the executable using PyInstaller"""
    print("\n🔨 Building executable...")
    
    # Check if spec file exists
    if not os.path.exists('order_management.spec'):
        print("❌ order_management.spec not found!")
        return False
    
    # Build using spec file
    success = run_command(
        f"{sys.executable} -m PyInstaller order_management.spec",
        "Building executable with PyInstaller"
    )
    
    return success

def verify_build():
    """Verify the build was successful"""
    print("\n🔍 Verifying build...")
    
    exe_path = os.path.join('dist', 'OrderManagementSystem')
    if sys.platform == "win32":
        exe_path += '.exe'
    
    if os.path.exists(exe_path):
        print(f"✅ Executable created successfully: {exe_path}")
        print(f"📁 Location: {os.path.abspath(exe_path)}")
        
        # Get file size
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"📊 Size: {size_mb:.1f} MB")
        
        return True
    else:
        print(f"❌ Executable not found at: {exe_path}")
        return False

def main():
    """Main build process"""
    print("🚀 Starting Order Management System Build Process")
    print("=" * 60)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    steps = [
        ("Cleaning build directories", clean_build_directories),
        ("Installing dependencies", install_dependencies),
        ("Building executable", build_executable),
        ("Verifying build", verify_build),
    ]
    
    for step_name, step_function in steps:
        print(f"\n📋 Step: {step_name}")
        if not step_function():
            print(f"\n❌ Build failed at step: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Build completed successfully!")
    print("\n📝 Next steps:")
    print("1. Test the executable by running it")
    print("2. The executable is located in the 'dist' folder")
    print("3. You can distribute the entire 'dist' folder or just the executable")

if __name__ == "__main__":
    main()
