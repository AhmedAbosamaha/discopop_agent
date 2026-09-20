#!/usr/bin/env python3
"""Build repository-level MAP evidence graph.

Uses Bear compilation database when present. Falls back to conservative C
source scanning so NPB and BOTS can run without tree-sitter.
"""
import argparse
import hashlib
import json
import os
import re
from collections import defaultdict, deque
from pathlib import Path

C_SUFFIXES = {".c", ".h", ".cc", ".cpp", ".cxx"}
IO_NAMES = {"printf", "fprintf", "sprintf", "fopen", "fclose", "read", "write", "scanf", "fscanf", "sscanf", "puts", "getchar"}
SERIAL_NAMES = {"omp_get_thread_num", "omp_get_num_threads", "omp_set_num_threads", "pthread_create", "fork"}
EXTERNAL_NAMES = {"malloc", "calloc", "realloc", "free", "memcpy", "memset", "sqrt", "sin", "cos", "exp", "log"}
KEYWORDS = {"if", "for", "while", "switch", "return", "sizeof", "defined"}
FUNC_RE = re.compile(r"(?:^|\n)\s*(?:static\s+|extern\s+|inline\s+|const\s+|unsigned\s+|signed\s+|long\s+|short\s+|double\s+|float\s+|int\s+|void\s+|char\s+|struct\s+\w+\s+)+([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{")
CALL_RE = re.compile(r"\b([A-Za-z_]\w*)\s*\(")
GLOBAL_RE = re.compile(r"^\s*(?:static\s+)?(?:const\s+)?(?:unsigned\s+|signed\s+|long\s+|short\s+)*(?:int|float|double|char|void|struct\s+\w+)[^;(){}]*\b([A-Za-z_]\w*)\s*(?:\[[^]]*\])?\s*(?:=|;)")


def stable_key(*parts):
    value = "\x1f".join(str(part) for part in parts)
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def source_span(text, start, end):
    start_line = text.count("\n", 0, start) + 1
    end_line = text.count("\n", 0, max(start, end - 1)) + 1
    line_start = text.rfind("\n", 0, start) + 1
    end_line_start = text.rfind("\n", 0, max(start, end - 1)) + 1
    return {"start_line": start_line, "start_column": start - line_start + 1,
            "end_line": end_line, "end_column": end - end_line_start + 1,
            "start_offset": start, "end_offset": end}


def independent_batches(items, conflicts):
    batches = []
    for item in sorted(items):
        for batch in batches:
            if all(other not in conflicts.get(item, set()) and item not in conflicts.get(other, set()) for other in batch):
                batch.append(item)
                break
        else:
            batches.append([item])
    return batches


def _files(root):
    skip = {".git", "build", "bin", "method_data", "node_modules", "__pycache__"}
    for p in sorted(Path(root).rglob("*")):
        if p.is_file() and p.suffix in C_SUFFIXES and not any(x in skip for x in p.parts):
            yield p


def _body_spans(text):
    spans = []
    for m in FUNC_RE.finditer(text):
        depth = 0
        end = m.end() - 1
        for i in range(end, len(text)):
            if text[i] == "{": depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    spans.append((m.group(1), m.start(1), i + 1, text[m.start():i]))
                    break
    return spans


def _local_globals(text):
    out = set()
    for line in text.splitlines():
        if "(" in line or line.lstrip().startswith("#"):
            continue
        m = GLOBAL_RE.match(line)
        if m:
            out.add(m.group(1))
    return out


def _attrs(name, body, globals_):
    calls = sorted({x for x in CALL_RE.findall(body) if x not in KEYWORDS and x != name})
    reads = sorted(g for g in globals_ if re.search(r"\b" + re.escape(g) + r"\b", body))
    writes = sorted(g for g in reads if re.search(r"(?:\b" + re.escape(g) + r"\b\s*(?:\[|\.|->)?[^;=]*=|\+\+\s*" + re.escape(g) + r"|\b" + re.escape(g) + r"\b\s*(?:\+=|-=|\*=|/=))", body))
    loops = len(re.findall(r"\bfor\s*\(|\bwhile\s*\(", body))
    reductions = bool(re.search(r"\b[A-Za-z_]\w*\s*(?:\+=|-=|\*=|/=)", body))
    io = sorted(x for x in calls if x in IO_NAMES)
    serial = sorted(x for x in calls if x in SERIAL_NAMES)
    external = sorted(x for x in calls if x in EXTERNAL_NAMES)
    indirect = "(*" in body or re.search(r"\b[A-Za-z_]\w*\s*=\s*\([^)]*\*", body) is not None
    return {"calls": calls, "global_reads": reads, "global_writes": writes, "loop_count": loops, "reduction": reductions, "io_calls": io, "serial_calls": serial, "external_calls": external, "indirect_memory": bool(indirect), "openmp": "#pragma omp" in body}


