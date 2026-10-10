cd ~/discopop_agent/evaluation/agent/runs || exit 1
for run in t0_11_c3_b19r_a t0_11_c4_a t0_11_b19r_apps_a; do
  n=0; with=0
  for f in $(find $run -path "*/.discopop/profiler/reduction.txt" 2>/dev/null | sort); do
    n=$((n+1))
    pkg=$(echo "$f" | sed -E "s#^$run/##; s#/\.discopop/profiler/reduction.txt##")
    ops=$(awk '{print $NF}' "$f" | sort | uniq -c | awk '{printf "%s×%s ", $2, $1}')
    [ -n "$ops" ] && with=$((with+1))
    echo "$run | $pkg | entries $(wc -l < "$f") | ${ops:-none}"
  done
  echo "== $run: $n reduction files, $with with entries"
done
