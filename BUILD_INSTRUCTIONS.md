# Order Management System - Executable Build Instructions

This guide will help you package your PyQt5-based Order Management System into a standalone executable file.

## 📋 Prerequisites

- Python 3.7 or higher
- All project dependencies installed
- Sufficient disk space (at least 500MB for build process)

## 🚀 Quick Start (Automated Build)

The easiest way to build your executable:

```bash
# Navigate to your project directory
cd /Users/shivamsanjaynikam/Desktop/Siemens

# Run the automated build script
python3 build_executable.py
```

Or use the shell script:
```bash
./build.sh
```

## 📝 Manual Build Process

If you prefer to build manually or troubleshoot issues:

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Clean Previous Builds (Optional)

```bash
# Remove build artifacts
rm -rf build/ dist/ __pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} +
```

### Step 3: Build the Executable

```bash
pyinstaller order_management.spec
```

## 📁 Output

After successful build, you'll find:
- **Executable**: `dist/OrderManagementSystem` (or `OrderManagementSystem.exe` on Windows)
- **Build logs**: Check the console output for any warnings or errors

## 🔧 Configuration Files

### `requirements.txt`
Contains all Python dependencies:
- PyQt5==5.15.10
- pyinstaller==6.3.0

### `order_management.spec`
PyInstaller configuration file that specifies:
- Entry point (`main.py`)
- Data files to include (images, database files)
- Hidden imports (all PyQt5 modules and custom tabs)
- Executable settings (name, console mode, etc.)

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors
**Problem**: "No module named 'PyQt5'"
**Solution**: 
```bash
pip install PyQt5==5.15.10
```

#### 2. Missing Data Files
**Problem**: Images or database files not found in executable
**Solution**: Check the `datas` section in `order_management.spec` and ensure all required files are listed.

#### 3. Large Executable Size
**Problem**: Executable is too large (>200MB)
**Solutions**:
- Use `--exclude-module` to exclude unused modules
- Consider using `--onedir` instead of `--onefile`
- Use UPX compression (already enabled in spec file)

#### 4. Application Crashes on Startup
**Problem**: Executable runs but crashes immediately
**Solutions**:
- Set `console=True` in spec file to see error messages
- Check that all dependencies are properly included
- Verify database file permissions

#### 5. macOS Code Signing Issues
**Problem**: "App can't be opened because it is from an unidentified developer"
**Solution**:
```bash
# Allow the app to run (one-time)
sudo xattr -rd com.apple.quarantine dist/OrderManagementSystem
```

### Debug Mode

To build with console output for debugging:

1. Edit `order_management.spec`
2. Change `console=False` to `console=True`
3. Rebuild the executable
4. Run it to see any error messages

## 📦 Distribution

### Single Executable
The build creates a single executable file that includes:
- All Python dependencies
- PyQt5 libraries
- Your application code
- Required data files

### Distribution Package
For easier distribution, you can:
1. Zip the entire `dist` folder
2. Include a simple README with usage instructions
3. Test the executable on a clean system

## 🎯 Performance Tips

1. **Exclude Unused Modules**: Add unused modules to the `excludes` list in the spec file
2. **Optimize Imports**: Use specific imports instead of wildcard imports
3. **Use UPX**: Already enabled in the spec file for compression
4. **Test on Clean System**: Always test the executable on a system without Python installed

## 🔄 Updating the Executable

When you make changes to your code:
1. Update the source files
2. Run the build process again
3. Test the new executable

## 📞 Support

If you encounter issues:
1. Check the build logs for specific error messages
2. Verify all dependencies are installed
3. Ensure your Python environment is clean
4. Try building with `console=True` to see runtime errors

## 🎉 Success!

Once built successfully, your executable will be ready for distribution and can run on any system without requiring Python to be installed.
