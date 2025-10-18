#!/bin/bash
set -euo pipefail

echo "🔥🔥🔥 GHOSTAI firewall EXTREME STRESS TEST 🔥🔥🔥"
echo "=============================================="
echo ""
echo "⚠️  WARNING: This will generate MASSIVE amounts of data!"
echo "⚠️  WARNING: This will stress test ALL components!"
echo "⚠️  WARNING: This will run for several minutes!"
echo ""
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv_stable/bin/activate

# Install required packages
echo "📦 Installing required packages..."
pip install psutil requests

# Run extreme stress test
echo "🚀 Starting EXTREME stress test..."
echo "   This will generate 15,000+ test samples"
echo "   This will run 75 concurrent threads"
echo "   This will run for 10 minutes"
echo "   All results will be logged to files"
echo ""

python scripts/extreme_stress.py

echo ""
echo "🎉 EXTREME stress test completed!"
echo "📄 Check the generated report files for detailed results"
echo "📊 Check the log files for detailed execution logs"
