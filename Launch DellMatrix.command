#!/bin/bash
cd "$(dirname "$0")"
echo ""
echo " DellMatrix — ready for anyone"
echo " Offline. Type help for examples, or:"
echo " create an idea called test"
echo ""
python3 -m form.repl --owner Operator
if [ $? -ne 0 ]; then
  echo ""
  echo " Python could not start. Install Python 3 and see docs/INSTALL.md"
fi
echo ""
read -p "Press Enter to close..."
