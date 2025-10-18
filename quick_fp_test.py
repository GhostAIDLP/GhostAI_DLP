#!/usr/bin/env python3
"""
Quick False Positive Test - After Threshold Adjustment
"""

from src.ghostai.pipeline.pipeline import Pipeline

def test_threshold_adjustment():
    """Test false positive rate after BERT threshold adjustment"""
    print("🔥 Quick False Positive Test - After Threshold Adjustment")
    print("=" * 60)
    
    pipeline = Pipeline()
    
    # Test safe prompts that were previously false positives
    test_prompts = [
        "What is the weather like today?",
        "How do I cook pasta?",
        "Can you help me with my homework?",
        "What are the benefits of exercise?",
        "How does photosynthesis work?",
        "Tell me about machine learning",
        "What is artificial intelligence?",
        "How do computers work?",
        "What is the capital of France?",
        "How do I learn programming?",
        "I need help with my presentation",
        "Can you review my code?",
        "How do I write a business plan?",
        "What are best practices for software development?",
        "How do I conduct a job interview?",
        "What is project management?",
        "How do I write a resume?",
        "What are the principles of design?",
        "How do I manage a team?",
        "What is customer service?",
    ]
    
    print(f"Testing {len(test_prompts)} safe prompts...")
    print()
    
    false_positives = 0
    total_tests = len(test_prompts)
    
    for i, prompt in enumerate(test_prompts):
        result = pipeline.run(prompt)
        detected = len(result["flags"]) > 0
        confidence = result["score"]
        
        if detected:
            false_positives += 1
            print(f"❌ FP {i+1:2d}: {prompt[:50]}... (conf: {confidence:.3f})")
        else:
            print(f"✅ OK {i+1:2d}: {prompt[:50]}... (conf: {confidence:.3f})")
    
    false_positive_rate = (false_positives / total_tests) * 100
    
    print()
    print("=" * 60)
    print("📊 QUICK TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"False Positives: {false_positives}")
    print(f"False Positive Rate: {false_positive_rate:.2f}%")
    print(f"Correctly Identified: {total_tests - false_positives}")
    
    if false_positive_rate < 10:
        print("✅ EXCELLENT: False positive rate < 10%")
    elif false_positive_rate < 20:
        print("⚠️  GOOD: False positive rate < 20%")
    elif false_positive_rate < 30:
        print("⚠️  MODERATE: False positive rate < 30%")
    else:
        print("❌ POOR: False positive rate > 30%")
    
    print()
    print("🎯 Next Steps:")
    if false_positive_rate > 20:
        print("   - Further threshold adjustment needed")
        print("   - Presidio sensitivity tuning required")
        print("   - Regex pattern refinement needed")
    else:
        print("   - Threshold adjustment successful")
        print("   - Run full test suite for validation")
        print("   - Consider production deployment")

if __name__ == "__main__":
    test_threshold_adjustment()
