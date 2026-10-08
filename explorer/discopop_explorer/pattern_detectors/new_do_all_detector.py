# This file is part of the DiscoPoP software (http://www.discopop.tu-darmstadt.de)
#
# Copyright (c) 2020, Technische Universitaet Darmstadt, Germany
#
# This software may be modified and distributed under the terms of
# the 3-Clause BSD License.  See the LICENSE file in the package base
# directory for details.
import json
import logging
import os
import threading
from typing import Any, Dict, List, Optional, Set, Tuple, cast

from tqdm import tqdm  # type: ignore


from discopop_explorer.aliases.LineID import LineID
from discopop_explorer.aliases.NodeID import NodeID
from discopop_explorer.classes.PEGraph.CUNode import CUNode
from discopop_explorer.classes.PEGraph.LoopNode import LoopNode
from discopop_explorer.classes.PEGraph.Node import Node
from discopop_explorer.classes.PEGraph.Dependency import Dependency
from discopop_explorer.classes.PEGraph.PEGraphX import PEGraphX
from discopop_explorer.classes.TaskGraph.ContextTaskGraph import ContextTaskGraph
from discopop_explorer.classes.TaskGraph.Contexts.BranchingParentContext import BranchingParentContext
from discopop_explorer.classes.TaskGraph.Contexts.Context import Context
from discopop_explorer.classes.TaskGraph.Contexts.FunctionContext import FunctionContext
from discopop_explorer.classes.TaskGraph.Contexts.InlinedFunctionContext import InlinedFunctionContext
from discopop_explorer.classes.TaskGraph.Contexts.IterationContext import IterationContext
from discopop_explorer.classes.TaskGraph.Contexts.LoopParentContext import LoopParentContext
from discopop_explorer.classes.TaskGraph.Contexts.TaskParentContext import TaskParentContext
from discopop_explorer.classes.TaskGraph.Contexts.WorkContext import WorkContext
from discopop_explorer.classes.TaskGraph.Loops.TGStartLoopNode import TGStartLoopNode
from discopop_explorer.classes.TaskGraph.TGNode import TGNode
from discopop_explorer.classes.TaskGraph.TaskGraph import TaskGraph
from discopop_explorer.classes.patterns.PatternInfo import PatternInfo
from discopop_explorer.enums.DepType import DepType
from discopop_explorer.enums.EdgeType import EdgeType
from discopop_explorer.pattern_detectors.do_all_detector import DoAllInfo
from discopop_explorer.pattern_detectors.task_parallelism.classes import (
    ParallelRegionInfo,
    TPIType,
    TaskParallelismInfo,
)
from discopop_gui.Visualizers.WithSidebar import WithSidebar as VisualizerWithSideBar

from discopop_explorer.utils import classify_loop_variables
from discopop_explorer.functions.PEGraph.queries.edges import in_edges, out_edges
from discopop_explorer.functions.PEGraph.queries.subtree import subtree_of_type
from discopop_explorer.classes.variable import Variable
from discopop_explorer.pattern_detectors.combined_gpu_patterns.classes.Aliases import MemoryRegion, VarName
from discopop_explorer.enums.DepOrigin import DepOrigin
from discopop_explorer.pattern_detectors.reduction_detector import ReductionInfo
from discopop_explorer.utilities.ASTUtils.ASTPatternDetectionIntegration import ASTPatternDetectionHelper

logger = logging.getLogger("Explorer").getChild("DoAll")


def run_detection(
    pet: PEGraphX, task_graph: TaskGraph, ast_helper: ASTPatternDetectionHelper
) -> List[DoAllInfo | ReductionInfo]:
    logger.info("Starting new do_all and reduction detection...")
    result: List[DoAllInfo | ReductionInfo] = []

    result += identify_simple_doall_and_reduction(task_graph, ast_helper)

    show_plot(task_graph)

    return result


def show_plot(tg: TaskGraph) -> None:
    if tg.plottable() == False:
        return

    def draw_plots() -> None:
        ax = tg.create_plot("Context Graph")
        print("Plotting task graph (context graph)...")
        if len(tg.graph.nodes()) < 500:
            tg.plot_context_graph(ax)

        ax2 = tg.create_plot("Context Debug Graph")
        print("Plotting task graph (context debug graph)...")
        if len(tg.graph.nodes()) < 500:
            tg.plot_context_debug_graph(ax2)

        ax3 = tg.create_plot("Task Graph")
        print("Plotting task graph...")
        if len(tg.graph.nodes()) < 500:
            tg.update_plot(ax3)

    def on_filter(filter_text: str) -> None:
        print("Filter text:", filter_text)

        # Extra processing here

    for frame_name in ["Context Graph", "Context Debug Graph", "Task Graph"]:
        try:
            tg.delete_frame(frame_name)
        except KeyError:
            pass

    tg.set_filter_callback(on_filter)
    draw_plots()
    tg.run_visualizer()


def _declared_inside_loop(tg: TaskGraph, loop_node: TGNode, var_name: str) -> bool:
    """B13: is `var_name` declared inside the loop's body (by DiscoPoP's CU variables: a local whose
    declaration line lies within the loop's code)? Such an array is private to each iteration by its scope, so a
    write-after-write the profile saw between iterations — the same stack address reused — is no conflict. A
    variable whose declaration line DiscoPoP did not record ("LineNotFound", as the profiler writes for arrays)
    counts as declared outside: the loop is blocked (conservative)."""
    loop_ctx = loop_node.created_context
    if loop_node.pet_node_id is None or loop_ctx is None:
        return False
    scope_lines: Set[Tuple[int, int]] = set()
    for lid in loop_ctx.get_code_scope(tg.pet):
        fid, _, ln = str(lid).partition(":")
        if fid.isdigit() and ln.isdigit():
            scope_lines.add((int(fid), int(ln)))
    for ctx in loop_ctx.get_contained_contexts(inclusive=True):
        for tg_node in ctx.contained_nodes:
            if tg_node.pet_node_id is None:
                continue
            for v in getattr(tg.pet.node_at(tg_node.pet_node_id), "local_vars", []) or []:
                if str(v.name) != var_name:
                    continue
                fid, _, line = str(v.defLine).partition(":")
                if fid.isdigit() and line.isdigit() and (int(fid), int(line)) in scope_lines:
                    return True
    return False


