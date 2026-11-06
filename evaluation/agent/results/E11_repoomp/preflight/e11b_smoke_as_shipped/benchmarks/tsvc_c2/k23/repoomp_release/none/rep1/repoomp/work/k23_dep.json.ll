; ModuleID = '/home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e11b_smoke/benchmarks/tsvc_c2/k23/repoomp_release/none/rep1/repoomp/work/src/k23.c'
source_filename = "/home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e11b_smoke/benchmarks/tsvc_c2/k23/repoomp_release/none/rep1/repoomp/work/src/k23.c"
target datalayout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@w = external global ptr, align 8
@c = external global ptr, align 8
@u = external global ptr, align 8
@x = external global ptr, align 8
@d = external global ptr, align 8
@v = external global ptr, align 8
@a = external global ptr, align 8
@b = external global ptr, align 8
@e = external global ptr, align 8

; Function Attrs: noinline nounwind optnone uwtable
define dso_local double @kernel_k23() #0 !dbg !15 {
  %1 = alloca i32, align 4
  %2 = alloca i64, align 8
    #dbg_declare(ptr %1, !19, !DIExpression(), !22)
  store i32 0, ptr %1, align 4, !dbg !22
  br label %3, !dbg !23

3:                                                ; preds = %50, %0
  %4 = load i32, ptr %1, align 4, !dbg !24
  %5 = icmp slt i32 %4, 48, !dbg !26
  br i1 %5, label %6, label %53, !dbg !27

6:                                                ; preds = %3
    #dbg_declare(ptr %2, !28, !DIExpression(), !32)
  store i64 1, ptr %2, align 8, !dbg !32
  br label %7, !dbg !33

7:                                                ; preds = %40, %6
  %8 = load i64, ptr %2, align 8, !dbg !34
  %9 = icmp slt i64 %8, 32000, !dbg !36
  br i1 %9, label %10, label %43, !dbg !37

10:                                               ; preds = %7
  %11 = load ptr, ptr @w, align 8, !dbg !38
  %12 = load i64, ptr %2, align 8, !dbg !40
  %13 = getelementptr inbounds double, ptr %11, i64 %12, !dbg !38
  %14 = load double, ptr %13, align 8, !dbg !38
  %15 = load ptr, ptr @c, align 8, !dbg !41
  %16 = load i64, ptr %2, align 8, !dbg !42
  %17 = getelementptr inbounds double, ptr %15, i64 %16, !dbg !41
  %18 = load double, ptr %17, align 8, !dbg !41
  %19 = load ptr, ptr @u, align 8, !dbg !43
  %20 = load i64, ptr %2, align 8, !dbg !44
  %21 = getelementptr inbounds double, ptr %19, i64 %20, !dbg !43
  %22 = load double, ptr %21, align 8, !dbg !45
  %23 = call double @llvm.fmuladd.f64(double %14, double %18, double %22), !dbg !45
  store double %23, ptr %21, align 8, !dbg !45
  %24 = load ptr, ptr @x, align 8, !dbg !46
  %25 = load i64, ptr %2, align 8, !dbg !47
  %26 = getelementptr inbounds double, ptr %24, i64 %25, !dbg !46
  %27 = load double, ptr %26, align 8, !dbg !46
  %28 = load ptr, ptr @d, align 8, !dbg !48
  %29 = load i64, ptr %2, align 8, !dbg !49
  %30 = getelementptr inbounds double, ptr %28, i64 %29, !dbg !48
  %31 = load double, ptr %30, align 8, !dbg !48
  %32 = load ptr, ptr @c, align 8, !dbg !50
  %33 = load i64, ptr %2, align 8, !dbg !51
  %34 = getelementptr inbounds double, ptr %32, i64 %33, !dbg !50
  %35 = load double, ptr %34, align 8, !dbg !50
  %36 = call double @llvm.fmuladd.f64(double %27, double %31, double %35), !dbg !52
  %37 = load ptr, ptr @v, align 8, !dbg !53
  %38 = load i64, ptr %2, align 8, !dbg !54
  %39 = getelementptr inbounds double, ptr %37, i64 %38, !dbg !53
  store double %36, ptr %39, align 8, !dbg !55
  br label %40, !dbg !56

40:                                               ; preds = %10
  %41 = load i64, ptr %2, align 8, !dbg !57
  %42 = add nsw i64 %41, 1, !dbg !57
  store i64 %42, ptr %2, align 8, !dbg !57
  br label %7, !dbg !58, !llvm.loop !59

