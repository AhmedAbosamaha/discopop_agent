#!/bin/bash
# This file is part of the DiscoPoP software (http://www.discopop.tu-darmstadt.de)
#
# Copyright (c) 2020, Technische Universitaet Darmstadt, Germany
#
# This software may be modified and distributed under the terms of
# the 3-Clause BSD License.  See the LICENSE file in the package base
# directory for details.

# This script is based on a script from the discopop project
# https://github.com/discopop-project/discopop

# `readlink -fm` is a GNU extension; BSD readlink (macOS) rejects -m, which left
# SCRIPT_PATH empty and made the plugin path "/LLVMHotspotDetection.so".  Resolve
# the symlink chain by hand instead, which works on both.
SCRIPT_PATH="$0"
while [ -L "$SCRIPT_PATH" ]; do
    _target="$(readlink "$SCRIPT_PATH")"
    case "$_target" in
        /*) SCRIPT_PATH="$_target" ;;
        *)  SCRIPT_PATH="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)/$_target" ;;
    esac
done
LIBS_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"

LLVM_CLANG=""
LLVM_CLANGPP=""
for _v in 22 21 20 19; do
    if command -v clang-$_v &> /dev/null; then
        LLVM_CLANG=$(which clang-$_v)
        LLVM_CLANGPP=$(which clang++-$_v)
        break
    fi
done
if [ -z "$LLVM_CLANGPP" ]; then
    echo "ERROR: No supported clang version (19-22) found in PATH"
    exit 1
fi

# pthread is bundled into libSystem on macOS; only link explicitly on Linux
PTHREAD_XLINKER_FLAGS=()
[[ "$(uname)" != "Darwin" ]] && PTHREAD_XLINKER_FLAGS=(-Xlinker -lpthread)

# macOS: a Homebrew clang has no built-in SDK path, and LLVM's own libc++ has to
# be named explicitly or the link fails with "library 'c++' not found" — the same
# two fixes DiscoPoP's own CXX_wrapper.sh needs here.
SYSROOT_FLAGS=()
LIBCXX_FLAGS=()
if [[ "$(uname)" == "Darwin" ]]; then
    _sdk="$(xcrun --show-sdk-path 2>/dev/null)"
    [ -n "$_sdk" ] && [ -d "$_sdk" ] && SYSROOT_FLAGS=(-isysroot "$_sdk")
    _clang_real="$LLVM_CLANGPP"
    while [ -L "$_clang_real" ]; do
        _t="$(readlink "$_clang_real")"
        case "$_t" in
            /*) _clang_real="$_t" ;;
            *)  _clang_real="$(cd "$(dirname "$_clang_real")" && pwd)/$_t" ;;
        esac
    done
    _llvm_libcxx="$(cd "$(dirname "$_clang_real")/../lib" 2>/dev/null && pwd)"
    if [ -n "$_llvm_libcxx" ] && [ -f "$_llvm_libcxx/libc++.dylib" ]; then
        LIBCXX_FLAGS=(-nostdlib++ "$_llvm_libcxx/libc++.dylib" \
                      "$_llvm_libcxx/libc++abi.dylib" -Wl,-rpath,"$_llvm_libcxx")
    fi
fi

# The CMake build names the pass plugin .dylib on macOS and .so elsewhere, but
# this script only ever asked for .so — so on macOS it loaded nothing.
PLUGIN="${LIBS_DIR}/LLVMHotspotDetection.so"
[ -f "$PLUGIN" ] || PLUGIN="${LIBS_DIR}/LLVMHotspotDetection.dylib"

${LLVM_CLANGPP} "$@" "${SYSROOT_FLAGS[@]}" "${LIBCXX_FLAGS[@]}" -g -fno-discard-value-names -O0 -Xclang -load -Xclang "${PLUGIN}" -Xclang -fpass-plugin="${PLUGIN}" -Xlinker -L${LIBS_DIR} -Xlinker -lHotspotDetection_RT "${PTHREAD_XLINKER_FLAGS[@]}" -Xlinker -v
