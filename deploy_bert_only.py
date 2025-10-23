#!/usr/bin/env python3
"""
Deploy BERT Model Only (Cost-Effective)
Deploy just the BERT model for inference without red teaming.
"""

import subprocess
import sys
import os

def main():
    print("🚀 Deploying GhostAI BERT (Inference Only)")
    print("=" * 50)
    print("💰 Cost-effective hosting - No red teaming!")
    print("=" * 50)
    
    # Check if Modal is installed
    try:
        import modal
        print("✅ Modal is installed")
    except ImportError:
        print("❌ Modal not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "modal"])
        print("✅ Modal installed")
    
    # Check if user is authenticated
    print("\n🔐 Checking Modal authentication...")
    try:
        result = subprocess.run(["modal", "token", "list"], capture_output=True, text=True)
        if "No tokens found" in result.stdout:
            print("❌ No Modal token found. Please run: modal token new")
            print("   Then run this script again.")
            return
        else:
            print("✅ Modal token found")
    except Exception as e:
        print(f"❌ Error checking token: {e}")
        return
    
    # Deploy the app
    print("\n📦 Deploying BERT model...")
    try:
        result = subprocess.run([sys.executable, "modal_bert_only.py"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Deployment successful!")
            print("\n🔗 Your BERT model is now hosted on Modal")
            print("   https://modal.com/apps/ghostai-bert-inference")
            
            print("\n🧪 Testing the deployed model...")
            subprocess.run([sys.executable, "use_hosted_bert.py"])
            
        else:
            print("❌ Deployment failed:")
            print(result.stderr)
    except Exception as e:
        print(f"❌ Error during deployment: {e}")

if __name__ == "__main__":
    main()
