# Test results

| Date | Commit | Scenario | Expected | Actual | Result |
|------|--------|----------|----------|--------|--------|
| 2026-10-12 | 9b877a4 | 5 stops, round trip (VROOM + Valhalla) | All 5 jobs once, none unassigned | Order [1, 4, 5, 2, 3] | PASS |
| 2026-10-12 | 9b877a4 | 5 stops, open trip | All 5 jobs once, none unassigned | Order [1, 4, 5, 2, 3] | PASS |
| 2026-10-12 | 9b877a4 | 8 stops, round trip | All 8 jobs once, none unassigned | Order [1, 4, 6, 8, 5, 2, 7, 3] | PASS |
| 2026-10-12 | 9b877a4 | 8 stops, open trip | All 8 jobs once, none unassigned | Order [1, 4, 6, 8, 5, 2, 3, 7] | PASS |
| 2026-10-12 | f4524df | POST /api/optimize, 8 stops, round trip (live engines) | 200, D1 to D8 once each | 200, order D1 D4 D6 D8 D5 D2 D7 D3, 35.236 km, 102.0 min | PASS |
| 2026-10-12 | 45cdfa6 | Browser: load example, review (real Gemini), optimize, 5 stops round trip | All 5 recognized, route lists D1 to D5 once, depot start and return | Recognized all 5, order D1 D4 D5 D2 D3, 23.5 km, 66 min | PASS |
| 2026-10-12 | 709531c | Browser: Load example, review with real Gemini, optimize, 5 stops round trip | All 5 recognized, every ID once, depot start and return | All 5 recognized, order D1 D4 D5 D2 D3, 23.5 km, 66 min | PASS |
| 2026-10-12 | 709531c | Browser: instruction 'Deliver D2 before 10am' | Notice that time constraints are not supported, optimize blocked until acknowledged | Notice shown with acknowledgement checkbox | PASS |
| 2026-10-12 | 709531c | Browser: 5 stops, open trip (return to depot unticked) | Route ends at the last stop, no return line, every ID once | No return line, order D1 D4 D5 D2 D3, 20.5 km, 57 min | PASS |
| 2026-10-12 | 709531c | Browser: 5 addresses outside the catalogue (Nagasandra, whitefield, Erode, electroniccity, Majestic) | All shown as Not supported, optimize blocked | All 5 shown as Not supported with a note per delivery, optimize button disabled | PASS |
| 2026-10-12 | 709531c | Browser: misspelled address 'Jubilei Hills' among 4 valid ones | Only that delivery flagged Not supported, optimize blocked, no guessing | D4 flagged Not supported with a note, other 4 recognized | PASS |
| 2026-10-12 | 709531c | Browser: edit the addresses after a review | Review table and any route are cleared | Table disappeared after changing one letter | PASS |
| 2026-10-12 | 709531c | Browser: Review when the Gemini quota is reached | Readable error shown, no key or stack trace | 'The language model quota was reached. Try again later.' shown | PASS |
| 2026-10-12 | 709531c | Browser: 8 stops, open trip, real Gemini extraction | All 8 recognized, every ID once | All 8 recognized, order D1 D4 D6 D8 D5 D2 D3 D7, 29.5 km, 87 min | PASS |
| 2026-10-12 | 709531c | Browser: Review while the backend is stopped | Readable error, no blank page | Readable error shown, page still usable | PASS |
| 2026-10-12 | f157ccf | Frontend: npm run lint | No errors | No output after eslint, no errors | PASS |
| 2026-10-12 | f157ccf | Frontend: npm run build | Build succeeds | built in 241ms, 21 modules | PASS |
| 2026-10-12 | d6769ee | Clean install: fresh clone of develop, backend install, pytest, npm ci, lint, build | Tests pass, lint and build succeed, no .env files in the repository | Backend and frontend checks passed, no .env files found | PASS |
| 2026-10-13 | b1fd1b2 | Browser (model simulated, stub mode): shortened place names for geocoded stops | Short names shown, full name in tooltip, approximate label kept | Short names shown in review and route, approximate labels kept | PASS |
| 2026-10-14 | b1fd1b2 | Browser, real model (gemini-3.5-flash-lite): Madhapur, Hitec City Metro Station, Charminar, round trip | One catalogue and two geocoded stops, each once, approximate labels, no simulated-model note | All three stops once, geocoded ones marked approximate, 42.7 km, 93 min | PASS |
