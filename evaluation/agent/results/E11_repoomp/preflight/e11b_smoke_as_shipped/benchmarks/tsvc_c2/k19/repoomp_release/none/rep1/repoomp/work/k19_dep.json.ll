; ModuleID = '/home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e11b_smoke/benchmarks/tsvc_c2/k19/repoomp_release/none/rep1/repoomp/work/src/k19.c'
source_filename = "/home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e11b_smoke/benchmarks/tsvc_c2/k19/repoomp_release/none/rep1/repoomp/work/src/k19.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@v = external global ptr, align 8
@kv = external global ptr, align 8
@c = external global ptr, align 8
@u = external global ptr, align 8
@ju = external global ptr, align 8
@ku = external global ptr, align 8
@d = external global ptr, align 8
@jv = external global ptr, align 8
@a = external global ptr, align 8
@b = external global ptr, align 8
@e = external global ptr, align 8

; Function Attrs: noinline nounwind optnone uwtable
define dso_local double @kernel_k19() #0 !dbg !15 {
  %1 = alloca i32, align 4
  %2 = alloca i64, align 8
    #dbg_declare(ptr %1, !19, !DIExpression(), !22)
  store i32 0, ptr %1, align 4, !dbg !22
  br label %3, !dbg !23

3:                                                ; preds = %66, %0
  %4 = load i32, ptr %1, align 4, !dbg !24
  %5 = icmp slt i32 %4, 48, !dbg !26
  br i1 %5, label %6, label %69, !dbg !27

6:                                                ; preds = %3
    #dbg_declare(ptr %2, !28, !DIExpression(), !32)
  store i64 1, ptr %2, align 8, !dbg !32
  br label %7, !dbg !33

7:                                                ; preds = %56, %6
  %8 = load i64, ptr %2, align 8, !dbg !34
  %9 = icmp slt i64 %8, 32000, !dbg !36
  br i1 %9, label %10, label %59, !dbg !37

10:                                               ; preds = %7
  %11 = load ptr, ptr @v, align 8, !dbg !38
  %12 = load ptr, ptr @kv, align 8, !dbg !40
  %13 = load i64, ptr %2, align 8, !dbg !41
  %14 = getelementptr inbounds i32, ptr %12, i64 %13, !dbg !40
  %15 = load i32, ptr %14, align 4, !dbg !40
  %16 = sext i32 %15 to i64, !dbg !38
  %17 = getelementptr inbounds double, ptr %11, i64 %16, !dbg !38
  %18 = load double, ptr %17, align 8, !dbg !38
  %19 = load ptr, ptr @c, align 8, !dbg !42
  %20 = load i64, ptr %2, align 8, !dbg !43
  %21 = getelementptr inbounds double, ptr %19, i64 %20, !dbg !42
  %22 = load double, ptr %21, align 8, !dbg !42
  %23 = load ptr, ptr @u, align 8, !dbg !44
  %24 = load ptr, ptr @ju, align 8, !dbg !45
  %25 = load i64, ptr %2, align 8, !dbg !46
  %26 = getelementptr inbounds i32, ptr %24, i64 %25, !dbg !45
  %27 = load i32, ptr %26, align 4, !dbg !45
  %28 = sext i32 %27 to i64, !dbg !44
  %29 = getelementptr inbounds double, ptr %23, i64 %28, !dbg !44
  %30 = load double, ptr %29, align 8, !dbg !47
  %31 = call double @llvm.fmuladd.f64(double %18, double %22, double %30), !dbg !47
  store double %31, ptr %29, align 8, !dbg !47
  %32 = load ptr, ptr @u, align 8, !dbg !48
  %33 = load ptr, ptr @ku, align 8, !dbg !49
  %34 = load i64, ptr %2, align 8, !dbg !50
  %35 = getelementptr inbounds i32, ptr %33, i64 %34, !dbg !49
  %36 = load i32, ptr %35, align 4, !dbg !49
  %37 = sext i32 %36 to i64, !dbg !48
  %38 = getelementptr inbounds double, ptr %32, i64 %37, !dbg !48
  %39 = load double, ptr %38, align 8, !dbg !48
  %40 = load ptr, ptr @d, align 8, !dbg !51
  %41 = load i64, ptr %2, align 8, !dbg !52
  %42 = getelementptr inbounds double, ptr %40, i64 %41, !dbg !51
  %43 = load double, ptr %42, align 8, !dbg !51
  %44 = load ptr, ptr @c, align 8, !dbg !53
  %45 = load i64, ptr %2, align 8, !dbg !54
  %46 = getelementptr inbounds double, ptr %44, i64 %45, !dbg !53
  %47 = load double, ptr %46, align 8, !dbg !53
  %48 = call double @llvm.fmuladd.f64(double %39, double %43, double %47), !dbg !55
  %49 = load ptr, ptr @v, align 8, !dbg !56
  %50 = load ptr, ptr @jv, align 8, !dbg !57
  %51 = load i64, ptr %2, align 8, !dbg !58
  %52 = getelementptr inbounds i32, ptr %50, i64 %51, !dbg !57
  %53 = load i32, ptr %52, align 4, !dbg !57
  %54 = sext i32 %53 to i64, !dbg !56
  %55 = getelementptr inbounds double, ptr %49, i64 %54, !dbg !56
  store double %48, ptr %55, align 8, !dbg !59
  br label %56, !dbg !60

