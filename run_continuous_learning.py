#!/usr/bin/env python3
"""
Run Continuous Learning System
Starts the algorithmic red teaming and vector RAG pipeline.
"""

import os
import sys
import argparse
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ghostai.pipeline.pipeline import Pipeline
from ghostai.redteam.continuous_learning import ContinuousLearningSystem

def main():
    parser = argparse.ArgumentParser(description='Run Continuous Learning System')
    parser.add_argument('--duration', type=float, default=1, help='Duration in hours (default: 1)')
    parser.add_argument('--interval', type=int, default=60, help='Learning interval in seconds (default: 60)')
    parser.add_argument('--batch-size', type=int, default=20, help='Attack batch size (default: 20)')
    parser.add_argument('--test', action='store_true', help='Run test mode (6 minutes)')
    
    args = parser.parse_args()
    
    print("🚀 GhostAI Continuous Learning System")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {args.duration} hours")
    print(f"Learning interval: {args.interval} seconds")
    print(f"Attack batch size: {args.batch_size}")
    print("=" * 50)
    
    # Initialize pipeline
    print("🔧 Initializing DLP pipeline...")
    pipeline = Pipeline()
    
    # Initialize learning system
    print("🧠 Initializing continuous learning system...")
    learning_system = ContinuousLearningSystem(
        pipeline=pipeline,
        learning_interval=args.interval,
        attack_batch_size=args.batch_size
    )
    
    # Run learning
    if args.test:
        print("🧪 Running in test mode (6 minutes)...")
        learning_system.start_continuous_learning(duration_hours=0.1)
    else:
        print(f"🔥 Starting continuous learning for {args.duration} hours...")
        learning_system.start_continuous_learning(duration_hours=args.duration)
    
    print(f"\n✅ Continuous learning completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
