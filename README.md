# The World in One Day — 26 November 2026

[![news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/kriptmwan/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/kriptmwan/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126)

One 1024×1024 image summing up the world's news of Thursday 26 November 2026, built for the [make.fun bounty](https://make.fun/bounty/news-image-20261126).

## The front page

- **Lead — TANKERS BURN IN HORMUZ.** Iran vows the strait stays shut as mines hit a supertanker carrying two million barrels of crude; a second tanker burns and a blast is reported west of Dubai.
- **AMERICA'S TARIFF WALL.** Washington proposes duties on 14 nations — China 20%, India 25%, Vietnam 35%, EU and Japan 15%.
- **MISSILES HIT KYIV MALL.** Russia fires 113 drones at Ukraine's cities; 7 hurt in Kyiv, 3 killed in Kharkiv.
- **Also today.** Cairo tanker blast kills 31; Macy's parade delayed — a first in 100 years; Gaza strikes kill 9 despite a ceasefire.
- **Briefs.** Netanyahu trial: judges urge the bribery charge dropped; Solomon Islands signs an Australia security treaty; UK migration lowest since 1997.

## How it is made

`render.py` draws the page with PIL (DejaVu fonts, measured word wrap, layout asserts that fail the build rather than clip text). `main.ts` (Node 22, standard library only) copies the finished `entry.png` to `/output/entry.png`. The render is deterministic — two runs write byte-identical PNGs — and the program uses no network.

```sh
python3 render.py          # writes entry.png (1024x1024, < 1 MiB)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

## License

MIT — see [LICENSE](LICENSE).
