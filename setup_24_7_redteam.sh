#!/bin/bash
# GhostAI Security Firewall - 24/7 Red Team Setup Script

echo "🤖 Setting up GhostAI Red Team for 24/7 Operation"
echo "================================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Don't run this script as root!"
    echo "   Run as regular user, the script will handle permissions"
    exit 1
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x start_redteam_daemon.sh
chmod +x stop_redteam_daemon.sh
chmod +x check_redteam_status.sh

# Create log directory
echo "📁 Creating log directory..."
mkdir -p logs

# Create systemd service (if on Linux)
if command -v systemctl >/dev/null 2>&1; then
    echo "🐧 Setting up systemd service..."
    
    # Copy service file
    sudo cp ghostai-redteam.service /etc/systemd/system/
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable service
    sudo systemctl enable ghostai-redteam.service
    
    echo "✅ Systemd service installed and enabled"
    echo "   Start: sudo systemctl start ghostai-redteam"
    echo "   Stop: sudo systemctl stop ghostai-redteam"
    echo "   Status: sudo systemctl status ghostai-redteam"
    echo "   Logs: journalctl -u ghostai-redteam -f"
else
    echo "🍎 macOS detected - using launchd instead"
    
    # Create launchd plist
    cat > ~/Library/LaunchAgents/com.ghostai.redteam.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ghostai.redteam</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/rjama/GhostAI_DLP/venv_stable/bin/python</string>
        <string>/Users/rjama/GhostAI_DLP/run_continuous_learning.py</string>
        <string>--daemon</string>
        <string>--interval</string>
        <string>10</string>
        <string>--batch-size</string>
        <string>5</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/rjama/GhostAI_DLP</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/rjama/GhostAI_DLP/logs/redteam_daemon.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/rjama/GhostAI_DLP/logs/redteam_daemon.log</string>
</dict>
</plist>
EOF

    # Load the service
    launchctl load ~/Library/LaunchAgents/com.ghostai.redteam.plist
    
    echo "✅ Launchd service installed and loaded"
    echo "   Start: launchctl start com.ghostai.redteam"
    echo "   Stop: launchctl stop com.ghostai.redteam"
    echo "   Status: launchctl list | grep ghostai"
    echo "   Logs: tail -f logs/redteam_daemon.log"
fi

# Create monitoring script
echo "📊 Creating monitoring script..."
cat > monitor_redteam.sh << 'EOF'
#!/bin/bash
# GhostAI Red Team Monitor

echo "🤖 GhostAI Red Team Monitor"
echo "==========================="

# Check if running
if pgrep -f "run_continuous_learning.py" > /dev/null; then
    echo "✅ Red team daemon is running"
    
    # Show process info
    echo ""
    echo "📊 Process Information:"
    ps aux | grep "run_continuous_learning.py" | grep -v grep
    
    # Show recent activity
    echo ""
    echo "📈 Recent Activity:"
    if [ -f "logs/redteam_daemon.log" ]; then
        echo "Last 5 log entries:"
        tail -5 logs/redteam_daemon.log | sed 's/^/  /'
    fi
    
    # Show database stats
    echo ""
    echo "💾 Database Statistics:"
    python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('data/redteam.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM attack_results')
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM attack_results WHERE timestamp > datetime(\"now\", \"-1 hour\")')
    recent = cursor.fetchone()[0]
    print(f'  Total Attacks: {total:,}')
    print(f'  Last Hour: {recent:,}')
    conn.close()
except:
    print('  Database not accessible')
"
else
    echo "❌ Red team daemon is NOT running"
    echo "   Start with: ./start_redteam_daemon.sh"
fi
EOF

chmod +x monitor_redteam.sh

echo ""
echo "🎉 24/7 Red Team Setup Complete!"
echo "================================"
echo ""
echo "📋 Available Commands:"
echo "   ./start_redteam_daemon.sh    - Start daemon manually"
echo "   ./stop_redteam_daemon.sh     - Stop daemon"
echo "   ./check_redteam_status.sh    - Check status"
echo "   ./monitor_redteam.sh         - Monitor activity"
echo ""
echo "🔄 Auto-start:"
if command -v systemctl >/dev/null 2>&1; then
    echo "   sudo systemctl start ghostai-redteam"
else
    echo "   launchctl start com.ghostai.redteam"
fi
echo ""
echo "📊 Monitoring:"
echo "   tail -f logs/redteam_daemon.log"
echo ""
echo "✅ Red team will now run 24/7 automatically!"