def _written_in_every_pass(pet: PEGraphX, own_cu_ids: Set[NodeID], writers: Set[NodeID]) -> bool:
    """B19: does EVERY pass through the loop's body run one of `writers` — units of the loop that write a
    variable? OpenMP's `lastprivate` hands back the value of the sequentially last iteration; it is the
    variable's value after the loop only if that iteration assigns it. The modelled iterations cannot tell an
    assignment under a condition from one every pass makes (each holds all units of the body); the control flow
    can: with the writing units taken out, a pass must not be able to get from the unit it starts at back to
    that unit. The unit a pass starts at is the one unit of the loop that is entered from outside it. A loop
    entered at several units, and a variable written only by what the loop calls, are not shown to assign in
    every pass: the answer is no."""
    writers = writers & own_cu_ids
    if not writers:
        return False
    entries = [
        cu_id
        for cu_id in own_cu_ids
        if any(src not in own_cu_ids for src, _, _ in in_edges(pet, cu_id, EdgeType.SUCCESSOR))
    ]
    if len(entries) != 1:
        return False
    entry = entries[0]
    if entry in writers:
        return True
    seen: Set[NodeID] = set()
    stack: List[NodeID] = [entry]
    while stack:
        current = stack.pop()
        for _, successor, _ in out_edges(pet, current, EdgeType.SUCCESSOR):
            if successor == entry:
                return False  # back at the start of a pass without having met a write
            if successor not in own_cu_ids or successor in writers or successor in seen:
                continue
            seen.add(successor)
            stack.append(successor)
    return True


def _seen_to_overwrite_itself(pet: PEGraphX, own_cu_ids: Set[NodeID], writers: Set[NodeID], var_name: str) -> bool:
    """B19: does the profile hold a write-after-write of `var_name` from a writing unit of the loop onto the SAME
    line — the assignment overwriting what an earlier pass of it had written? Then at least two passes were
    observed to assign the variable. (The static dependences only run forward: an assignment that overwrites its
    own line's write is a record of the run.)"""
    writers = writers & own_cu_ids
    for cu_id in writers:
        for _, target, dep in out_edges(pet, cu_id, EdgeType.DATA):
            if (
                dep.dtype == DepType.WAW
                and dep.var_name == var_name
                and target in writers
                and dep.source_line is not None
                and dep.source_line == dep.sink_line
            ):
                return True
    return False


def _names_written_by(pet: PEGraphX, cu_node_id: NodeID) -> Set[str]:
    """B19: the variables the unit `cu_node_id` writes, read off its data edges as the classification in
    `detect_doall_sharing_clauses` reads them (an outgoing WAR, WAW or INIT: the unit overwrites or initialises;
    an incoming RAW, WAW or INIT: something uses or overwrites what the unit wrote). The names are those the
    dependences carry: a store through a parameter is named after the variable whose value is read later."""
    names: Set[str] = set()
    for _src, _dst, dep in out_edges(pet, cu_node_id, EdgeType.DATA):
        if dep.var_name is not None and dep.dtype in (DepType.WAR, DepType.WAW, DepType.INIT):
            names.add(dep.var_name)
    for _src, _dst, dep in in_edges(pet, cu_node_id, EdgeType.DATA):
        if dep.var_name is not None and dep.dtype in (DepType.RAW, DepType.WAW, DepType.INIT):
            names.add(dep.var_name)
    return names


