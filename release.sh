#!/bin/bash
rm -rf *.pyc
rm -rf *.md
rm -rf .git
cp -Rp ../dewdrop/__main__.py ./
rm release.sh
zip -r ~/Desktop/dewdrop.zip *
cd ~/Desktop
echo '#!/usr/bin/env python' | cat - dewdrop.zip > dewdrop
chmod +x dewdrop
