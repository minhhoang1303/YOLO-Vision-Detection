#!/usr/bin/env python3
"""
AI Object Detection - Main Launcher
Gán nhãn, Train, và Nhận diện Object Detection
"""

import os
import sys
import subprocess

def print_banner():
    print("=" * 60)
    print("   🔍 AI OBJECT DETECTION PLATFORM")
    print("   Labeling • Training • Recognition")
    print("=" * 60)

def main():
    print_banner()
    
    while True:
        print("\n📋 CHỌN CHỨC NĂNG:")
        print("-" * 40)
        print("1. 🚀 Chạy Web Labeling Tool")
        print("2. 📸 Train Model (YOLO)")
        print("3. 🎯 Inference (Nhận diện)")
        print("4. 📁 Mở thư mục dataset")
        print("5. ❌ Thoát")
        print("-" * 40)
        
        choice = input("Nhập lựa chọn (1-5): ").strip()
        
        if choice == '1':
            print("\n🔄 Khởi động Web Labeling Tool...")
            print("   Mở trình duyệt: http://localhost:5000")
            print("   Stop: Ctrl+C\n")
            try:
                from app import app
                app.run(host='0.0.0.0', port=5000, debug=True)
            except KeyboardInterrupt:
                print("\n✅ Đã dừng Web Server")
            except ImportError as e:
                print(f"\n❌ Lỗi: {e}")
                print("   Cài đặt thư viện: pip install -r requirements.txt")
                
        elif choice == '2':
            print("\n🔄 Chạy Training...")
            script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'train.py')
            if os.path.exists(script_path):
                subprocess.run([sys.executable, script_path])
            else:
                print("❌ Script train.py không tìm thấy!")
                
        elif choice == '3':
            print("\n🔄 Chạy Inference...")
            script_path = os.path.join(os.path.dirname(__file__), 'scripts', 'inference.py')
            if os.path.exists(script_path):
                subprocess.run([sys.executable, script_path])
            else:
                print("❌ Script inference.py không tìm thấy!")
                
        elif choice == '4':
            folder = os.path.join(os.path.dirname(__file__), 'dataset')
            print(f"\n📁 Mở thư mục: {folder}")
            os.startfile(folder) if sys.platform == 'win32' else subprocess.run(['xdg-open', folder])
            
        elif choice == '5':
            print("\n👋 Tạm biệt!")
            break
        else:
            print("\n⚠️ Lựa chọn không hợp lệ!")

if __name__ == '__main__':
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Yêu cầu Python 3.7 trở lên")
        sys.exit(1)
    
    # Check dependencies
    try:
        import flask
        import cv2
        import ultralytics
    except ImportError:
        print("\n⚠️ Cần cài đặt thư viện!")
        print("   Chạy: pip install -r requirements.txt")
        response = input("   Cài đặt ngay? (y/n): ")
        if response.lower() == 'y':
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Đã cài đặt xong!")
        else:
            print("\n⚠️ Vui lòng cài đặt thủ công để tiếp tục")
            
    main()
