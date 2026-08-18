#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")"

if [ -f server.pid ]; then
    PID=$(cat server.pid)

    if kill -0 "$PID" 2>/dev/null; then
        kill -TERM -- "-$PID" 2>/dev/null || kill "$PID"
        echo "Stopping news server (PID $PID)..."
    else
        echo "Server was not running."
    fi

    rm -f server.pid
else
    echo "server.pid not found."
fi
