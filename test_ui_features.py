#!/usr/bin/env python
"""
Test script for new UI features
"""
import os
import sys
import webbrowser
import time

# Add Django project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drowsiness_project.settings')

def test_ui_features():
    """Test all new UI features"""
    
    print("🎨 Testing DrowsiSense Modern UI Features")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test pages to visit
    test_pages = [
        {
            'name': 'Modern Homepage',
            'url': f'{base_url}/',
            'features': [
                '✨ Dark/Light mode toggle (top-right)',
                '🎨 Modern hero section',
                '📊 Feature showcase',
                '💼 Professional design'
            ]
        },
        {
            'name': 'Modern Login',
            'url': f'{base_url}/login/',
            'features': [
                '🔐 Demo credentials button',
                '👁️ Password visibility toggle',
                '🎯 Smooth animations',
                '📱 Responsive design'
            ]
        },
        {
            'name': 'Modern Registration',
            'url': f'{base_url}/register/',
            'features': [
                '💪 Password strength meter',
                '✅ Real-time validation',
                '🎨 Modern form styling',
                '📋 Feature highlights'
            ]
        },
        {
            'name': 'Modern Dashboard',
            'url': f'{base_url}/dashboard/',
            'features': [
                '📊 Statistics cards',
                '🎛️ Modern monitoring panel',
                '🔔 Real-time alerts',
                '⚙️ Settings forms'
            ]
        }
    ]
    
    print("🚀 Opening test pages in your browser...")
    print("\n📋 What to test on each page:")
    
    for i, page in enumerate(test_pages, 1):
        print(f"\n{i}. {page['name']}")
        print(f"   URL: {page['url']}")
        print("   Features to test:")
        for feature in page['features']:
            print(f"   {feature}")
        
        # Open page in browser
        webbrowser.open(page['url'])
        
        if i < len(test_pages):
            input("\n   Press Enter to open next page...")
    
    print("\n" + "=" * 50)
    print("🎯 KEY FEATURES TO TEST:")
    print("\n🌓 Dark/Light Mode Toggle:")
    print("   • Click toggle in header (moon/sun icon)")
    print("   • See instant theme change")
    print("   • Refresh page - theme persists")
    
    print("\n👤 Profile Features:")
    print("   • Click profile avatar in header")
    print("   • See dropdown menu")
    print("   • Notice user initials in avatar")
    
    print("\n📊 Dashboard Features:")
    print("   • Statistics cards with gradients")
    print("   • Monitoring panel animations")
    print("   • Real-time status indicator")
    print("   • Modern form styling")
    
    print("\n🔐 Login Features:")
    print("   • Click 'Demo Login' button")
    print("   • Toggle password visibility")
    print("   • See loading animations")
    
    print("\n📱 Responsive Design:")
    print("   • Resize browser window")
    print("   • Test on mobile device")
    print("   • Check navigation collapse")
    
    print("\n" + "=" * 50)
    print("✅ UI Testing Complete!")
    print("\nYour portfolio project now has:")
    print("• 🎨 Professional modern design")
    print("• 🌓 Dark/light mode switching") 
    print("• 👤 Modern profile header")
    print("• 📱 Mobile-first responsive design")
    print("• ⚡ Smooth animations and transitions")
    print("• 💼 Portfolio-ready appearance")

def check_server_running():
    """Check if Django server is running"""
    import urllib.request
    import urllib.error
    
    try:
        urllib.request.urlopen('http://localhost:8000', timeout=2)
        return True
    except urllib.error.URLError:
        return False

def main():
    """Main function"""
    print("🎨 DrowsiSense UI Feature Tester")
    print("=" * 40)
    
    # Check if server is running
    if not check_server_running():
        print("❌ Django server is not running!")
        print("\n🚀 Please start the server first:")
        print("   python manage.py runserver")
        print("\nThen run this script again.")
        return
    
    print("✅ Django server is running!")
    print("\n🎯 This will open multiple browser tabs to test UI features")
    
    choice = input("\nContinue? (y/N): ").lower().strip()
    if choice in ['y', 'yes']:
        test_ui_features()
    else:
        print("Test cancelled. Run again when ready!")

if __name__ == "__main__":
    main()