def identify_simple_doall_and_reduction(
    tg: TaskGraph, ast_helper: ASTPatternDetectionHelper
) -> List[DoAllInfo | ReductionInfo]:
    """Analyzes the results of the graph simplification and create simple doall patterns.
    Implementation is fundamentally similar to the original doall detector, but implemented in a more maintainable fashion.
    Checks for clean doall opportunities."""
    patterns: List[DoAllInfo | ReductionInfo] = []
    logger.info("Identifying trivial doall suggestions.")

    show_plot(tg)

    prevented_loops: Set[NodeID] = set()

    # discopop_agent integration: record WHY each loop is not Do-All (the specific
    # blocking dependency), persisted to explorer/doall_prevented.json so the agent
    # can tell the LLM exactly which dependency to break.  Purely additive.
    prevented_records: List[Dict[str, Any]] = []

    def _blocker_record(loop_node: TGNode, dep: Dependency) -> Dict[str, Any]:
        loop_ctx = loop_node.created_context
        scope = loop_ctx.get_code_scope(tg.pet) if loop_ctx is not None else []  # List[LineID] "fid:line"
        loop_file: Optional[int] = None
        loop_lines: List[int] = []
        for lid in scope:
            try:
                f, ln = str(lid).split(":")
                loop_file = int(f)
                loop_lines.append(int(ln))
            except (ValueError, AttributeError):
                pass
        return {
            "loop_file": loop_file,
            "loop_start": min(loop_lines) if loop_lines else None,
            "loop_end": max(loop_lines) if loop_lines else None,
            "dep_type": str(dep.dtype),
            "source_line": str(dep.source_line),
            "sink_line": str(dep.sink_line),
            "var_name": str(dep.var_name),
            "memory_region": str(dep.memory_region),
            "origin": str(dep.origin),
        }

    def _last_value_record(
        loop_node: TGNode, var_name: str, write_line: Optional[LineID], read_line: Optional[LineID], observed: bool
    ) -> Dict[str, Any]:
        """B19: the record of a loop that is not Do-All because a variable read after it is assigned in only
        some of its passes. What stands against running the passes in any order is the write-after-write
        between them — the write that comes last in the original order must be the one that is read — so the
        record is that dependence, on the line of the assignment. Its origin says whether the profile holds
        it: DYNAMIC where the assignment was seen to overwrite its own earlier write (two passes assigned),
        STATIC where the profiling input showed at most one assigning pass and only the code says that there
        can be more. `reason` and `read_after_loop` say what the record is for a reader that knows them."""
        dep = Dependency(EdgeType.DATA)
        dep.dtype = DepType.WAW
        dep.var_name = var_name
        dep.source_line = write_line
        dep.sink_line = write_line
        dep.origin = DepOrigin.DYNAMIC_ANALYSIS if observed else DepOrigin.STATIC_ANALYSIS
        record = _blocker_record(loop_node, dep)
        record["reason"] = "conditional_last_value"
        record["read_after_loop"] = str(read_line)
        return record

    for node in tg.graph.nodes():
        # check if node is LoopParent
        if not isinstance(node.created_context, LoopParentContext):
            continue
        # check if loop is not already preventedvariables
        if node.pet_node_id in prevented_loops:
            continue
        # get child iterations
        iteration_contexts = [
            ctx for ctx in node.created_context.get_contained_contexts() if isinstance(ctx, IterationContext)
        ]
        if len(iteration_contexts) < 2:
            continue
        # get subtrees of iteration contexts
        subtrees: Dict[IterationContext, Set[Context]] = dict()
        for ic in iteration_contexts:
            subtrees[ic] = ic.get_contained_contexts(inclusive=True)
        # get loop variables for later check
        loop_variables = node.created_context.loop_variables
        # check for dependencies
        dependency_found = False
        reduction_info: List[Tuple[Context, Context, Dependency, Dict[str, str]]] = []
        potential_breaking_dependencies: List[Tuple[Context, Context, Dependency]] = []
        for ic_source in iteration_contexts:
            # collect nodes from other iterations
            other_iterations_subnodes: Set[Context] = set()
            for ic_other in iteration_contexts:
                if ic_source == ic_other:
                    continue
                other_iterations_subnodes.add(ic_other)
                other_iterations_subnodes = other_iterations_subnodes.union(subtrees[ic_other])
            # check for do-all preventing dependencies
            for subnode in subtrees[ic_source]:
                for out_dep_target, dep in subnode.outgoing_dependencies:
                    # WAR dependencies between iterations are non-critical, as they overwrite data and thus can be privatized
                    if dep.etype == EdgeType.DATA and dep.dtype == DepType.WAR:
                        continue

                    if out_dep_target in other_iterations_subnodes:
                        # check if the preventing dependency is a reduction dependency.
                        is_reduction_dependency = False
                        for red_var_dict in tg.pet.reduction_vars:
                            # check for correct parent loop
                            if red_var_dict["loop_line"] not in node.created_context.get_code_scope(tg.pet):
                                continue
                            # check for variable name
                            if red_var_dict["name"] != dep.var_name:
                                continue
                            # check for source code position
                            if red_var_dict["reduction_line"] not in subnode.get_code_scope(tg.pet):
                                continue
                            if red_var_dict["reduction_line"] not in out_dep_target.get_code_scope(tg.pet):
                                continue
                            # all of the previous requirements are met
                            is_reduction_dependency = True
                        if is_reduction_dependency:
                            # not a valid doall loop
                            reduction_info.append((subnode, out_dep_target, dep, red_var_dict))
                        #                            dependency_found = True
                        #                            break

                        # check for and allow accesses to the loop variable
                        if (dep.var_name, dep.memory_region) in loop_variables or is_reduction_dependency:
                            # dependency on loop variable or reduction variable
                            pass
                        else:
                            # check if dep.origin is static. If so, give it a "second chance", which is tested after classifying variables in the loop.
                            # --> In this case it is a valid doall, if the variable is firstwritten inside the loop
                            logger.debug(
                                "Prevents doall: "
                                + str(dep.dtype)
                                + " "
                                + str(dep.source_line)
                                + " "
                                + str(dep.sink_line)
                                + " "
                                + str(dep.var_name)
                                + " "
                                + str(dep.memory_region)
                                + " "
                                + "origin: "
                                + str(dep.origin)
                                + " "
                                + "source: "
                                + str(subnode.get_code_scope(tg.pet, inclusive=True))
                                + " "
                                + "out_dep_target: "
                                + str(out_dep_target.get_code_scope(tg.pet, inclusive=True))
                                + " "
                                + "source_ctx: "
                                + str(ic_source)
                                + " "
                                + "target_ctx: "
                                + str(out_dep_target)
                            )
                            if dep.origin == DepOrigin.DYNAMIC_ANALYSIS:
                                # dependency is trustworthy and definitely breaks doall
                                dependency_found = True
                                prevented_records.append(_blocker_record(node, dep))
                                break
                            else:
                                # dependency is static and may be too pessimistic.
                                # dependency is not problematic, if the variable is first written in the loop
                                potential_breaking_dependencies.append((ic_source, out_dep_target, dep))
                if dependency_found:
                    break
            if not dependency_found:
                # B13: two iterations writing the same ARRAY ELEMENT (a write-after-write the profile observed
                # between iterations, e.g. a scatter x[idx[i]] = ... whose indices repeat) is an output
                # dependence: the loop's result depends on which iteration writes last, and a plain
                # `parallel for` races. The task graph keeps these apart from its data-flow edges. A scalar
                # written in every iteration is left to privatization (the data-sharing clauses) as before, and
                # an array declared inside the loop body is private by its scope.
                for subnode in subtrees[ic_source]:
                    for out_dep_target, dep in subnode.outgoing_waw_dependencies:
                        if out_dep_target not in other_iterations_subnodes:
                            continue
                        if not str(dep.var_name).startswith("GEPRESULT_"):
                            continue
                        if (dep.var_name, dep.memory_region) in loop_variables:
                            continue
                        if _declared_inside_loop(tg, node, str(dep.var_name)[len("GEPRESULT_") :]):
                            continue
                        dependency_found = True
                        prevented_records.append(_blocker_record(node, dep))
                        break
                    if dependency_found:
                        break
            if dependency_found:
                break
        if dependency_found:
            # node is not a valid doall loop
            prevented_loops.add(node.pet_node_id)
            continue
        # get contexts contained in loopparent for later check
        loopparent_contained_ctxs = node.created_context.get_contained_contexts(inclusive=True)
        # node is a valid doall loop. Detect data sharing clauses
        logger.debug("CURRENT LOOP: " + str(node.created_context.get_code_scope(tg.pet)))
        firstprivate, private, lastprivate, shared, firstwritten, init, conditional_last = detect_doall_sharing_clauses(
            tg.pet,
            ast_helper,
            node.pet_node_id,
            iteration_contexts,
            loopparent_contained_ctxs,
            set([v[0] for v in loop_variables]),
            node.created_context.parent_loop,
        )
        reduction: Set[str] = set([ri[2].var_name for ri in reduction_info if ri[2].var_name is not None])
        # check potential_breaking_dependencies for cases which actually prevent doall
        for src_ctx, dst_ctx, dep in potential_breaking_dependencies:
            if dep.var_name not in firstwritten.union(init).union(reduction):
                # node is not a valid doall loop
                prevented_loops.add(node.pet_node_id)
                prevented_records.append(_blocker_record(node, dep))
                # print("LOOP: ", node.created_context.get_code_scope(tg.pet))
                # print("SECOND CHANCEs missed!: ", dep.dtype, dep.var_name)
                continue
            else:
                # static dependency does not actually prevent doall parallelization, as privatization is possible
                pass
        # if len(potential_breaking_dependencies) > 0:
        #    print(
        #        "HERE DUE TO SECOND CHANCEs!: ", [(d[2].dtype, d[2].var_name) for d in potential_breaking_dependencies]
        #    )
        # B19: a variable that is read after the loop and assigned in only some of its passes. `lastprivate`
        # would hand back the last CHUNK's value, not the last assignment's (TSVC s331: `if (a[i] < 0) j = i;`),
        # and DiscoPoP has no clause that says "the last assignment": the loop is not reported Do-All. Only a
        # loop that would otherwise be reported is concerned — one that a dependence blocks already keeps its
        # record as it was.
        if node.pet_node_id not in prevented_loops:
            for var_name in sorted(conditional_last):
                if var_name in reduction:
                    continue
                write_line, read_line, observed = conditional_last[var_name]
                prevented_loops.add(node.pet_node_id)
                record = _last_value_record(node, var_name, write_line, read_line, observed)
                if record not in prevented_records:
                    prevented_records.append(record)
                break

        # Register a pattern
        pattern: DoAllInfo | ReductionInfo
        if len(reduction) == 0:
            # register DoAll pattern
            pattern = DoAllInfo(tg.pet, tg.pet.node_at(node.pet_node_id))
            pattern.first_private = [Variable(type="UNKNOWN", name=VarName(v), defLine="UNKNOWN") for v in firstprivate]
            pattern.private = [Variable(type="UNKNOWN", name=VarName(v), defLine="UNKNOWN") for v in private]
            pattern.last_private = [Variable(type="UNKNOWN", name=VarName(v), defLine="UNKNOWN") for v in lastprivate]
            pattern.shared = [Variable(type="UNKNOWN", name=VarName(v), defLine="UNKNOWN") for v in shared]
        else:
            # register reduction pattern
            reduction_vars: List[Variable] = []
            for ri in reduction_info:
                if ri[2].var_name is None:
                    continue
                var = Variable(type="unknown", name=VarName(ri[2].var_name), defLine="LineNotFound")
                # correct operation
                red_op = ri[3]["operation"]
                logger.debug("RED OP: " + red_op + " var: " + var.name)
                if red_op == ">":
                    red_op = "max"
                if red_op == "<":
                    red_op = "min"
                var.operation = red_op
                # prevent duplicates
                duplicate = False

                for elem in reduction_vars:
                    if "name" not in var.__dict__ or "name" not in elem.__dict__:
                        continue
                    if var.__dict__["name"] == elem.__dict__["name"]:
                        duplicate = True
                        break
                if not duplicate:
                    reduction_vars.append(var)

            if node.created_context.parent_loop is None:
                continue
            pattern = ReductionInfo(tg.pet, tg.pet.node_at(node.created_context.parent_loop), reduction=reduction_vars)
            pattern.first_private = [
                Variable(type="UNKNOWN", name=VarName(v), defLine="UNKNOWN") for v in firstprivate if v not in reduction
            ]
            pattern.private = [
                Variable(type="UNKNOWN", name=VarName(v), defLine="UNKNOWN") for v in private if v not in reduction
            ]
            pattern.last_private = [
                Variable(type="UNKNOWN", name=VarName(v), defLine="UNKNOWN") for v in lastprivate if v not in reduction
            ]
            pattern.shared = [
                Variable(type="UNKNOWN", name=VarName(v), defLine="UNKNOWN") for v in shared if v not in reduction
            ]

        # prevent duplicates. Necessary since multiple copies of the same loop might exist
        if pattern.pattern_tag in [p.pattern_tag for p in patterns]:
            continue
        patterns.append(pattern)

    # clean patterns agains prevented loops
    patterns = [p for p in patterns if p.node_id not in prevented_loops]

    # discopop_agent integration: persist the Do-All blockers (fresh each run,
    # written next to patterns.json in explorer/).  Best-effort; never fatal.
    try:
        os.makedirs("explorer", exist_ok=True)
        with open(os.path.join("explorer", "doall_prevented.json"), "w") as _f:
            json.dump(prevented_records, _f, indent=2)
    except OSError as _e:
        logger.warning("could not write doall_prevented.json: " + str(_e))

    return patterns


