# BUILD NOTES — Sum up 21 November's world news in one image

- **Bounty:** Sum up 21 November's world news in one image
- **Slug:** `news-image-20261121`
- **Bounty page:** https://make.fun/bounty/news-image-20261121
- **Kit:** https://make.fun/c/news-image-20261121/kit (downloaded 21 Nov 2026 ~11:36 WIB,
  `kit/news-image-20261121-kit/`, bundle SHA-256
  `35b3239e3a19cc1d41b80cba8e3f8e629534e23997d93ec2df2750ff3f1d24f4`)
- **Prize:** $100 total — 1st $20, 2nd $12, 3rd $6, 4th–10th $2, 11th–50th $1.20
- **Deadline:** Mon 23 Nov 2026 07:00 WIB (2026-11-23T00:00:00Z)
- **Field (per brief):** 2,816 agents; leaders tied ~99.1% (@kuda, @samatch-we)
- **Escrow:** reward locked in make.fun escrow at open (competition.yaml `escrow: at_open`),
  so a submission will need a signature from a linked Solana wallet at submit time.

## Entry

- **Program:** `main.py` (678 lines), Python 3 stdlib only, written from scratch in this
  session. No earlier news-image entry was opened or read. It draws everything itself:
  a hand-rolled raster canvas, a stroke font defined in the file, simple pictograms,
  three self-drawn hero scenes, and a hand-written PNG encoder (zlib + struct).
- **Output:** `/output/entry.png` (grading path; never written into the repo folder).
  Also honours `MAKEFUN_OUTPUT_DIR` for local runs.
- **Layout (1024 x 1024):** navy masthead "THE SATURDAY GLOBE", giant date headline
  "SATURDAY 21 NOVEMBER 2026", three hero panels (Russian missile in Poland; COP31
  overtime with the fossil-fuels draft; Wall Street correction chart), 37 numbered
  story cards in a 4-column grid (stories 4–40), and a navy DATE CHECK footer with
  sources. 40 stories in total.
- **Research:** real 21 Nov 2026 news, verified by web search 21 Nov 11:36–11:45 WIB
  (AP/Reuters/BBC/AFP/Xinhua digests and the day's briefings). Every story was reported
  on Saturday 21 November 2026; where an event happened on Friday evening (Peru quake,
  Wall Street close, ICJ ruling) it is included as reported in Saturday's news, and the
  footer says "reported on Saturday 21 November 2026" rather than claiming all events
  occurred that day.

## Verification (local, 21 Nov 2026 ~11:47 WIB)

- **Determinism: PASS.** Two independent runs (fresh output dirs) wrote byte-identical
  output.
- **Output:** 50,497 bytes (limit 1,048,576), 1024 x 1024 px (limit 1024 x 1024),
  valid PNG (magic bytes + all chunk CRCs verified).
- **SHA-256:** `2662c2a6c7a6f9c9982d297df838c89a15d05e0330eee0b6032a4e177e9e174c`
- **Visual check:** full image inspected — masthead, date headline, 3 hero scenes and
  all 40 numbered cards legible; two layout defects found and fixed in-session
  (market tick labels struck through by the chart line; a misleading "SEE INDEX BELOW"
  label; chart's final segment rising). Final render re-verified after the fixes.
- **Kit check/grader:** the kit ships NO local grader — RULES.txt states "There is no
  local grade of this competition: the server grades every entry". The CLI
  `makefun check` requires `--repo` and `--transcripts`, which do not exist yet
  (separate later steps), so it was not run. Gate rules were checked locally instead
  (format, size, dimensions, determinism, output path).

## Still open (SEPARATE later steps — NOT done here)

1. Transcript bundle (`makefun bundle`) from the real build session.
2. Public GitHub repo `news-image-20261121` under exc-ana (main.py + LICENSE + README
   with bounty badges + `.makefun/owner.json`), created after the competition opened.
   NOTE: `kit/` in this folder must NOT be committed.
3. `makefun check --kit . --repo <repo> --transcripts transcripts.tar.gz` — must pass,
   especially `thinking_reproduces` (main.py was written in this session in several
   write/edit turns, so authored coverage should hold).
4. Submit before Mon 23 Nov 07:00 WIB. Entry quota: at most 10 submissions/day,
   20 total. This bounty has escrow, so the submission needs a signature from the
   linked agent wallet (API key) — payout wallet handling per Bos's standing rules.
5. Optional refresh: the day is only half over at build time (11:47 WIB); a rebuild
   with the full day's news before the deadline would strengthen the entry, but the
   current entry is complete and submittable as-is.

## Files in this folder

- `main.py` — the entry program (the only file that goes to the repo, plus LICENSE/README)
- `BUILD-NOTES.md` — this file
- `README.md` — draft repo README (badges to be verified at the submitted commit)
- `kit/` — official kit (excluded from any repo)
- `kit.zip` — kit download as received
