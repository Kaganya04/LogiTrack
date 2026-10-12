# Test results

| Date | Commit | Scenario | Expected | Actual | Result |
|------|--------|----------|----------|--------|--------|
| 2026-10-12 | 9b877a4 | 5 stops, round trip (VROOM + Valhalla) | All 5 jobs once, none unassigned | Order [1, 4, 5, 2, 3] | PASS |
| 2026-10-12 | 9b877a4 | 5 stops, open trip | All 5 jobs once, none unassigned | Order [1, 4, 5, 2, 3] | PASS |
| 2026-10-12 | 9b877a4 | 8 stops, round trip | All 8 jobs once, none unassigned | Order [1, 4, 6, 8, 5, 2, 7, 3] | PASS |
| 2026-10-12 | 9b877a4 | 8 stops, open trip | All 8 jobs once, none unassigned | Order [1, 4, 6, 8, 5, 2, 3, 7] | PASS |
