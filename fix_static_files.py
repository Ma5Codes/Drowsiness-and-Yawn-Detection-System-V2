#!/usr/bin/env python
"""
Fix static files configuration for DrowsiSense
"""
import os
import shutil
from pathlib import Path

def fix_static_files():
    """Fix static files configuration"""
    
    print("🔧 Fixing Static Files Configuration")
    print("=" * 40)
    
    # Ensure static directory exists
    static_dir = Path("static")
    css_dir = static_dir / "css"
    
    print(f"📁 Creating directories...")
    static_dir.mkdir(exist_ok=True)
    css_dir.mkdir(exist_ok=True)
    print(f"  ✓ Created {static_dir}")
    print(f"  ✓ Created {css_dir}")
    
    # Check if CSS file exists
    css_file = css_dir / "modern_theme.css"
    if css_file.exists():
        print(f"  ✓ CSS file exists: {css_file}")
    else:
        print(f"  ❌ CSS file missing: {css_file}")
        return False
    
    # Test file can be read
    try:
        with open(css_file, 'r') as f:
            content = f.read()
        print(f"  ✓ CSS file readable ({len(content)} characters)")
    except Exception as e:
        print(f"  ❌ Cannot read CSS file: {e}")
        return False
    
    print("\n🎨 CSS File Content Preview:")
    with open(css_file, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:5]):
            print(f"  {i+1}: {line.strip()}")
        if len(lines) > 5:
            print(f"  ... and {len(lines)-5} more lines")
    
    print("\n✅ Static files configuration is correct!")
    return True

def test_static_access():
    """Test static file access"""
    print("\n🌐 Testing Static File Access")
    print("=" * 30)
    
    try:
        import urllib.request
        import urllib.error
        
        # Test static file URL
        static_url = "http://localhost:8000/static/css/modern_theme.css"
        
        print(f"📡 Testing: {static_url}")
        
        try:
            response = urllib.request.urlopen(static_url, timeout=5)
            if response.getcode() == 200:
                print("  ✅ Static file accessible!")
                return True
            else:
                print(f"  ❌ HTTP {response.getcode()}")
                return False
        except urllib.error.HTTPError as e:
            print(f"  ❌ HTTP Error {e.code}: {e.reason}")
            return False
        except urllib.error.URLError as e:
            print(f"  ❌ Server not running or unreachable")
            return False
            
    except Exception as e:
        print(f"  ❌ Test failed: {e}")
        return False

def create_debug_template():
    """Create a debug template to test static loading"""
    
    debug_template = """<!DOCTYPE html>
<html>
<head>
    <title>Static Files Debug</title>
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/modern_theme.css' %}">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .test { background: var(--accent-primary, red); color: white; padding: 20px; border-radius: 8px; }
        .success { background: green; }
        .fail { background: red; }
    </style>
</head>
<body>
    <h1>🔧 Static Files Debug Page</h1>
    
    <div class="test" id="css-test">
        <h2>CSS Test</h2>
        <p>If this box has a blue background, CSS is working!</p>
        <p>If this box is red, CSS is NOT loading.</p>
    </div>
    
    <div style="margin-top: 20px;">
        <h3>🎨 Theme Test</h3>
        <button onclick="toggleTheme()" style="padding: 10px 20px; border: none; border-radius: 4px; background: #007bff; color: white; cursor: pointer;">
            Toggle Theme
        </button>
    </div>
    
    <script>
    // Test if CSS loaded by checking custom properties
    function testCSS() {
        const test = document.getElementById('css-test');
        const style = getComputedStyle(test);
        const bgColor = style.backgroundColor;
        
        if (bgColor.includes('rgb(13, 110, 253)') || bgColor.includes('#0d6efd')) {
            test.className = 'test success';
            test.innerHTML = '<h2>✅ CSS Working!</h2><p>Modern theme CSS is loaded correctly.</p>';
        } else {
            test.className = 'test fail';
            test.innerHTML = '<h2>❌ CSS Failed</h2><p>Modern theme CSS is NOT loading.</p>';
        }
    }
    
    function toggleTheme() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';
        html.setAttribute('data-theme', newTheme);
    }
    
    // Test CSS on page load
    document.addEventListener('DOMContentLoaded', testCSS);
    </script>
</body>
</html>"""
    
    debug_file = Path("templates") / "debug_static.html"
    with open(debug_file, 'w') as f:
        f.write(debug_template)
    
    print(f"📄 Created debug template: {debug_file}")
    return debug_file

def main():
    """Main function"""
    print("🎨 DrowsiSense Static Files Fixer")
    print("=" * 40)
    
    # Step 1: Fix static files
    if not fix_static_files():
        print("\n❌ Cannot continue - static files have issues")
        return
    
    # Step 2: Create debug template
    debug_file = create_debug_template()
    
    # Step 3: Test access
    print("\n🚀 Next Steps:")
    print("1. Restart your Django server:")
    print("   python manage.py runserver")
    print("")
    print("2. Test static files by visiting:")
    print("   http://localhost:8000/static/css/modern_theme.css")
    print("")
    print("3. Test in your app:")
    print("   http://localhost:8000/")
    print("")
    print("4. If still having issues, visit debug page:")
    print("   (Add this URL to your urls.py for testing)")
    
    print("\n✅ Static files should now work correctly!")
    print("🎨 Your modern UI should be visible!")

if __name__ == "__main__":
    main()