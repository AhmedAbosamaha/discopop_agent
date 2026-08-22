#!/usr/bin/env bash
# Build libarcher — the OMPT tool that makes ThreadSanitizer understand OpenMP.
#
# Why this exists
# ---------------
# ThreadSanitizer only reports a race between accesses it cannot order.  Every
# `#pragma omp parallel for` ends in an implicit barrier, which orders one
# region's writes before the next region's reads — but TSan learns that only if
# something tells it.  That something is archer: an OMPT tool that listens to
# the OpenMP runtime's callbacks and calls TSan's AnnotateHappensBefore/After.
#
# Homebrew's libomp formula builds with -DOPENMP_ENABLE_OMPT_TOOLS=OFF, so no
# libarcher ships with it.  Without it, TSan reports a data race between ANY two
# parallel regions touching the same data.  Verified here: a program whose second
# parallel loop reads what the first one wrote is bit-identical over 20 runs at
# 1/2/4/8/16 threads, and TSan calls it a race.
#
# The runtime side needs nothing: Homebrew's libomp already has OMPT support
# compiled in (it looks up `ompt_start_tool` and honours OMP_TOOL_LIBRARIES), so
# only the tool itself has to be built — one source file, no LLVM tree required.
#
# Usage:  discopop_agent/tools/build_archer.sh [install_dir]
# Default install_dir is ~/.local/lib.  The agent finds the result automatically
# (see _find_archer in l4_validator.py); DP_ARCHER_LIB overrides the search.
set -euo pipefail

INSTALL_DIR="${1:-$HOME/.local/lib}"

command -v brew >/dev/null || { echo "error: needs Homebrew's libomp"; exit 1; }
LIBOMP="$(brew --prefix libomp)"
[ -d "$LIBOMP/include" ] || { echo "error: libomp not installed (brew install libomp)"; exit 1; }

# Build archer from the SAME release as the installed runtime: the tool and the
# runtime agree on the OMPT interface version, and a mismatch is silently
# ignored at load time rather than reported.
VERSION="$(basename "$(readlink "$LIBOMP" 2>/dev/null || echo "$LIBOMP")")"
case "$VERSION" in
  [0-9]*) ;;
  *) VERSION="$(ls -1 "$(brew --cellar libomp)" | tail -1)" ;;
esac
TAG="llvmorg-${VERSION}"
echo "libomp ${VERSION} at ${LIBOMP} -> building archer from ${TAG}"

CXX=""
for c in /usr/local/Cellar/llvm@19/*/bin/clang++ /opt/homebrew/Cellar/llvm@19/*/bin/clang++ \
         "$(command -v clang++ || true)"; do
  [ -x "$c" ] && { CXX="$c"; break; }
done
[ -n "$CXX" ] || { echo "error: no clang++ found"; exit 1; }

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
URL="https://raw.githubusercontent.com/llvm/llvm-project/${TAG}/openmp/tools/archer/ompt-tsan.cpp"
curl -sfL -o "$WORK/ompt-tsan.cpp" "$URL" \
  || { echo "error: could not fetch $URL"; exit 1; }

SYSROOT=()
if [ "$(uname)" = "Darwin" ]; then
  SDK="$(xcrun --show-sdk-path 2>/dev/null || echo /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk)"
  [ -d "$SDK" ] && SYSROOT=(-isysroot "$SDK")
fi
# The TSan Annotate* symbols are resolved at run time from the sanitizer runtime
# already loaded into the process under test, so they are undefined here.
"$CXX" -shared -fPIC -O2 -std=c++17 "${SYSROOT[@]}" \
  -I"$LIBOMP/include" "$WORK/ompt-tsan.cpp" \
  -o "$WORK/libarcher.dylib" -Wl,-undefined,dynamic_lookup

mkdir -p "$INSTALL_DIR"
install -m 0755 "$WORK/libarcher.dylib" "$INSTALL_DIR/libarcher.dylib"
echo "installed -> $INSTALL_DIR/libarcher.dylib"
