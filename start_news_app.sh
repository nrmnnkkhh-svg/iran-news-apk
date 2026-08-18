#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")"

if [ "$1" = "--daemon" ]; then
    INTERVAL=180

    termux-wake-lock 2>/dev/null

    cleanup() {
        termux-wake-unlock 2>/dev/null
    }
    trap cleanup EXIT

    (
        while true; do
            python fetch_news.py >> fetch.log 2>&1
            sleep "$INTERVAL"
        done
    ) &

    while true; do
        python app.py >> server.log 2>&1
        echo "app.py exited with code $? - restarting in 3 seconds" >> server.log
        sleep 3
    done
fi

if [ -f server.pid ] && kill -0 "$(cat server.pid)" 2>/dev/null; then
    echo "Already running (PID $(cat server.pid))."
    echo "Stop it first with: ./stop_news_app.sh"
    exit 1
fi

nohup setsid "$0" --daemon > server.log 2>&1 &
echo $! > server.pid

echo "News server started in background (PID $(cat server.pid))."
echo "Stop anytime with: ./stop_news_app.sh"
