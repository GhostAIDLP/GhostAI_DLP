#!/bin/bash
# GhostAI Security Firewall - Red Team Status Check Script

echo "🤖 GhostAI Red Team Status Check"
echo "================================="

# Check if daemon is running
REDTEAM_PIDS=$(pgrep -f "run_continuous_learning.py")

if [ -z "$REDTEAM_PIDS" ]; then
    echo "❌ Red team daemon is NOT running"
    echo "   Start with: ./start_redteam_daemon.sh"
    exit 1
fi

echo "✅ Red team daemon is running"
echo "   PIDs: $REDTEAM_PIDS"

# Check process details
for pid in $REDTEAM_PIDS; do
    echo ""
    echo "📊 Process $pid details:"
    ps -p $pid -o pid,ppid,cmd,etime,pcpu,pmem
done

# Check recent activity
echo ""
echo "📈 Recent Activity:"
if [ -f "logs/redteam_daemon.log" ]; then
    echo "   Last 10 log entries:"
    tail -10 logs/redteam_daemon.log | sed 's/^/     /'
else
    echo "   No log file found"
fi

# Check database activity
echo ""
echo "💾 Database Activity:"
if [ -f "data/redteam.db" ]; then
    python3 -c "
import sqlite3
conn = sqlite3.connect('data/redteam.db')
cursor = conn.cursor()

# Get attack count
cursor.execute('SELECT COUNT(*) FROM attack_results')
attack_count = cursor.fetchone()[0]

# Get recent attacks
cursor.execute('SELECT COUNT(*) FROM attack_results WHERE timestamp > datetime(\"now\", \"-1 hour\")')
recent_attacks = cursor.fetchone()[0]

# Get success rate
cursor.execute('SELECT AVG(success) FROM attack_results')
success_rate = cursor.fetchone()[0] or 0

print(f'   Total Attacks: {attack_count:,}')
print(f'   Last Hour: {recent_attacks:,}')
print(f'   Success Rate: {success_rate:.1%}')

conn.close()
"
else
    echo "   No database found"
fi

echo ""
echo "🎯 Status: Red team daemon is active and learning!"
