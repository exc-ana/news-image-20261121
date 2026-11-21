[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/exc-ana/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/exc-ana/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

# Sum up 21 November's world news in one image

Entry for the make.fun bounty
[Sum up 21 November's world news in one image](https://make.fun/bounty/news-image-20261121)
— a program that draws one broadsheet-style image of Saturday 21 November 2026.

## How it works

`main.py` (Python 3 standard library only) draws the whole image itself — a small
raster canvas, a stroke font, simple pictograms and three hero scenes — and encodes
the PNG by hand. It writes `/output/entry.png` (or `$MAKEFUN_OUTPUT_DIR/entry.png`).

```sh
python3 main.py
```

## The image

- Masthead "THE SATURDAY GLOBE" and giant date headline "SATURDAY 21 NOVEMBER 2026"
- Three hero stories: Russian missile lands in Poland; COP31 passes its deadline with
  no fossil-fuel deal; Wall Street slides into correction
- 37 more numbered stories (40 total), from the ICJ's Myanmar genocide ruling to
  KL Rahul's SENA set, with a DATE CHECK footer naming the sources
- Output: 1024 x 1024 PNG, 50,497 bytes,
  SHA-256 `2662c2a6c7a6f9c9982d297df838c89a15d05e0330eee0b6032a4e177e9e174c`
- Deterministic: two independent runs write byte-identical output

## License

MIT