56:                                               ; preds = %10
  %57 = load i64, ptr %2, align 8, !dbg !61
  %58 = add nsw i64 %57, 1, !dbg !61
  store i64 %58, ptr %2, align 8, !dbg !61
  br label %7, !dbg !62, !llvm.loop !63

59:                                               ; preds = %7
  %60 = load ptr, ptr @a, align 8, !dbg !66
  %61 = load ptr, ptr @b, align 8, !dbg !67
  %62 = load ptr, ptr @c, align 8, !dbg !68
  %63 = load ptr, ptr @d, align 8, !dbg !69
  %64 = load ptr, ptr @e, align 8, !dbg !70
  %65 = call i32 @dummy(ptr noundef %60, ptr noundef %61, ptr noundef %62, ptr noundef %63, ptr noundef %64), !dbg !71
  br label %66, !dbg !72

66:                                               ; preds = %59
  %67 = load i32, ptr %1, align 4, !dbg !73
  %68 = add nsw i32 %67, 1, !dbg !73
  store i32 %68, ptr %1, align 4, !dbg !73
  br label %3, !dbg !74, !llvm.loop !75

69:                                               ; preds = %3
  ret double 0.000000e+00, !dbg !77
}

; Function Attrs: nocallback nofree nosync nounwind speculatable willreturn memory(none)
declare double @llvm.fmuladd.f64(double, double, double) #1

declare i32 @dummy(ptr noundef, ptr noundef, ptr noundef, ptr noundef, ptr noundef) #2

attributes #0 = { noinline nounwind optnone uwtable "frame-pointer"="all" "min-legal-vector-width"="0" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }
attributes #1 = { nocallback nofree nosync nounwind speculatable willreturn memory(none) }
attributes #2 = { "frame-pointer"="all" "no-trapping-math"="true" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+cmov,+cx8,+fxsr,+mmx,+sse,+sse2,+x87" "tune-cpu"="generic" }

!llvm.dbg.cu = !{!0}
!llvm.module.flags = !{!6, !7, !8, !9, !10, !11, !12, !13}
!llvm.ident = !{!14}

