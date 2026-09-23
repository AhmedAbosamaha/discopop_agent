#!/bin/bash
set -x
cd ~/discopop_agent
export PATH=/usr/lib/llvm-20/bin:$PATH
export CC=/usr/lib/llvm-20/bin/clang
export CXX=/usr/lib/llvm-20/bin/clang++
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install . ./profiler ./library
echo "BUILD_EXIT=$?"
which discopop_cxx discopop_explorer
