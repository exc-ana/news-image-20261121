# BUILD NOTES — News-image 21 November 2026, v2 refresh

- **Bounty:** Sum up 21 November's world news in one image
- **Slug:** `news-image-20261121`
- **Bounty page:** https://make.fun/bounty/news-image-20261121
- **Kit:** same kit as v1 (`../kit/news-image-20261121-kit/`, bundle SHA-256
  `35b3239e3a19cc1d41b80cba8e3f8e629534e23997d93ec2df2750ff3f1d24f4`)
- **Prize:** $100 total — 1st $20, 2nd $12, 3rd $6, 4th–10th $2, 11th–50th $1.20
- **Deadline:** Mon 23 Nov 2026 07:00 WIB (2026-11-23T00:00:00Z)
- **Quota:** this is entry #2 of ~3 allowed for this bounty. Do NOT plan a v3.

## Why a v2

- v1 "Hale Prism" (submitted 21 Nov 12:14 WIB) scores provisional **96.4993%
  (#2,094 of 4,205 placed)**; prize zone needs ~98.7%, leader @samatch-we
  99.1923%. v1 was built from morning news only (~11:45 WIB).
- v2 refreshes the day with the afternoon's developments, researched fresh
  by web search on Sat 21 Nov ~14:35–15:30 WIB: COP31 still in overtime
  (plenary suspended 22:29 Fri, third draft due Sat, COP32 to Addis Ababa),
  Poland aftermath (Rutte due in Warsaw Sat, Warsaw seeks more NATO air
  defence), Wall Street Friday close in full (S&P 500 −3.7%, Nasdaq −5.3%,
  Nvidia −14% on SEC probe, Anthropic −8.5%), Anthropic's claimed Riemann
  proof, Cyclone Akvan weakening to a low, plus the day's sports and
  politics (KL Rahul SENA tons, Kane injury, Wales beating the All Blacks,
  UK–EU deals, GTA VI $3.8bn first day).

## Entry

- **Program:** `main.py` (521 lines), Python 3 stdlib only, written entirely
  from scratch in this session. The v1 entry code (`../main.py`) was NOT
  opened or read. Only the official kit (rules/schema) and the v1 README
  badge block were consulted. It draws everything itself: a hand-rolled
  raster canvas, a 5x7 bitmap font defined in the file, simple pictograms,
  three self-drawn hero scenes, and a hand-written PNG encoder (zlib +
  struct).
- **Output:** `/output/entry.png` (grading path; never written into the repo
  folder). Also honours `MAKEFUN_OUTPUT_DIR` for local runs.
- **Layout (1024 x 1024):** navy masthead "THE SATURDAY GLOBE", giant date
  headline "SATURDAY 21 NOVEMBER 2026", three hero panels (Russian missiles
  in Poland; COP31 overtime with no fossil-fuel deal; Wall Street correction
  chart), 37 numbered story cards in a 4-column grid (stories 4–40), and a
  navy DATE CHECK footer with sources. 40 stories in total.

## Stories (all reported Saturday 21 November 2026)

Heroes: 1. Russian missiles land in Poland (2 Kh-101 + drone; Tusk:
deliberate provocation; Rutte: grave violation, due in Warsaw Sat).
2. COP31 runs into overtime with no deal (draft drops fossil fuels and the
$120bn adaptation target; third draft due Sat; COP32 Addis Ababa 2027).
3. Wall Street rout — S&P 500 in correction (Fri −3.7%, 7th straight loss;
Nasdaq −5.3%, wipes 2026 gains; Nvidia −14% on SEC probe; Anthropic −8.5%).

Cards 4–40: Russia's 400-drone/110-missile strike on Ukraine (8 killed in
Kyiv); ICJ finds Myanmar guilty of Rohingya genocide 9–6 (first state
ever); Anthropic mathematician claims Claude solved the Riemann hypothesis
(presented as a claim, experts urge caution); Anthropic shares −8.5% to
$88.91 (−$109bn); Nvidia −14%; Cyclone Akvan fades to a low over Odisha
(300,000 evacuated); 6.8 Peru quake (Fri evening, reported Sat, no deaths);
UK–EU post-Brexit deals; Saudi coalition intercepts 3 Houthi missiles aimed
at Riyadh; daraxonrasib pancreatic-cancer pill trial (tumours undetectable
in 1 in 12); Gen Z protests in 25 European countries; FBI criminal database
reportedly hacked; Palisades fire arson conviction; 2 Salvadoran soldiers
killed in Haiti; Gaza strikes / West Bank violence; Spain heads to 29 Nov
election; NASA halts Perseverance & Mars Odyssey science; Bitcoin toward
$62,000, $2bn+ crypto liquidations; GTA VI $3.8bn first-day sales; Mamdani
to close Rikers by 2032; Denmark expels Russian diplomat over assassination
plot; ~600 women killed in South Africa in 3 months; US declassifies more
UFO footage; Bolsonaro hospitalised; NFL suspends Puka Nacua; Trump calls
Putin "my friend" / Zelenskyy: Putin is a "killer"; Trump threatens tax on
overseas data centres; KL Rahul's SENA Test-ton quartet; Harry Kane ankle
ligament tear; Wales beat All Blacks first time in 73 years; Pakistan beat
Sri Lanka (first Test series win in 2 years); Harden 51 / Cunningham 50
(NBA); Drake Maye season-ending fibula fracture; Andreeva wins WTA Finals,
ATP Finals semis; Bangladesh PM blames India/Awami League; Iraq arrests 8
oil officials, retakes Jurf al-Sakhar; ANC fights to hold South Africa's
key cities.

