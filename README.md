# World news of Saturday 21 November 2026 — in one image

[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/parsaturky83/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/parsaturky83/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

Entry for the make.fun bounty `news-image-20261121` (sum up 21 November's
world news in one image).

## What it is

`main.py` (Python 3.13, standard library only) draws a 1024x1024 newspaper
front page — "WORLD NEWS — SATURDAY, 21 NOVEMBER 2026" — and writes it to
`/output/entry.png`. It uses an embedded 8x12 bitmap font (rasterised from
DejaVu Sans, with hand-drawn fixes for the glyphs a 8-pixel cell mangles)
and a hand-rolled PNG encoder (zlib). No network, no clock, no randomness:
two runs write byte-identical files.

Run it locally with:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Stories (all events reported on 21 November 2026)

- **Gulf crisis (lead):** Iran says its Revolutionary Guards struck two U.S.
  positions in Bahrain; Bahrain reports a fire at a civilian industrial
  site, no injuries. Tanker strikes near the Strait of Hormuz hit a
  wartime high.
- **War in Ukraine:** A Russian missile hit Kryvyi Rih, killing two and
  wounding dozens. Missiles also landed in Poland.
- **Diplomacy, Shenzhen:** Trump, Xi and Putin met at the APEC summit.
  Trump defended his Putin ties; Zelensky called Putin a "killer".
- **Mexico:** FBI most-wanted cartel boss Fausto Isidro Meza Flores was
  seized in Sinaloa; 11 died in the backlash.
- **Markets:** U.S. stocks slid into correction; the Nasdaq erased its
  2026 gains as the AI sell-off deepened.
- **Climate, COP31 Antalya:** Talks ran into overtime; the draft left out
  fossil fuels.
- **Space:** BepiColombo entered orbit around Mercury after an
  eight-year voyage.

Sources: wire-service reporting of 21 November 2026 (AP, Reuters via
syndication, Financial Times, and same-day news digests).

## Files

- `main.py` — the program (draws the image, encodes the PNG)
- `LICENSE` — MIT
- `.makefun/owner.json` — claim file naming the entrant's wallet
