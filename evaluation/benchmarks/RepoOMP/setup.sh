#!/usr/bin/env bash
set -euo pipefail

echo "=== RepoOMP Simplified setup ==="

# ---- system deps ----
echo "[1/3] Installing system dependencies..."
if command -v apt-get &>/dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y -qq clang gcc g++ make python3 python3-pip uuid-dev
elif command -v yum &>/dev/null; then
    sudo yum install -y -q clang gcc gcc-c++ make python3 python3-pip libuuid-devel
elif command -v brew &>/dev/null; then
    brew install clang gcc make python3
else
    echo "WARNING: package manager not detected. Install clang, gcc, make, python3 manually."
fi

# ---- uftrace ----
echo "[2/3] Installing uftrace..."
if ! command -v uftrace &>/dev/null; then
    if [ -d /tmp/uftrace ]; then
        rm -rf /tmp/uftrace
    fi
    git clone --depth=1 https://github.com/namhyung/uftrace.git /tmp/uftrace
    cd /tmp/uftrace
    ./configure
    make -j"$(nproc)"
    sudo make install
    cd -
    rm -rf /tmp/uftrace
    echo "uftrace installed."
else
    echo "uftrace already installed at $(command -v uftrace)."
fi

# ---- Python deps ----
echo "[3/3] Installing Python packages..."
pip3 install --quiet --upgrade pip
pip3 install --quiet openai>=1.0.0

echo ""
echo "=== Setup complete ==="
echo "Set API credentials before running:"
echo "  export REPOOMP_API_KEY='your key'"
echo "  export REPOOMP_API_BASE='https://your-api-endpoint/v1'"
echo "  export REPOOMP_MODEL='your-model'"