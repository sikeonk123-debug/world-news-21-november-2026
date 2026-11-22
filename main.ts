// A working news-image entry (Node 22, standard library only): its image is
// the entry.png beside this file, and the program copies it to
// /output/entry.png. The image sums up Saturday 21 November 2026 in one
// newspaper front page: 35 stories, 7 regions, drawn with Pillow by
// draw.py in this repository.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync } from 'node:fs';
import { join } from 'node:path';

copyFileSync(new URL('./entry.png', import.meta.url), join(process.env.MAKEFUN_OUTPUT_DIR ?? '/output', 'entry.png'));
