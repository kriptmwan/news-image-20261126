// news-image-20261126: a one-image entry for make.fun.
//
// The picture itself is entry.png, drawn up front by render.py (PIL) from
// the real news of Thursday 26 November 2026: tankers burning in the
// Strait of Hormuz, America's tariff wall, missiles over Kyiv, plus the
// day's other headlines. This program does the only thing the grader
// needs at run time: place that exact image at /output/entry.png.
//
// Deterministic: the copy is byte-for-byte, so two runs write the same
// bytes. No network, no clock, no input besides the bundled PNG.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
// /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
writeFileSync(target, readFileSync(join(here, "entry.png")));
