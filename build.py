import PyInstaller.__main__
import os
import sys
import platform

def build_app():
    main_script = 'main.py'
    if not os.path.exists(main_script):
        print(f"Error: {main_script} not found")
        return False
    is_windows = platform.system() == "Windows"
    separator = ";" if is_windows else ":"
    
    options = [
        main_script,
        '--onefile',
        '--windowed',  
        '--name=RubiksCube',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=.',
        '--hidden-import=pygame',
        '--hidden-import=pygame._sdl2',
        '--hidden-import=OpenGL',
        '--hidden-import=OpenGL.GL',
        '--hidden-import=OpenGL.GLU', 
        '--hidden-import=OpenGL.GLUT',
        '--hidden-import=OpenGL.arrays',
        '--hidden-import=numpy',
        '--collect-all=pygame',
        '--collect-all=OpenGL',
        '--strip',
        '--noupx',  
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
    ]

    if os.path.exists('README.txt'):
        options.append(f'--add-data=README.txt{separator}.')
    if os.path.exists('icon.ico'):
        options.append('--icon=icon.ico')
    elif os.path.exists('icon.icns'):  
        options.append('--icon=icon.icns')
    elif os.path.exists('icon.png'):   
        options.append('--icon=icon.png')
    
    print(f"Building for {platform.system()}...")
    print(f"Options: {' '.join(options)}")
    
    try:
        PyInstaller.__main__.run(options)
        return True
    except Exception as e:
        print(f"Build failed: {e}")
        return False

def check_dependencies():
    import subprocess
    
    required = {
        'pygame': 'pygame',
        'OpenGL': 'PyOpenGL', 
        'OpenGL_accelerate': 'PyOpenGL_accelerate'
    }
    
    missing = []
    
    for import_name, package_name in required.items():
        try:
            __import__(import_name)
            print(f"✓ {import_name} OK")
        except ImportError:
            missing.append(package_name)
            print(f"✗ {import_name} MISSING")
    
    if missing:
        print(f"Auto-installing: {missing}")
        try:
            for package in missing:
                print(f"Installing {package}...")
                if package == 'PyOpenGL_accelerate':
                    try:
                        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    except:
                        print(f"Warning: Could not install {package}, continuing without it")
                        continue
                else:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("Testing imports after installation...")
            for import_name, package_name in required.items():
                try:
                    __import__(import_name)
                    print(f"{import_name} now OK")
                except ImportError:
                    if package_name != 'PyOpenGL_accelerate':
                        print(f"✗ {import_name} still missing")
                        return False
            return True
            
        except Exception as e:
            print(f"Auto install failed: {e}")
            print("Please manually install:")
            print("pip3 install PyOpenGL")
            return False
    
    return True

def clean_build():
    """Xóa build cũ"""
    import shutil
    for folder in ['build', 'dist', '__pycache__']:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"Cleaned {folder}")

if __name__ == "__main__":
    print("=== Building Rubik's Cube Desktop App ===")
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print("\n1. Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("\n2. Testing main.py...")
    try:
        import pygame
        import OpenGL
        print("Imports OK")
    except Exception as e:
        print(f"Import error: {e}")
        sys.exit(1)
    print("\n3. Cleaning old builds...")
    clean_build()
    print("\n4. Building application...")
    if build_app():
        print("\nBuild successful!")
        if platform.system() == "Windows":
            exe_path = "dist/RubiksCube.exe"
        else:
            exe_path = "dist/RubiksCube"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Output: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            print(f"\nTo run: ./{exe_path}")
        else:
            print("Warning: Output file not found")
    else:
        print("\nBuild failed!")
        print("Try running with --console flag to see errors")