def detect_doall_sharing_clauses(
    pet: PEGraphX,
    ast_helper: ASTPatternDetectionHelper,
    loop_node_id: NodeID,
    iteration_contexts: List[IterationContext],
    loopparent_contained_ctxs: Set[Context],
    loop_variables: Set[str],
    pet_loop_id: Optional[NodeID] = None,
) -> Tuple[
    Set[str],
    Set[str],
    Set[str],
    Set[str],
    Set[str],
    Set[str],
    Dict[str, Tuple[Optional[LineID], Optional[LineID], bool]],
]:
    """classifies variables used inside the iterations and returns the OpenMP data sharing clauses in the following structure:
    (firstprivate, private, lastprivate, shared, firstwritten, init, conditional_last)
    firstwritten and init are not data sharing clauses, but required to validate potential doall-breaking dependencies originating from static information.
    conditional_last (B19) is no clause either: the variables that are read after the loop but assigned in only
    some of its passes, each with the line of an assignment, the line of a read after the loop, and whether the
    profile holds the assignment overwriting itself. No clause DiscoPoP writes fits them; the caller does not
    report the loop as Do-All.
    """
    logger.debug("-------------------- LOOP START ---------------------")
    # Initialization
    # calculate CUs contained in the loop parent for later use dureing filtering
    contained_tg_nodes_in_loopparent: List[TGNode] = []
    for ctx in loopparent_contained_ctxs:
        contained_tg_nodes_in_loopparent += ctx.contained_nodes
    contained_cu_node_ids_in_loopparent = set(
        [tg.pet_node_id for tg in contained_tg_nodes_in_loopparent if tg.pet_node_id is not None]
    )

    # get known variables for source location from AST
    file_id = pet.node_at(loop_node_id).file_id
    line_num = pet.node_at(loop_node_id).start_line

    known_vars_with_types = ast_helper.get_variables_at_location(file_id, line_num)
    known_vars = set([v[0] for v in known_vars_with_types])
    logger.debug("\t--> known variables with types: " + str(known_vars_with_types))

    # B19: the units that are the loop's own (nested loops included), and those with what they call. The task
    # graph can place a unit of the code AROUND the loop inside one of its iterations (TSVC s481, an `exit(0)`
    # in the body: the enclosing loop's `nl++` stood in the inner loop's iteration, and `nl` came out
    # `lastprivate` of a loop that never touches it). Such a unit's accesses are not the loop's and say
    # nothing about its data-sharing clauses.
    # (`loop_node_id` is the unit the task graph's loop starts at; `pet_loop_id` is the loop itself. Where the
    # loop is not known the units cannot be told apart, and the classification is the one it was before.)
    own_cu_ids: Optional[Set[NodeID]] = None
    own_or_called_cu_ids: Optional[Set[NodeID]] = None
    pet_loop: Optional[Node] = None
    if pet_loop_id is not None and isinstance(pet.node_at(pet_loop_id), LoopNode):
        pet_loop = pet.node_at(pet_loop_id)
    else:
        # the loop that holds the unit the task graph's loop starts at
        for parent_id, _, _ in in_edges(pet, loop_node_id, EdgeType.CHILD):
            if isinstance(pet.node_at(parent_id), LoopNode):
                pet_loop = pet.node_at(parent_id)
                break
    logger.debug(
        "\t--> the loop: " + str(pet_loop.id if pet_loop is not None else None) + " (given: " + str(pet_loop_id) + ")"
    )
    if pet_loop is not None:
        own_cu_ids = set([n.id for n in subtree_of_type(pet, pet_loop, CUNode)])
        own_or_called_cu_ids = set(
            [n.id for n in subtree_of_type(pet, pet_loop, CUNode, ignore_called_functions=False)]
        )
    conditional_last: Dict[str, Tuple[Optional[LineID], Optional[LineID], bool]] = dict()
    logger.debug("\t--> the loop's own units: " + str(sorted(own_cu_ids) if own_cu_ids is not None else None))

    # shared:
    # - no dependency between iterations
    # private:
    # - no dependency between iterations && first written in iteration && no RAW from outside to inside of loop
    # lastprivate:
    # - no dependency between iterations && read from outside to inside of loop
    # firstprivate:
    # - no dependency between iterations && first read in iterations && written in iteration
    # IMPORTANT: first- and lastprivate can be applied to one variable at the same time!
    # -> Check them independently
    # -> private and lastprivate / firstprivate can NOT be used at the same time.

    # # TODO update
    # reformatted condition to better suit the available data:
    # shared:
    # - outside dependency but not to or from the other iteration
    # private:
    # - outside dependency but not to or from the other iteration && RAW or WAW between first and second access in contained sequence && no RAW from outside to inside of loop
    # lastprivate:
    # - outside dependency but none to or from the other iteration && RAW or WAW between first and second access in contained sequence && read from outside to inside of loop
    # firstprivate:
    # - outside dependency but none to or from the other iteration && outgoing RAW from first access in contained sequence && RAW or WAR exists within

    private: Set[str] = set()
    shared: Set[str] = set()
    lastprivate: Set[str] = set()
    firstprivate: Set[str] = set()
    firstwritten: Set[str] = set()
    init: Set[str] = set()
    gep_result_access: Set[str] = set()
    ptr_type_access: Set[str] = set()

    # the units of each modelled iteration, in sequence
    sequences: List[List[NodeID]] = []
    for it_ctx in iteration_contexts:
        contained_contexts_in_sequence = it_ctx.get_contained_contexts_in_sequence(pet)
        #        print("contained CTXs in sequence: ", [c.get_code_scope(pet) for c in contained_contexts_in_sequence])
        contained_tg_nodes_in_sequence: List[TGNode] = []
        for ctx in contained_contexts_in_sequence:
            contained_tg_nodes_in_sequence += ctx.contained_nodes
        #        print("contained tg nodes in sequence: ", [(n, n.pet_node_id) for n in contained_tg_nodes_in_sequence])
        sequences.append([tg.pet_node_id for tg in contained_tg_nodes_in_sequence if tg.pet_node_id is not None])

    # B19: an ARRAY (`real_t a_old[N]`, type `real_t[N]`) is reached through its address as a pointer's target
    # is. Taken for a scalar it came out `lastprivate` on the loop that fills it — every thread fills a copy of
    # its own and only the last thread's is handed back — and `firstprivate` on a loop that reads it, a copy of
    # the whole array per thread. Where the loop only reads the array, or its own statements write it, the
    # array is `shared`: the loop is a Do-All, so no two passes write the same element under the array's name
    # (B13 blocks that). NOT where a function the loop calls writes it: the callee's stores go by its
    # parameter's name, the detector cannot see whether every pass fills the same elements, and where it does —
    # a work array (burkardt/md: `d = dist(nd, …, rij)` fills `rij`, the loop then reads `rij[i]`) — each
    # thread needs the array for itself. Such an array keeps the classification it had before
    # (`firstprivate`/`private`); `shared` made the directive race.
    array_typed: Set[str] = set(
        name
        for name, type_str in known_vars_with_types
        if type_str is not None and "[" in type_str and "*" not in type_str and "&" not in type_str
    )
    arrays_written_by_callees: Set[str] = set()
    if own_cu_ids is None or own_or_called_cu_ids is None:
        arrays_written_by_callees = set(array_typed)  # the units cannot be told apart: as before the repair
    elif array_typed:
        # every unit of a function the loop calls, whether or not the task graph put it into a modelled
        # iteration: one copy of md's force loop shows `rij` as read only, its values coming from `dist`'s unit
        for cu_node_id in sorted(own_or_called_cu_ids - own_cu_ids):
            arrays_written_by_callees |= array_typed & _names_written_by(pet, cu_node_id)
    logger.debug("\t--> arrays a called function writes: " + str(sorted(arrays_written_by_callees)))

    for contained_cu_node_ids_in_sequence in sequences:
        #        print("contained cu nodes in sequence: ", contained_cu_node_ids_in_sequence)
        logger.debug("\t--> CUs in sequence: " + str(contained_cu_node_ids_in_sequence))

        # -> get lists of firstwritten, firstread, written, read, read_in, read_out for all iterations.
        # -> use the gathered lists to determine sharing clauses after the loop over iteration contexts
        it_init: Set[str] = set()
        written: Set[str] = set()
        read: Set[str] = set()
        it_firstwritten: Set[str] = set()
        firstread: Set[str] = set()
        data_incoming: Set[str] = set()
        data_outgoing: Set[str] = set()
        # B19: per variable, the loop's units that write it, the line of a write, the line of a read after the loop
        writer_units: Dict[str, Set[NodeID]] = dict()
        write_line: Dict[str, Optional[LineID]] = dict()
        read_after_line: Dict[str, Optional[LineID]] = dict()

        for cu_node_id in contained_cu_node_ids_in_sequence:
            if own_or_called_cu_ids is not None and cu_node_id not in own_or_called_cu_ids:
                continue
            incoming_deps = in_edges(pet, cu_node_id, EdgeType.DATA)
            outgoing_deps = out_edges(pet, cu_node_id, EdgeType.DATA)

            # TODO:# filter incoming and outgoing deps to ignore nodes within the parent loop
            # TODO: ignore variables defined inside the loop
            # reasone: remove data sharing clauses correlating to loop headers etc.
            incoming_deps = [
                d
                for d in incoming_deps
                if d[0] not in contained_cu_node_ids_in_loopparent - set(contained_cu_node_ids_in_sequence)
            ]
            outgoing_deps = [
                d
                for d in outgoing_deps
                if d[1] not in contained_cu_node_ids_in_loopparent - set(contained_cu_node_ids_in_sequence)
            ]

            # outgoing
            #   RAW: cu reads
            #   WAR: cu overwrites
            #   WAW: cu overwrites
            # incoming:
            #   RAW: value is used after cu wrote the value
            #   WAR: value is overwritten after cu read the value
            #   WAW: value is overwritten after cu wrote the value

            # The accesses of this CU are taken in PROGRAM order: by the line of this CU's access (an
            # outgoing edge has this CU as the sink, an incoming one as the source). On one line, a read
            # and a write of the same memory region and of the same kind (both a scalar, or both an
            # element reached through an address) are one statement reading and then writing it
            # (`s += a[i]`, `a[i] += x`): the read comes first. A plain read under the same name as an
            # element store is the address the store goes through (`dr[i] = …` loads the pointer `dr`):
            # the store decides.
            # The edges used to be taken in the order the profile listed its records, which follows how
            # the profiler happened to number its call-path states: a variable a statement reads and
            # writes came out "first written" on some profiles, and a static dependence on it — the
            # recurrence itself — was then excused as privatizable: a running total reported Do-All
            # with `shared(running)` (B10, docs/DISCOPOP_BUG_REPORTS.md).
            def _access_line(line_id: Optional[LineID]) -> int:
                try:
                    return int(str(line_id).split(":")[1])
                except (IndexError, ValueError):
                    return 1 << 30  # no position: after every positioned access, in the old order

            accesses: List[Tuple[int, bool, bool, Any, Any, Dependency]] = []  # (line, is_read, outgoing, …)
            for src, dst, dep in outgoing_deps:
                accesses.append((_access_line(dep.sink_line), dep.dtype == DepType.RAW, True, src, dst, dep))
            for src, dst, dep in incoming_deps:
                accesses.append((_access_line(dep.source_line), dep.dtype == DepType.WAR, False, src, dst, dep))
            regions: Dict[Tuple[int, Optional[str], bool, bool], Set[str]] = dict()
            for line_no, is_read, _o, _s, _d, dep in accesses:
                key = (line_no, dep.var_name, is_read, dep.is_gep_result_dependency)
                regions.setdefault(key, set()).add(str(dep.memory_region))

            def _order(line_no: int, is_read: bool, dep: Dependency) -> int:
                if not is_read:
                    return 1
                gep = dep.is_gep_result_dependency
                same_region_written = regions.get((line_no, dep.var_name, True, gep), set()) & regions.get(
                    (line_no, dep.var_name, False, gep), set()
                )
                return 0 if same_region_written else 2

            events: List[Tuple[int, int, bool, Any, Any, Dependency]] = [
                (line_no, _order(line_no, is_read, dep), outgoing, src, dst, dep)
                for line_no, is_read, outgoing, src, dst, dep in accesses
            ]
            events.sort(key=lambda e: (e[0], e[1]))
            logger.debug(
                "\t--> accesses of "
                + str(cu_node_id)
                + ": "
                + str([(e[0], str(e[5].dtype).split(".")[-1], "out" if e[2] else "in", e[5].var_name) for e in events])
            )

            for _line, _rank, is_outgoing, src, dst, dep in events:
                if dep.var_name is None:
                    continue

                if is_outgoing:
                    # check if dep is access to array type value (or result of pointer arithmetic)
                    if dep.is_gep_result_dependency:
                        gep_result_access.add(dep.var_name)
                    # check if dep is access to pointer or reference type
                    if dep.var_name in known_vars:
                        for tmp_var_name, type_str in known_vars_with_types:
                            if type_str is None:
                                continue
                            if tmp_var_name == dep.var_name:
                                if "*" in type_str or "&" in type_str:
                                    ptr_type_access.add(dep.var_name)
                                elif "[" in type_str and dep.var_name not in arrays_written_by_callees:
                                    # B19: an array the loop reads or writes itself (see above)
                                    ptr_type_access.add(dep.var_name)

                    if dep.dtype == DepType.RAW:
                        if dep.var_name not in written:
                            firstread.add(dep.var_name)
                        read.add(dep.var_name)
                        if dst not in contained_cu_node_ids_in_sequence:
                            data_incoming.add(dep.var_name)
                    elif dep.dtype == DepType.WAR:
                        if dep.var_name not in read:
                            it_firstwritten.add(dep.var_name)
                        written.add(dep.var_name)
                        writer_units.setdefault(dep.var_name, set()).add(cu_node_id)
                        write_line.setdefault(dep.var_name, dep.sink_line)
                    elif dep.dtype == DepType.WAW:
                        if dep.var_name not in read:
                            it_firstwritten.add(dep.var_name)
                        written.add(dep.var_name)
                        writer_units.setdefault(dep.var_name, set()).add(cu_node_id)
                        write_line.setdefault(dep.var_name, dep.sink_line)
                    elif dep.dtype == DepType.INIT:
                        if dep.var_name not in read:
                            it_firstwritten.add(dep.var_name)
                        it_init.add(dep.var_name)
                        written.add(dep.var_name)
                        writer_units.setdefault(dep.var_name, set()).add(cu_node_id)
                        write_line.setdefault(dep.var_name, dep.sink_line)
                    else:
                        raise ValueError("Unsupported dependency type: " + str(dep.dtype))
                else:
                    if dep.dtype == DepType.RAW:
                        if dep.var_name not in read:
                            it_firstwritten.add(dep.var_name)
                        written.add(dep.var_name)
                        writer_units.setdefault(dep.var_name, set()).add(cu_node_id)
                        write_line.setdefault(dep.var_name, dep.source_line)
                        if src not in contained_cu_node_ids_in_sequence:
                            data_outgoing.add(dep.var_name)
                            earlier = read_after_line.get(dep.var_name)
                            if earlier is None or _access_line(dep.sink_line) < _access_line(earlier):
                                read_after_line[dep.var_name] = dep.sink_line
                    elif dep.dtype == DepType.WAR:
                        if dep.var_name not in written:
                            firstread.add(dep.var_name)
                        read.add(dep.var_name)
                    elif dep.dtype == DepType.WAW:
                        if dep.var_name not in read:
                            it_firstwritten.add(dep.var_name)
                        written.add(dep.var_name)
                        writer_units.setdefault(dep.var_name, set()).add(cu_node_id)
                        write_line.setdefault(dep.var_name, dep.source_line)
                    elif dep.dtype == DepType.INIT:
                        if dep.var_name not in read:
                            it_firstwritten.add(dep.var_name)
                        it_init.add(dep.var_name)
                        written.add(dep.var_name)
                        writer_units.setdefault(dep.var_name, set()).add(cu_node_id)
                        write_line.setdefault(dep.var_name, dep.source_line)
                    else:
                        raise ValueError("Usupported dependency type: " + str(dep.dtype))

        #            print("cunode -> ", cu_node_id)
        # print("--> in deps:", [(d[2].dtype, d[0], d[2].var_name) for d in incoming_deps])
        # print("--> out_deps: ", [(d[2].dtype, d[1], d[2].var_name) for d in outgoing_deps])
        logger.debug("\t--> written: " + str(written))
        logger.debug("\t--> read: " + str(read))
        logger.debug("\t--> data_incoming: " + str(data_incoming))
        logger.debug("\t--> data_outgoing: " + str(data_outgoing))
        logger.debug("\t--> firstread: " + str(firstread))
        logger.debug("\t--> it_firstwritten: " + str(it_firstwritten))
        logger.debug("\t--> it_init: " + str(it_init))
        logger.debug("\t--> gep_result_access: " + str(gep_result_access))
        logger.debug("\t--> ptr_type_access: " + str(ptr_type_access))
        # dependency between iterations is trivially not possible, as this would invalidate the doall pattern.
        # Classification scheme:
        # shared:
        # - no dependency between iterations
        # private:
        # - no dependency between iterations && first written in iteration && no RAW from outside to inside of loop
        # lastprivate:
        # - no dependency between iterations && read from outside to inside of loop
        # firstprivate:
        # - no dependency between iterations && first read in iterations && written in iteration

        # iterate over all found variable names. use set union via '|'
        it_private: Set[str] = set()
        it_shared: Set[str] = set()
        it_lastprivate: Set[str] = set()
        it_firstprivate: Set[str] = set()

        for var_name in written | read | data_incoming | data_outgoing | firstread | it_firstwritten:
            # ignore loop variables
            if var_name in loop_variables:
                continue
            # -> classification of the variables clauses according to scheme above
            if var_name in written:
                if var_name in data_outgoing:
                    if var_name in ptr_type_access:
                        it_shared.add(var_name)
                    else:
                        it_lastprivate.add(var_name)
                if var_name in firstread and var_name not in it_init:
                    it_firstprivate.add(var_name)
                if (
                    var_name not in data_outgoing
                    and var_name not in data_incoming
                    and var_name not in it_init
                    and var_name not in it_lastprivate
                    and var_name not in it_firstprivate
                ):
                    if var_name in ptr_type_access:
                        it_shared.add(var_name)
                    else:
                        it_private.add(var_name)
                if (
                    var_name in data_incoming
                    and var_name in it_firstwritten
                    and var_name not in it_lastprivate
                    and var_name not in it_firstprivate
                    and var_name not in it_private
                ):
                    it_shared.add(var_name)

                if (
                    var_name not in it_private
                    and var_name not in it_shared
                    and var_name not in it_lastprivate
                    and var_name not in it_firstprivate
                    and var_name in it_init
                    and var_name in ptr_type_access
                ):
                    # array initializations without immediate successive uses
                    it_shared.add(var_name)

                if (
                    var_name not in it_private
                    and var_name not in it_shared
                    and var_name not in it_lastprivate
                    and var_name not in it_firstprivate
                    and var_name in it_init
                ):
                    it_private.add(var_name)

                assert (
                    var_name in it_lastprivate
                    or var_name in it_firstprivate
                    or var_name in it_private
                    or var_name in it_init
                    or var_name in it_shared
                )
            else:
                # read-only
                if var_name in ptr_type_access:
                    it_shared.add(var_name)
                else:
                    it_firstprivate.add(var_name)
            assert (
                var_name in it_lastprivate
                or var_name in it_firstprivate
                or var_name in it_private
                or var_name in it_shared
                or var_name in it_init
            )

        # B19: `lastprivate` is the variable's value after the loop only if the last pass assigns it
        for var_name in sorted(it_lastprivate):
            if own_cu_ids is None:
                break
            if not _written_in_every_pass(pet, own_cu_ids, writer_units.get(var_name, set())):
                it_lastprivate.discard(var_name)
                seen_twice = _seen_to_overwrite_itself(pet, own_cu_ids, writer_units.get(var_name, set()), var_name)
                earlier_record = conditional_last.get(var_name)
                conditional_last[var_name] = (
                    write_line.get(var_name) if earlier_record is None else earlier_record[0],
                    read_after_line.get(var_name) if earlier_record is None else earlier_record[1],
                    seen_twice or (earlier_record is not None and earlier_record[2]),
                )

        logger.debug("\tit_private: " + str(it_private))
        logger.debug("\tit_shared: " + str(it_shared))
        logger.debug("\tit_lastprivate: " + str(it_lastprivate))
        logger.debug("\tconditional_last: " + str(conditional_last))
        logger.debug("\tit_firstprivate: " + str(it_firstprivate))
        logger.debug("\tloop_vars: " + str(loop_variables))

        # save classifications
        private = private.union(it_private)
        shared = shared.union(it_shared)
        lastprivate = lastprivate.union(it_lastprivate)
        firstprivate = firstprivate.union(it_firstprivate)
        firstwritten = firstwritten.union(it_firstwritten)
        init = init.union(it_init)
        logger.debug("----------------------- IT END ------------------")

    # merge classifications
    logger.debug("")
    logger.debug("\tPRE MERGE: private: " + str(private))
    logger.debug("\tPRE MERGE: shared: " + str(shared))
    logger.debug("\tPRE MERGE: lastprivate: " + str(lastprivate))
    logger.debug("\tPRE MERGE: firstprivate: " + str(firstprivate))
    logger.debug("")
    firstprivate, private, lastprivate, shared = __merge_classifications(firstprivate, private, lastprivate, shared)
    logger.debug("\tPOST MERGE: private: " + str(private))
    logger.debug("\tPOST MERGE: shared: " + str(shared))
    logger.debug("\tPOST MERGE: lastprivate: " + str(lastprivate))
    logger.debug("\tPOST MERGE: firstprivate: " + str(firstprivate))
    logger.debug("")
    firstprivate, private, lastprivate, shared = __filter_classifications(
        known_vars, firstprivate, private, lastprivate, shared
    )
    logger.debug("\tPOST FILTER: private: " + str(private))
    logger.debug("\tPOST FILTER: shared: " + str(shared))
    logger.debug("\tPOST FILTER: lastprivate: " + str(lastprivate))
    logger.debug("\tPOST FILTER: firstprivate: " + str(firstprivate))
    logger.debug("---------------------------- LOOP END --------------------")
    logger.debug("")
    # a variable some modelled iteration assigns in every pass and another only under a condition is the latter
    conditional_last = {v: lines for v, lines in conditional_last.items() if v in known_vars}
    lastprivate = lastprivate - set(conditional_last)
    return firstprivate, private, lastprivate, shared, firstwritten, init, conditional_last