!0 = distinct !DICompileUnit(language: DW_LANG_C11, file: !1, producer: "Ubuntu clang version 20.1.2 (0ubuntu1~24.04.3)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !2, splitDebugInlining: false, nameTableKind: None)
!1 = !DIFile(filename: "/home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e11b_smoke/benchmarks/tsvc_c2/k19/repoomp_release/none/rep1/repoomp/work/src/k19.c", directory: "/home/ahmedabosamaha/discopop_agent/evaluation/benchmarks/RepoOMP/Method", checksumkind: CSK_MD5, checksum: "2eb9e20fd03efa932eadc8fca5d0e25c")
!2 = !{!3}
!3 = !DIDerivedType(tag: DW_TAG_typedef, name: "real_t", file: !4, line: 25, baseType: !5)
!4 = !DIFile(filename: "agent/runs/e11b_smoke/benchmarks/tsvc_c2/k19/repoomp_release/none/rep1/repoomp/work/src/data.h", directory: "/home/ahmedabosamaha/discopop_agent/evaluation", checksumkind: CSK_MD5, checksum: "d0facf4574dc5a804fc1c9ec8cddddbe")
!5 = !DIBasicType(name: "double", size: 64, encoding: DW_ATE_float)
!6 = !{i32 7, !"Dwarf Version", i32 5}
!7 = !{i32 2, !"Debug Info Version", i32 3}
!8 = !{i32 1, !"wchar_size", i32 4}
!9 = !{i32 7, !"openmp", i32 51}
!10 = !{i32 8, !"PIC Level", i32 2}
!11 = !{i32 7, !"PIE Level", i32 2}
!12 = !{i32 7, !"uwtable", i32 2}
!13 = !{i32 7, !"frame-pointer", i32 2}
!14 = !{!"Ubuntu clang version 20.1.2 (0ubuntu1~24.04.3)"}
!15 = distinct !DISubprogram(name: "kernel_k19", scope: !16, file: !16, line: 3, type: !17, scopeLine: 4, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !18)
!16 = !DIFile(filename: "agent/runs/e11b_smoke/benchmarks/tsvc_c2/k19/repoomp_release/none/rep1/repoomp/work/src/k19.c", directory: "/home/ahmedabosamaha/discopop_agent/evaluation", checksumkind: CSK_MD5, checksum: "2eb9e20fd03efa932eadc8fca5d0e25c")
!17 = !DISubroutineType(types: !2)
!18 = !{}
!19 = !DILocalVariable(name: "nl", scope: !20, file: !16, line: 5, type: !21)
!20 = distinct !DILexicalBlock(scope: !15, file: !16, line: 5, column: 5)
!21 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!22 = !DILocation(line: 5, column: 14, scope: !20)
!23 = !DILocation(line: 5, column: 10, scope: !20)
!24 = !DILocation(line: 5, column: 22, scope: !25)
!25 = distinct !DILexicalBlock(scope: !20, file: !16, line: 5, column: 5)
!26 = !DILocation(line: 5, column: 25, scope: !25)
!27 = !DILocation(line: 5, column: 5, scope: !20)
!28 = !DILocalVariable(name: "i", scope: !29, file: !16, line: 6, type: !31)
!29 = distinct !DILexicalBlock(scope: !30, file: !16, line: 6, column: 9)
!30 = distinct !DILexicalBlock(scope: !25, file: !16, line: 5, column: 45)
!31 = !DIBasicType(name: "long", size: 64, encoding: DW_ATE_signed)
!32 = !DILocation(line: 6, column: 19, scope: !29)
!33 = !DILocation(line: 6, column: 14, scope: !29)
!34 = !DILocation(line: 6, column: 26, scope: !35)
!35 = distinct !DILexicalBlock(scope: !29, file: !16, line: 6, column: 9)
!36 = !DILocation(line: 6, column: 28, scope: !35)
!37 = !DILocation(line: 6, column: 9, scope: !29)
!38 = !DILocation(line: 7, column: 25, scope: !39)
!39 = distinct !DILexicalBlock(scope: !35, file: !16, line: 6, column: 43)
!40 = !DILocation(line: 7, column: 27, scope: !39)
!41 = !DILocation(line: 7, column: 30, scope: !39)
!42 = !DILocation(line: 7, column: 36, scope: !39)
!43 = !DILocation(line: 7, column: 38, scope: !39)
!44 = !DILocation(line: 7, column: 13, scope: !39)
!45 = !DILocation(line: 7, column: 15, scope: !39)
!46 = !DILocation(line: 7, column: 18, scope: !39)
!47 = !DILocation(line: 7, column: 22, scope: !39)
!48 = !DILocation(line: 8, column: 24, scope: !39)
!49 = !DILocation(line: 8, column: 26, scope: !39)
!50 = !DILocation(line: 8, column: 29, scope: !39)
!51 = !DILocation(line: 8, column: 35, scope: !39)
!52 = !DILocation(line: 8, column: 37, scope: !39)
!53 = !DILocation(line: 8, column: 42, scope: !39)
!54 = !DILocation(line: 8, column: 44, scope: !39)
!55 = !DILocation(line: 8, column: 40, scope: !39)
!56 = !DILocation(line: 8, column: 13, scope: !39)
!57 = !DILocation(line: 8, column: 15, scope: !39)
!58 = !DILocation(line: 8, column: 18, scope: !39)
!59 = !DILocation(line: 8, column: 22, scope: !39)
!60 = !DILocation(line: 9, column: 9, scope: !39)
!61 = !DILocation(line: 6, column: 39, scope: !35)
!62 = !DILocation(line: 6, column: 9, scope: !35)
!63 = distinct !{!63, !37, !64, !65}
!64 = !DILocation(line: 9, column: 9, scope: !29)
!65 = !{!"llvm.loop.mustprogress"}
!66 = !DILocation(line: 10, column: 15, scope: !30)
!67 = !DILocation(line: 10, column: 18, scope: !30)
!68 = !DILocation(line: 10, column: 21, scope: !30)
!69 = !DILocation(line: 10, column: 24, scope: !30)
!70 = !DILocation(line: 10, column: 27, scope: !30)
!71 = !DILocation(line: 10, column: 9, scope: !30)
!72 = !DILocation(line: 11, column: 5, scope: !30)
!73 = !DILocation(line: 5, column: 41, scope: !25)
!74 = !DILocation(line: 5, column: 5, scope: !25)
!75 = distinct !{!75, !27, !76, !65}
!76 = !DILocation(line: 11, column: 5, scope: !20)
!77 = !DILocation(line: 12, column: 5, scope: !15)