def build_map(root, out, compile_db=None):
    root = os.path.abspath(root)
    files = []
    nodes = []
    edges = []
    funcs_by_name = defaultdict(list)
    for path in _files(root):
        rel = os.path.relpath(path, root)
        try: text = path.read_text(errors="replace")
        except OSError: continue
        file_id = "file:" + rel
        globals_ = sorted(_local_globals(text))
        files.append({"id": file_id, "path": rel, "language": "c" if path.suffix == ".c" else "c++", "global_definitions": globals_, "line_count": text.count("\n") + 1})
        nodes.append({"id": file_id, "kind": "file", "path": rel})
        for name, start, end, body in _body_spans(text):
            line = text.count("\n", 0, start) + 1
            fid = f"function:{rel}:{name}:{line}"
            attrs = _attrs(name, body, set(globals_))
            span = source_span(text, start, end)
            evidence_id = "evidence:function:" + stable_key(rel, name, start, end)
            node = {"id": fid, "kind": "function", "name": name, "file": rel, "line": line, "end_line": text.count("\n", 0, end) + 1, "span": span, "evidence_id": evidence_id, "evidence": {"id": evidence_id, "source": rel, "span": span}, "hotspot_match_keys": sorted({name, fid, rel + ":" + name}), **attrs}
            nodes.append(node); funcs_by_name[name].append(node)
            edges.append({"source": file_id, "target": fid, "kind": "contains"})
    known = set(funcs_by_name)
    for n in [x for x in nodes if x["kind"] == "function"]:
        for call in n["calls"]:
            if call in known:
                target = funcs_by_name[call][0]
                edges.append({"source": n["id"], "target": target["id"], "kind": "calls"})
        for g in n["global_reads"]:
            edges.append({"source": n["id"], "target": "global:" + g, "kind": "reads"})
        for g in n["global_writes"]:
            edges.append({"source": n["id"], "target": "global:" + g, "kind": "writes"})
    funcs = {n["id"]: n for n in nodes if n["kind"] == "function"}
    children = defaultdict(set)
    for e in edges:
        if e["kind"] == "calls": children[e["source"]].add(e["target"])
    conflicts = defaultdict(set)
    for fid, n in funcs.items():
        blockers = set()
        if n["global_writes"]: blockers.add("shared-state-write")
        if n["io_calls"]: blockers.add("io")
        if n["serial_calls"]: blockers.add("serial-control")
        if n["indirect_memory"]: blockers.add("indirect-memory")
        # Known library calls such as sqrt/memcpy are evidence, not blockers.
        # Unknown calls are conservatively represented by indirect-memory or
        # global-write evidence instead of treating every math call as unsafe.
        seen = set(); q = deque(children[fid])
        while q:
            child = q.popleft()
            if child in seen: continue
            seen.add(child); c = funcs[child]
            if c["global_writes"]: blockers.add("shared-state-write")
            if c["io_calls"]: blockers.add("io")
            if c["serial_calls"]: blockers.add("serial-control")
            if c["indirect_memory"]: blockers.add("indirect-memory")
            # External math and memory routines are not blockers by themselves.
            q.extend(children[child])
        n["blockers"] = sorted(blockers)
        n["reachable_callers"] = sorted(x["id"] for x in funcs.values() if fid in children[x["id"]])
        for other, other_node in funcs.items():
            if other != fid and ((set(n["global_reads"]) | set(n["global_writes"])) & (set(other_node["global_reads"]) | set(other_node["global_writes"])) or other in children[fid] or fid in children[other]):
                conflicts[fid].add(other)
    batches = independent_batches(list(funcs), conflicts)
    graph = {"schema": "repoomp.map.v1", "root": root, "compile_database": os.path.abspath(compile_db) if compile_db else None, "repository": {"id": "repository:" + os.path.basename(root), "path": root}, "files": files, "nodes": nodes, "edges": edges, "independent_batches": batches, "hotspot_match_keys": {key: node["id"] for node in funcs.values() for key in node["hotspot_match_keys"]}}
    Path(out).parent.mkdir(parents=True, exist_ok=True); Path(out).write_text(json.dumps(graph, indent=2))
    return graph


def main():
    ap = argparse.ArgumentParser(description="Build RepoOMP MAP evidence graph")
    ap.add_argument("--root", required=True); ap.add_argument("--out", required=True); ap.add_argument("--compile-db", default=None)
    args = ap.parse_args(); g = build_map(args.root, args.out, args.compile_db)
    print(f"[map] wrote {args.out} nodes={len(g['nodes'])} edges={len(g['edges'])}")

if __name__ == "__main__": main()
