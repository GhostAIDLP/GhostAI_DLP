#!/usr/bin/env python3
"""
Image Red Team Testing Script
Stress tests image detection with comprehensive attack patterns
"""

import sys
import os
sys.path.append('src')

from ghostai.pipeline.pipeline import Pipeline
from ghostai.redteam.redteam_engine import RedTeamEngine
import time
import random

def test_image_red_team():
    """Test image detection with red team attacks."""
    print("🖼️ Image Red Team Testing - Stress Test Image Detection")
    print("=" * 60)
    
    # Initialize pipeline and red team engine
    pipeline = Pipeline(profile='runtime')
    redteam = RedTeamEngine()
    
    print(f"✅ Pipeline loaded with {len(pipeline.scanners)} scanners")
    print(f"✅ Red team engine loaded with {len(redteam.attack_patterns)} patterns")
    
    # Test image-specific patterns
    image_patterns = [p for p in redteam.attack_patterns if 'image' in p.name]
    print(f"🖼️ Image attack patterns: {len(image_patterns)}")
    for pattern in image_patterns:
        print(f"   - {pattern.name}: {pattern.template[:50]}...")
    
    print("\n🧪 Testing Image Attack Generation:")
    
    # Generate and test image attacks
    image_attacks = []
    for i in range(20):  # Generate 20 image attacks
        attack = redteam.generate_attack(target_type='image')
        image_attacks.append(attack)
        print(f"{i+1:2d}. {attack[:80]}...")
    
    print("\n🔥 Testing Image Attacks Against Pipeline:")
    
    # Test each attack
    results = []
    for i, attack in enumerate(image_attacks, 1):
        start_time = time.time()
        result = pipeline.run(attack)
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000
        
        results.append({
            'attack': attack,
            'detected': result['flagged'],
            'score': result['score'],
            'flags': result['flags'],
            'latency_ms': latency
        })
        
        status = "🚫 BLOCKED" if result['flagged'] else "✅ BYPASSED"
        print(f"{i:2d}. {status} | Score: {result['score']:.2f} | Latency: {latency:.1f}ms")
        print(f"    Attack: {attack[:60]}...")
        if result['flags']:
            print(f"    Flags: {', '.join(result['flags'])}")
        print()
    
    # Analyze results
    total_attacks = len(results)
    detected_attacks = sum(1 for r in results if r['detected'])
    bypassed_attacks = total_attacks - detected_attacks
    
    avg_score = sum(r['score'] for r in results) / total_attacks
    avg_latency = sum(r['latency_ms'] for r in results) / total_attacks
    
    print("📊 Image Red Team Results:")
    print(f"   Total Attacks: {total_attacks}")
    print(f"   Detected: {detected_attacks} ({detected_attacks/total_attacks*100:.1f}%)")
    print(f"   Bypassed: {bypassed_attacks} ({bypassed_attacks/total_attacks*100:.1f}%)")
    print(f"   Average Score: {avg_score:.2f}")
    print(f"   Average Latency: {avg_latency:.1f}ms")
    
    # Show bypassed attacks (false negatives)
    bypassed = [r for r in results if not r['detected']]
    if bypassed:
        print(f"\n🚨 FALSE NEGATIVES ({len(bypassed)} attacks bypassed detection):")
        for i, result in enumerate(bypassed[:5], 1):  # Show first 5
            print(f"   {i}. Score: {result['score']:.2f} - {result['attack'][:80]}...")
    
    # Show high-confidence detections (potential false positives)
    high_confidence = [r for r in results if r['detected'] and r['score'] > 0.8]
    if high_confidence:
        print(f"\n⚠️ HIGH CONFIDENCE DETECTIONS ({len(high_confidence)} attacks):")
        for i, result in enumerate(high_confidence[:5], 1):  # Show first 5
            print(f"   {i}. Score: {result['score']:.2f} - {result['attack'][:80]}...")
    
    return results

