#!/usr/bin/env python3
"""
Cleanup Old Modal Deployments
Remove any old or unused Modal deployments to avoid confusion.
"""

import subprocess
import sys

def main():
    print("🧹 Cleaning Up Old Modal Deployments")
    print("=" * 50)
    
    # List of old deployment names to remove
    old_deployments = [
        "ghostai-bert-dlp",
        "ghostai-bert-test", 
        "ghostai-bert-hosting"
    ]
    
    print("🔍 Checking for old deployments...")
    
    for deployment in old_deployments:
        print(f"\n📦 Checking {deployment}...")
        try:
            # Try to delete the deployment
            result = subprocess.run([
                "python", "-m", "modal", "app", "delete", deployment
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"   ✅ Deleted {deployment}")
            else:
                print(f"   ℹ️  {deployment} not found or already deleted")
                
        except Exception as e:
            print(f"   ⚠️  Could not check {deployment}: {e}")
    
    print("\n✅ Cleanup complete!")
    print("\n🎯 Current deployments:")
    print("   - ghostai-bert-inference (cost-effective BERT only)")
    
    print("\n💡 To deploy the clean version:")
    print("   python deploy_clean.py")

if __name__ == "__main__":
    main()
