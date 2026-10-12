# Test results

| Date | Commit | Scenario | Expected | Actual | Result |
|------|--------|----------|----------|--------|--------|
| 2026-10-12 | 9b877a4 | 5 stops, round trip (VROOM + Valhalla) | All 5 jobs once, none unassigned | Order [1, 4, 5, 2, 3] | PASS |
| 2026-10-12 | 9b877a4 | 5 stops, open trip | All 5 jobs once, none unassigned | Order [1, 4, 5, 2, 3] | PASS |
| 2026-10-12 | 9b877a4 | 8 stops, round trip | All 8 jobs once, none unassigned | Order [1, 4, 6, 8, 5, 2, 7, 3] | PASS |
| 2026-10-12 | 9b877a4 | 8 stops, open trip | All 8 jobs once, none unassigned | Order [1, 4, 6, 8, 5, 2, 3, 7] | PASS |
| 2026-10-12 | f4524df | POST /api/optimize, 8 stops, round trip (live engines) | 200, D1 to D8 once each | 200, order D1 D4 D6 D8 D5 D2 D7 D3, 35.236 km, 102.0 min | PASS |
