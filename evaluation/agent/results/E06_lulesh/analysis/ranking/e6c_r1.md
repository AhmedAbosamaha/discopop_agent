# Queue without the measurement vs the agent's queue — `server: runs/e6c_r1/profiles/llnl_c1/lulesh (the five input files copied to the Mac, 3 Nov)`

Inputs (sha256): `FileMapping.txt` 92e8e5b28884, `profiler/Data.xml` 452d7dfd128d, `profiler/dynamic_dependencies.txt` a7e4c0c4d297, `profiler/loop_counter_output.txt` dbbbec6cc4ed, `explorer/patterns.json` e627736dc4b8

Flags taken from `runs/e6c_r1/benchmarks/llnl_c1/lulesh/llm_pragmas_v5/claude-haiku-4-5-20251001/rep1/trial.json`: editable `lulesh.cc`, --min-runtime-share 0.01 (inert without the measurement), 23 excluded functions.

Proxy queue: 100 regions.  Measured queue of `e6c_r1/rep1`: 44 regions.  Measured queue of `e6c_r1/rep2`: 44 regions.

| proxy # | region | type | lines | tier | pattern | W | proxy score | % run | measured # (e6c_r1/rep1) | measured # (e6c_r1/rep2) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 1:3209  | loop | 1504–1517 | 1 | do_all | 48553050 | 25.53 | 2.7 | 32 | 32 |
| 2 | 1:3132  | loop | 1585–1616 | 1 | do_all | 38593450 | 25.20 |  | — | — |
| 3 | 1:2052  | loop | 512–564 | 1 | do_all | 35100000 | 25.06 |  | — | — |
| 4 | 1:3099  | loop | 1546–1568 | 1 | do_all | 27388900 | 24.71 |  | — | — |
| 5 | 1:2046  | loop | 500–644 | 1 | do_all | 24300000 | 24.53 | 13.5 | 15 | 15 |
| 6 | 1:2532  | loop | 1155–1286 | 1 | do_all | 22106250 | 24.40 | 13.3 | 19 | 19 |
| 7 | 1:3160  | loop | 1621–1638 | 1 | do_all | 21164150 | 24.34 |  | — | — |
| 8 | 1:3203  | loop | 1498–1502 | 1 | do_all | 14939400 | 23.83 |  | — | — |
| 9 | 1:3117  | loop | 1570–1580 | 1 | do_all | 12449500 | 23.57 |  | — | — |
| 10 | 1:1961  | loop | 670–679 | 1 | do_all | 12150000 | 23.53 |  | — | — |
| 11 | 1:2977  | loop | 1698–1706 | 1 | do_all | 9959600 | 23.25 | 10.5 | 21 | 21 |
| 12 | 1:3014  | loop | 1725–1732 | 1 | do_all | 8714650 | 23.06 |  | — | — |
| 13 | 1:3087  | loop | 1534–1541 | 1 | do_all | 8714650 | 23.06 |  | — | — |
| 14 | 1:118  | loop | 1066–1117 | 1 | do_all | 8606250 | 23.04 | 16.0 | 13 | 13 |
| 15 | 1:142  | loop | 1092–1098 | 1 | do_all | 8100000 | 22.95 | 5.8 | 23 | 23 |
| 16 | 1:2995  | loop | 1708–1714 | 1 | do_all | 7469700 | 22.83 |  | — | — |
| 17 | 1:155  | loop | 1101–1106 | 1 | do_all | 6750000 | 22.69 |  | — | — |
| 18 | 1:1918  | loop | 332–337 | 1 | do_all | 6750000 | 22.69 | 5.8 | 24 | 24 |
| 19 | 1:3004  | loop | 1717–1722 | 1 | do_all | 6224750 | 22.57 |  | — | — |
| 20 | 1:1998  | loop | 246–250 | 1 | do_all | 5400000 | 22.36 |  | — | — |
| 21 | 1:2018  | loop | 296–300 | 1 | do_all | 5400000 | 22.36 |  | — | — |
| 22 | 1:2227  | loop | 427–431 | 1 | do_all | 5400000 | 22.36 |  | — | — |
| 23 | 1:2247  | loop | 438–442 | 1 | do_all | 5400000 | 22.36 |  | — | — |
| 24 | 1:2267  | loop | 449–453 | 1 | do_all | 5400000 | 22.36 |  | — | — |
| 25 | 1:1905  | loop | 313–339 | 1 | do_all | 4387500 | 22.06 | 13.4 | 17 | 17 |
| 26 | 1:1952  | loop | 661–686 | 1 | do_all | 4218750 | 22.01 | 8.2 | 22 | 22 |
| 27 | 1:2215  | loop | 421–426 | 1 | do_all | 3375000 | 21.69 |  | — | — |
| 28 | 1:2235  | loop | 432–437 | 1 | do_all | 3375000 | 21.69 |  | — | — |
| 29 | 1:2255  | loop | 443–448 | 1 | do_all | 3375000 | 21.69 |  | — | — |
| 30 | 1:1774  | loop | 790–805 | 1 | do_all | 3072000 | 21.55 | 3.0 | 30 | 30 |
| 31 | 1:3023  | loop | 1735–1737 | 1 | do_all | 2489900 | 21.25 |  | — | — |
| 32 | 1:2312  | loop | 1131–1145 | 1 | do_all | 2362500 | 21.17 | 1.2 | 43 | 43 |
| 33 | 1:2422  | loop | 1804–1817 | 1 | do_all | 2193750 | 21.06 |  | — | — |
| 34 | 1:3185  | loop | 1652–1663 | 1 | do_all | 1856250 | 20.82 |  | — | — |
| 35 | 1:2476  | loop | 1842–1849 | 1 | do_all | 1181250 | 20.17 |  | — | — |
| 36 | 1:1818  | loop | 811–816 | 1 | do_all | 1024000 | 19.97 | 1.7 | 36 | 36 |
| 37 | 1:2369  | loop | 1477–1482 | 1 | do_all | 843750 | 19.69 |  | — | — |
| 38 | 1:3032  | loop | 1747–1752 | 1 | do_all | 843750 | 19.69 |  | — | — |
| 39 | 1:1689  | loop | 740–744 | 1 | do_all | 819200 | 19.64 |  | — | — |
| 40 | 1:1705  | loop | 754–758 | 1 | do_all | 819200 | 19.64 | 2.6 | 34 | 34 |
| 41 | 1:1870  | loop | 721–725 | 1 | do_all | 675000 | 19.36 |  | — | — |
| 42 | 1:2405  | loop | 1791–1794 | 1 | do_all | 506250 | 18.95 |  | — | — |
| 43 | 1:2414  | loop | 1798–1801 | 1 | do_all | 506250 | 18.95 |  | — | — |
| 44 | 1:1893  | loop | 114–116 | 1 | do_all | 337500 | 18.36 |  | — | — |
| 45 | 1:2397  | loop | 1786–1788 | 1 | do_all | 337500 | 18.36 |  | — | — |
| 46 | 1:2974  | loop | 1696–1745 | 1 | do_all | 85750 | 16.39 | 16.2 | 11 | 11 |
| 47 | 1:1738  | loop | 769–770 | 1 | do_all | 12800 | 13.64 |  | — | — |
| 48 | 1:1750  | loop | 774–775 | 1 | do_all | 12800 | 13.64 |  | — | — |
| 49 | 1:1762  | loop | 779–780 | 1 | do_all | 12800 | 13.64 |  | — | — |
| 50 | 1:2735  | loop | 1298–1441 | 2 |  | 24131250 | 6.36 | 5.0 | 27 | 27 |
| 51 | 1:3227  | loop | 1877–1896 | 2 |  | 3206250 | 5.48 | 1.3 | 41 | 41 |
| 52 | 1:3270  | loop | 1913–1924 | 2 |  | 1856250 | 5.25 |  | — | — |
| 53 | 1:2440  | loop | 1820–1831 | 2 |  | 6050 | 2.77 | 17.2 | 10 | 10 |
| 54 | 1:396  | loop | 1939–1949 | 2 |  | 5500 | 2.73 | 1.6 | 39 | 39 |
| 55 | 1:2680  | loop | 1449–1453 | 2 |  | 2200 | 2.33 | 5.0 | 26 | 26 |
| 56 | 1:2033  | cu | 381–413 | 2 |  | 489 | 1.68 |  | — | — |
| 57 | 1:2588  | cu | 1225–1237 | 2 |  | 156 | 1.19 |  | — | — |
| 58 | 1:296  | cu | 148–158 | 2 |  | 152 | 1.18 |  | — | — |
| 59 | 1:110  | cu | 856–904 | 2 |  | 145 | 1.16 |  | — | — |
| 60 | 1:1932 _ZL28CalcHourglassControlForElemsR6DomainPdd | function | 649–701 | 1 | task | 0 | 0.00 | 21.7 | 6 | 6 |
| 61 | 1:2031 _ZL24CalcElemVolumeDerivativePdS_S_PKdS1_S1_ | function | 374–413 | 1 | task | 0 | 0.00 | 1.1 | 44 | 44 |
| 62 | 1:1728 _ZL43ApplyAccelerationBoundaryConditionsForNodesR6Domain | function | 762–783 | 1 | task | 0 | 0.00 |  | — | — |
| 63 | 1:362 _ZL13LagrangeNodalR6Domain | function | 820–839 | 1 | task | 0 | 0.00 | 43.9 | 3 | 3 |
| 64 | 1:377 _ZL16LagrangeElementsR6Domaini | function | 1856–1866 | 1 | task | 0 | 0.00 | 54.1 | 2 | 2 |
| 65 | 1:2383 _ZL31ApplyMaterialPropertiesForElemsR6Domain | function | 1829–1835 | 1 | task | 0 | 0.00 |  | — | — |
| 66 | 1:2042 _ZL28CalcFBHourglassForceForElemsR6DomainPdS1_S1_S1_S1_S1_S1_dii | function | 457–646 | 2 |  | 0 | -1.00 | 13.5 | 16 | 16 |
| 67 | 2:2723 _ZL28CalcMonotonicQRegionForElemsR6Domainid | function | 1290–1442 | 2 |  | 0 | -1.00 | 5.0 | 29 | 29 |
| 68 | 2:2526 _ZL31CalcMonotonicQGradientsForElemsR6Domain | function | 1151–1287 | 2 |  | 0 | -1.00 | 13.3 | 20 | 20 |
| 69 | 2:3081 _ZL18CalcEnergyForElemsPdS_S_S_S_S_S_S_S_S_S_S_S_dddddS_S_ddiPi | function | 1521–1642 | 2 |  | 0 | -1.00 | 5.6 | 25 | 25 |
| 70 | 2:2924 _ZL15EvalEOSForElemsR6DomainPdiPii | function | 1667–1773 | 2 |  | 0 | -1.00 | 17.1 | 12 | 12 |
| 71 | 1:108 _ZL14CalcElemVolumedddddddddddddddddddddddd | function | 843–924 | 2 |  | 0 | -1.00 |  | — | — |
| 72 | 2:293 _ZL32CalcElemShapeFunctionDerivativesPKdS0_S0_PA8_dPd | function | 120–200 | 2 |  | 0 | -1.00 |  | — | — |
| 73 | 1:331 _ZL24CalcElemVelocityGradientPKdS0_S0_PA8_S_dPd | function | 1000–1060 | 2 |  | 0 | -1.00 |  | — | — |
| 74 | 1:115 _Z22CalcKinematicsForElemsR6Domaindi | function | 1062–1118 | 2 |  | 0 | -1.00 | 16.0 | 14 | 14 |
| 75 | 2:1995 _ZL19CalcElemNodeNormalsPdS_S_PKdS1_S1_ | function | 239–287 | 2 |  | 0 | -1.00 |  | — | — |
| 76 | 2:178 _ZL29CollectDomainNodesToElemNodesR6DomainPKiPdS3_S3_ | function | 64–106 | 2 |  | 0 | -1.00 | 17.3 | 8 | 8 |
| 77 | 2:246 _ZL28CalcElemCharacteristicLengthPKdS0_S0_d | function | 957–996 | 2 |  | 0 | -1.00 | 1.6 | 38 | 38 |
| 78 | 2:2212 _ZL24CalcElemFBHourglassForcePdS_S_PA4_ddS_S_S_ | function | 416–454 | 2 |  | 0 | -1.00 |  | — | — |
| 79 | 1:1902 _ZL23IntegrateStressForElemsR6DomainPdS1_S1_S1_ii | function | 304–341 | 2 |  | 0 | -1.00 | 13.4 | 18 | 18 |
| 80 | 1:2023 _ZL17SumElemFaceNormalPdS_S_S_S_S_S_S_S_S_S_S_dddddddddddd | function | 203–236 | 2 |  | 0 | -1.00 |  | — | — |
| 81 | 1:3223 _ZL29CalcCourantConstraintForElemsR6DomainiPidRd | function | 1869–1902 | 2 |  | 0 | -1.00 | 1.3 | 42 | 42 |
| 82 | 1:2340 _ZL13CalcQForElemsR6Domain | function | 1457–1488 | 2 |  | 0 | -1.00 | 18.6 | 7 | 7 |
| 83 | 2:1847 _ZL23CalcVolumeForceForElemsR6Domain | function | 705–734 | 2 |  | 0 | -1.00 | 35.6 | 5 | 5 |
| 84 | 1:2202 _ZL7VoluDerddddddddddddddddddPdS_S_ | function | 344–371 | 2 |  | 0 | -1.00 |  | — | — |
| 85 | 2:2299 _ZL20CalcLagrangeElementsR6Domain | function | 1121–1148 | 2 |  | 0 | -1.00 | 17.2 | 9 | 9 |
| 86 | 1:3200 _ZL20CalcPressureForElemsPdS_S_S_S_S_dddiPi | function | 1491–1518 | 2 |  | 0 | -1.00 | 2.7 | 33 | 33 |
| 87 | 2:3266 _ZL27CalcHydroConstraintForElemsR6DomainiPidRd | function | 1907–1930 | 2 |  | 0 | -1.00 |  | — | — |
| 88 | 1:1771 _ZL20CalcVelocityForNodesR6Domainddi | function | 786–806 | 2 |  | 0 | -1.00 | 3.0 | 31 | 31 |
| 89 | 2:1671 _ZL8AreaFacedddddddddddd | function | 935–953 | 2 |  | 0 | -1.00 |  | — | — |
| 90 | 1:3182 _ZL22CalcSoundSpeedForElemsR6DomainPddS1_S1_S1_S1_diPi | function | 1646–1664 | 2 |  | 0 | -1.00 |  | — | — |
| 91 | 2:388 _ZL27CalcTimeConstraintsForElemsR6Domain | function | 1934–1950 | 2 |  | 0 | -1.00 | 1.6 | 40 | 40 |
| 92 | 2:355 _Z16LagrangeLeapFrogR6Domain | function | 1952–1967 | 2 |  | 0 | -1.00 | 99.6 | 1 | 1 |
| 93 | 1:2472 _ZL21UpdateVolumesForElemsR6Domaindi | function | 1838–1852 | 2 |  | 0 | -1.00 |  | — | — |
| 94 | 2:1683 _ZL17CalcForceForNodesR6Domain | function | 736–748 | 2 |  | 0 | -1.00 | 36.4 | 4 | 4 |
| 95 | 1:2015 _ZL27SumElemStressesToNodeForcesPA8_KddddPdS2_S2_ | function | 290–301 | 2 |  | 0 | -1.00 |  | — | — |
| 96 | 1:2676 _ZL22CalcMonotonicQForElemsR6Domain | function | 1445–1454 | 2 |  | 0 | -1.00 | 5.0 | 28 | 28 |
| 97 | 1:1702 _ZL24CalcAccelerationForNodesR6Domaini | function | 751–759 | 2 |  | 0 | -1.00 | 2.6 | 35 | 35 |
| 98 | 1:1815 _ZL20CalcPositionForNodesR6Domaindi | function | 809–817 | 2 |  | 0 | -1.00 | 1.7 | 37 | 37 |
| 99 | 2:1890 _ZL23InitStressTermsForElemsR6DomainPdS1_S1_i | function | 109–117 | 2 |  | 0 | -1.00 |  | — | — |
| 100 | 2:104 _Z14CalcElemVolumePKdS0_S0_ | function | 927–931 | 2 |  | 0 | -1.00 |  | — | — |
