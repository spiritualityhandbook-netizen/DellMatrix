#!/bin/bash
cd "$(dirname "$0")"
echo ""
echo " Starting DellMatrix..."
echo " Just talk normally. Type help if you need examples."
echo ""
python3 -m form.repl --owner Ace
echo ""
read -p "Press Enter to close..."
