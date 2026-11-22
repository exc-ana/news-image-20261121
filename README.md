[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/exc-ana/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/exc-ana/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

# Sum up 21 November's world news in one image

Entry for the make.fun bounty
[Sum up 21 November's world news in one image](https://make.fun/bounty/news-image-20261121)
— a program that draws one broadsheet-style image of Saturday 21 November 2026.

This is the v2 refresh of the entry: rebuilt from scratch with the full
day's news as reported on Saturday afternoon (COP31 still in overtime,
Poland aftermath, Wall Street's Friday close, Anthropic's claimed Riemann
proof), replacing the morning-only v1.

## How it works

`main.py` (Python 3 standard library only) draws the whole image itself — a small
raster canvas, a bitmap font, simple pictograms and three hero scenes — and encodes
the PNG by hand. It writes `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`).

```sh
python3 main.py
```

## The image

- Masthead "THE SATURDAY GLOBE" and giant date headline "SATURDAY 21 NOVEMBER 2026"
- Three hero stories: Russian missiles land in Poland; COP31 runs into overtime
  with no fossil-fuel deal; Wall Street slides into correction
- 37 more numbered stories (40 total), from the ICJ's Myanmar genocide ruling to
  KL Rahul's SENA set, with a DATE CHECK footer naming the sources
- Output: 1024 x 1024 PNG, 40,682 bytes,
  SHA-256 `52345520bdbfd64a5562012ade69198b62d285bcb3f1b20b4e4f9c05a998a966`
- Deterministic: two independent runs write byte-identical output

## License

MIT