43:                                               ; preds = %7
  %44 = load ptr, ptr @a, align 8, !dbg !62
  %45 = load ptr, ptr @b, align 8, !dbg !63
  %46 = load ptr, ptr @c, align 8, !dbg !64
  %47 = load ptr, ptr @d, align 8, !dbg !65
  %48 = load ptr, ptr @e, align 8, !dbg !66
  %49 = call i32 @dummy(ptr noundef %44, ptr noundef %45, ptr noundef %46, ptr noundef %47, ptr noundef %48), !dbg !67
  br label %50, !dbg !68

50:                                               ; preds = %43
  %51 = load i32, ptr %1, align 4, !dbg !69
  %52 = add nsw i32 %51, 1, !dbg !69
  store i32 %52, ptr %1, align 4, !dbg !69
  br label %3, !dbg !70, !llvm.loop !71

53:                                               ; preds = %3
  ret double 0.000000e+00, !dbg !73
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
!1 = !DIFile(filename: "/home/ahmedabosamaha/discopop_agent/evaluation/agent/runs/e11b_smoke/benchmarks/tsvc_c2/k23/repoomp_release/none/rep1/repoomp/work/src/k23.c", directory: "/home/ahmedabosamaha/discopop_agent/evaluation/benchmarks/RepoOMP/Method", checksumkind: CSK_MD5, checksum: "13156bc28a2511bc4db3908de75eb092")
!2 = !{!3}
!3 = !DIDerivedType(tag: DW_TAG_typedef, name: "real_t", file: !4, line: 25, baseType: !5)
!4 = !DIFile(filename: "agent/runs/e11b_smoke/benchmarks/tsvc_c2/k23/repoomp_release/none/rep1/repoomp/work/src/data.h", directory: "/home/ahmedabosamaha/discopop_agent/evaluation", checksumkind: CSK_MD5, checksum: "30a4de122b6da7f884f4bcb64e18d8e7")
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
!15 = distinct !DISubprogram(name: "kernel_k23", scope: !16, file: !16, line: 3, type: !17, scopeLine: 4, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !0, retainedNodes: !18)
!16 = !DIFile(filename: "agent/runs/e11b_smoke/benchmarks/tsvc_c2/k23/repoomp_release/none/rep1/repoomp/work/src/k23.c", directory: "/home/ahmedabosamaha/discopop_agent/evaluation", checksumkind: CSK_MD5, checksum: "13156bc28a2511bc4db3908de75eb092")
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
!38 = !DILocation(line: 7, column: 21, scope: !39)
!39 = distinct !DILexicalBlock(scope: !35, file: !16, line: 6, column: 43)
!40 = !DILocation(line: 7, column: 23, scope: !39)
!41 = !DILocation(line: 7, column: 28, scope: !39)
!42 = !DILocation(line: 7, column: 30, scope: !39)
!43 = !DILocation(line: 7, column: 13, scope: !39)
!44 = !DILocation(line: 7, column: 15, scope: !39)
!45 = !DILocation(line: 7, column: 18, scope: !39)
!46 = !DILocation(line: 8, column: 20, scope: !39)
!47 = !DILocation(line: 8, column: 22, scope: !39)
!48 = !DILocation(line: 8, column: 27, scope: !39)
!49 = !DILocation(line: 8, column: 29, scope: !39)
!50 = !DILocation(line: 8, column: 34, scope: !39)
!51 = !DILocation(line: 8, column: 36, scope: !39)
!52 = !DILocation(line: 8, column: 32, scope: !39)
!53 = !DILocation(line: 8, column: 13, scope: !39)
!54 = !DILocation(line: 8, column: 15, scope: !39)
!55 = !DILocation(line: 8, column: 18, scope: !39)
!56 = !DILocation(line: 9, column: 9, scope: !39)
!57 = !DILocation(line: 6, column: 39, scope: !35)
!58 = !DILocation(line: 6, column: 9, scope: !35)
!59 = distinct !{!59, !37, !60, !61}
!60 = !DILocation(line: 9, column: 9, scope: !29)
!61 = !{!"llvm.loop.mustprogress"}
!62 = !DILocation(line: 10, column: 15, scope: !30)
!63 = !DILocation(line: 10, column: 18, scope: !30)
!64 = !DILocation(line: 10, column: 21, scope: !30)
!65 = !DILocation(line: 10, column: 24, scope: !30)
!66 = !DILocation(line: 10, column: 27, scope: !30)
!67 = !DILocation(line: 10, column: 9, scope: !30)
!68 = !DILocation(line: 11, column: 5, scope: !30)
!69 = !DILocation(line: 5, column: 41, scope: !25)
!70 = !DILocation(line: 5, column: 5, scope: !25)
!71 = distinct !{!71, !27, !72, !61}
!72 = !DILocation(line: 11, column: 5, scope: !20)
!73 = !DILocation(line: 12, column: 5, scope: !15)