def test_image_false_positives():
    """Test for false positives in image detection."""
    print("\n🔍 Testing Image Detection False Positives:")
    print("=" * 50)
    
    pipeline = Pipeline(profile='runtime')
    
    # Legitimate image references that should NOT be flagged
    legitimate_cases = [
        "Please analyze this chart: https://example.com/sales-chart.png",
        "Look at this diagram: https://docs.example.com/architecture.jpg",
        "Check this screenshot: https://support.example.com/error.png",
        "Review this logo: https://brand.example.com/logo.svg",
        "Examine this graph: https://analytics.example.com/metrics.gif",
        "Here's a photo from our event: https://media.example.com/event.jpg",
        "This is our product image: https://shop.example.com/product.png",
        "Look at this infographic: https://marketing.example.com/info.webp"
    ]
    
    print("Testing legitimate image references:")
    false_positives = 0
    
    for i, case in enumerate(legitimate_cases, 1):
        result = pipeline.run(case)
        flagged = result['flagged']
        score = result['score']
        
        if flagged:
            false_positives += 1
            status = "❌ FALSE POSITIVE"
        else:
            status = "✅ CORRECT"
        
        print(f"{i:2d}. {status} | Score: {score:.2f} | {case[:60]}...")
    
    fp_rate = (false_positives / len(legitimate_cases)) * 100
    print(f"\n📊 False Positive Analysis:")
    print(f"   Legitimate Cases: {len(legitimate_cases)}")
    print(f"   False Positives: {false_positives}")
    print(f"   False Positive Rate: {fp_rate:.1f}%")
    
    return false_positives

def run_continuous_image_red_team():
    """Run continuous image red teaming for stress testing."""
    print("\n🔥 Continuous Image Red Team Stress Test:")
    print("=" * 50)
    
    pipeline = Pipeline(profile='runtime')
    redteam = RedTeamEngine()
    
    print("Starting continuous image attack generation...")
    print("Press Ctrl+C to stop")
    
    attack_count = 0
    successful_bypasses = 0
    start_time = time.time()
    
    try:
        while True:
            # Generate image attack
            attack = redteam.generate_attack(target_type='image')
            result = pipeline.run(attack)
            
            attack_count += 1
            if not result['flagged']:
                successful_bypasses += 1
            
            # Print progress every 10 attacks
            if attack_count % 10 == 0:
                elapsed = time.time() - start_time
                success_rate = (successful_bypasses / attack_count) * 100
                print(f"Attacks: {attack_count} | Bypasses: {successful_bypasses} ({success_rate:.1f}%) | Time: {elapsed:.1f}s")
            
            # Learn from attacks every 50 attacks
            if attack_count % 50 == 0:
                redteam.learn_from_attacks()
                print(f"🔄 Learned from {attack_count} attacks")
            
            # Small delay to prevent overwhelming
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        elapsed = time.time() - start_time
        success_rate = (successful_bypasses / attack_count) * 100
        
        print(f"\n⏹️ Stopped after {attack_count} attacks")
        print(f"   Successful bypasses: {successful_bypasses} ({success_rate:.1f}%)")
        print(f"   Total time: {elapsed:.1f}s")
        print(f"   Attacks per second: {attack_count/elapsed:.1f}")

if __name__ == "__main__":
    print("🖼️ GhostAI Image Red Team Testing Suite")
    print("=" * 60)
    
    # Test 1: Basic image red team testing
    results = test_image_red_team()
    
    # Test 2: False positive testing
    false_positives = test_image_false_positives()
    
    # Test 3: Continuous stress testing (optional)
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        run_continuous_image_red_team()
    
    print("\n🎯 Image Red Team Testing Complete!")
    print("   - Image attacks are now integrated into red team engine")
    print("   - Image detection is being stress tested")
    print("   - False positives are being ground out")
    print("   - Continuous learning is improving detection")
