#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")"

echo "Paste the full clone X cookie string below."
echo "After pasting, press Enter."

read -r cookie

if [ -z "$cookie" ]; then
    echo "No cookie entered. Nothing was saved."
    exit 1
fi

printf '%s' "$cookie" > x_cookies_clone.txt
chmod 600 x_cookies_clone.txt

echo "Cookie saved to x_cookies_clone.txt"