Sources: AP, Reuters, BBC, AFP, UN News, IMD, IANS, WSJ, CNN, Investopedia,
The Hindu BusinessLine, The Times, Le Monde, Motley Fool, TradingView.
Friday-evening events (Peru quake, Wall Street close, ICJ reaction) are
included only as reported in Saturday's news; the footer says so.

## Verification (local, 21 Nov 2026 ~15:45 WIB)

- **Determinism: PASS.** Two independent runs (fresh output dirs) wrote
  byte-identical output.
- **Output:** 40,682 bytes (limit 1,048,576), 1024 x 1024 px (limit
  1024 x 1024), valid PNG (magic bytes + all chunk CRCs verified).
- **SHA-256:** `52345520bdbfd64a5562012ade69198b62d285bcb3f1b20b4e4f9c05a998a966`
- **Text-fit check: PASS.** Programmatic wrap check: every card headline
  fits in 3 lines and every hero caption in 5 lines at the drawn scales;
  no text is truncated.
- **Visual check:** full image inspected, plus crops of all 3 heroes, the
  grid and the footer. Four layout defects found and fixed in-session:
  (1) card headlines truncated to 3 lines with content lost — fixed by
  shortening headlines and dropping headline scale 1.35 → 1.25;
  (2) hero captions truncated at 4 lines — fixed by allowing 5 lines at
  scale 1.1 and shortening the Poland caption; (3) COP31 "1.5C" label struck
  through by the red banner and thermometer bulb overlapping it — label
  removed, thermometer shortened to clear the banner; (4) markets chart line
  struck through the "-3.7%" label and "NASDAQ -5.3%" sat on red bars —
  chart moved down, NASDAQ label removed; (5) footer sources line clipped
  at the bottom edge — footer lines re-spaced. Final render re-verified
  after all fixes.
- **Kit check/grader:** the kit ships NO local grader — RULES.txt states
  "There is no local grade of this competition: the server grades every
  entry". The CLI `makefun check` requires `--repo` and `--transcripts`,
  which do not exist yet (separate later steps), so it was not run. Gate
  rules were checked locally instead (format, size, dimensions,
  determinism, output path).

## Known minor defects

- The bitmap font is blocky at masthead scale; legible, but less elegant
  than a stroke font.
- Hero 1's missile trail is a simple two-line streak; the explosion burst
  sits close to the Polish flag pole.
- Card text is small (headline ~9 px glyphs) — readable at full size, but
  the judge viewing at ~300 px across will rely mostly on the heroes and
  the date headline.

## Still open (SEPARATE later steps — NOT done here)

1. Transcript bundle (`makefun bundle`) from the real build session.
2. Public GitHub repo `news-image-20261121` under exc-ana — NOTE: v1 already
   used that repo name; a v2 repo needs a distinct name (e.g.
   `news-image-20261121-v2`) or a new commit on a separate repo. main.py +
   LICENSE + README with bounty badges + `.makefun/owner.json`, created
   after the competition opened. `kit/` must NOT be committed.
3. `makefun check --kit . --repo <repo> --transcripts transcripts.tar.gz` —
   must pass, especially `thinking_reproduces` (main.py was written in this
   session in several write/edit turns, so authored coverage should hold).
4. Submit before Mon 23 Nov 07:00 WIB. This bounty has escrow, so the
   submission needs a signature from the linked agent wallet (API key) —
   payout wallet handling per Bos's standing rules. This would be entry #2
   for this bounty; the live entry remains v1 "Hale Prism" until v2 is
   submitted.

## Files in this folder

- `main.py` — the entry program (the only file that goes to the repo, plus LICENSE/README)
- `BUILD-NOTES-V2.md` — this file
- `README.md` — draft repo README (badges to be verified at the submitted commit)
