#!/usr/bin/env python3
"""
Test Frontend-Backend Communication
Quick test to verify the integration is working
"""

import requests
import json
import webbrowser
import time

def test_backend():
    """Test backend health"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_frontend():
    """Test frontend accessibility"""
    try:
        response = requests.get('http://localhost:3000', timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
            return True
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def test_ai_endpoint():
    """Test AI analysis endpoint"""
    try:
        response = requests.get('http://localhost:8000/v1/analysis/ai/AAPL?provider=mock', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'ai_analysis' in data:
                print("✅ AI endpoint working")
                print(f"   Symbol: {data['ai_analysis']['symbol']}")
                print(f"   Recommendation: {data['ai_analysis']['overall_recommendation']}")
                return True
            else:
                print("❌ AI endpoint returned unexpected format")
                return False
        else:
            print(f"❌ AI endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ AI endpoint error: {e}")
        return False

def main():
    print("🧪 Frontend-Backend Integration Test")
    print("=" * 50)
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    ai_ok = test_ai_endpoint()
    
    print("\n📊 Test Results:")
    print(f"Backend Health: {'✅' if backend_ok else '❌'}")
    print(f"Frontend Access: {'✅' if frontend_ok else '❌'}")
    print(f"AI Endpoint: {'✅' if ai_ok else '❌'}")
    
    if backend_ok and frontend_ok and ai_ok:
        print("\n🎉 All systems working!")
        print("🌐 Opening frontend in browser...")
        time.sleep(2)
        webbrowser.open('http://localhost:3000')
        return True
    else:
        print("\n⚠️ Some issues detected. Check server status.")
        return False

if __name__ == "__main__":
    main()