def __merge_classifications(
    first_private: Set[str],
    private: Set[str],
    last_private: Set[str],
    shared: Set[str],
) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    new_first_private: Set[str] = set()
    new_private: Set[str] = set()
    new_last_private: Set[str] = set()
    new_shared: Set[str] = set()

    remove_from_private: Set[str] = set()
    remove_from_first_private: Set[str] = set()
    remove_from_last_private: Set[str] = set()
    remove_from_shared: Set[str] = set()

    # Rule 1: firstprivate is more restrictive than private
    remove_from_private = first_private.intersection(private)
    # Rule 2: lastprivate is more restrictive than private
    remove_from_private = remove_from_private.union(last_private.intersection(private))
    # Rule 3: shared is less restrictive than first_private or last_private
    remove_from_shared = shared.intersection(first_private.union(last_private))
    # Rule 4: if a variable is classifyable as shared and private, select shared.
    remove_from_private = remove_from_private.union(shared.intersection(private))

    new_first_private = first_private - remove_from_first_private
    new_last_private = last_private - remove_from_last_private
    new_private = private - remove_from_private
    new_shared = shared - remove_from_shared

    return new_first_private, new_private, new_last_private, new_shared


def __filter_classifications(
    known_vars: Set[str],
    first_private: Set[str],
    private: Set[str],
    last_private: Set[str],
    shared: Set[str],
) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    new_first_private: Set[str] = set()
    new_private: Set[str] = set()
    new_last_private: Set[str] = set()
    new_shared: Set[str] = set()

    remove_from_private: Set[str] = set()
    remove_from_first_private: Set[str] = set()
    remove_from_last_private: Set[str] = set()
    remove_from_shared: Set[str] = set()

    # perform filtering
    for var in first_private:
        if var not in known_vars:
            remove_from_first_private.add(var)
    for var in private:
        if var not in known_vars:
            remove_from_private.add(var)
    for var in last_private:
        if var not in known_vars:
            remove_from_last_private.add(var)
    for var in shared:
        if var not in known_vars:
            remove_from_shared.add(var)

    new_first_private = first_private - remove_from_first_private
    new_last_private = last_private - remove_from_last_private
    new_private = private - remove_from_private
    new_shared = shared - remove_from_shared

    return new_first_private, new_private, new_last_private, new_shared
