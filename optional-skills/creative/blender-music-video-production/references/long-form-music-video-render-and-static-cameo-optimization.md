# Long-form music-video render and static-cameo optimization

Use this reference when a Blender dance scene expands to a complete supplied song, especially when late-added static characters make the final render materially heavier.

## 1. Calculate and disclose the real render commitment

Inspect the soundtrack with `ffprobe`; do not infer duration from a filename or editor display. For a scene starting at frame 1, a practical inclusive end frame is:

```python
scene_end = math.ceil(audio_duration_seconds * fps)
```

Before rendering, tell the artist:

- exact audio duration and scene frame range;
- total output frames, FPS, and raster;
- time for a representative **worst-case** frame;
- estimated elapsed time and available disk space;
- that a numbered PNG sequence is recoverable if interrupted.

Rendering directly to MP4 does **not** avoid computing each animation frame. It only changes the output/recovery strategy. Ask for explicit approval before a long full-song render. If questioned mid-render, report completed frames, percentage, estimated remainder, and whether cancellation preserves completed PNGs.

Validated example: a 291.880167-second song at 30 FPS used frames 1–8757. The resulting video span was 291.900000 seconds, leaving only a 0.019833-second visual tail after the audio.

## 2. Extend every time-dependent layer

Adding audio alone is not a full-song edit. Verify that the full timeline is covered by:

- hero Body Actions;
- MotionRoot policy;
- every secondary performer’s NLA strips;
- mascot loops;
- camera object animation;
- camera-data animation such as lens changes;
- the soundtrack strip itself.

A safe extension for an already-approved traveling hero is to repeat the protected Body sequence with short overlaps while holding the final MotionRoot position. This avoids a world-space teleport. For a Blender 5.2 multi-slot camera Action, repeat compatible strips separately on the camera object and camera data. Fresh-reopen and prove nonzero late motion for every animated performer.

## 3. Measure a brief static cameo before optimizing it

A static character that is visible only near the camera edge can still dominate load time. Inventory:

- vertex/polygon count;
- evaluated dimensions and world bounds;
- material and image user counts;
- packed/external image state and dimensions;
- exact camera-visible intervals.

Project the evaluated bounding box through every camera frame. Distinguish a bounding-box sliver from a recognizably framed cameo; use clipped screen area and a rendered maximum-area frame, not object presence alone.

If the cameo is roughly a million vertices and small in a 720p background shot:

1. Preserve the full-quality scene.
2. Create a render-only derivative.
3. Decimate only the static cameo, commonly to roughly 100k–120k vertices.
4. If its materials/images are unique, copy or safely reduce 4K maps to packed 2K assets in the derivative; never downscale shared hero/stage textures.
5. Compare the same maximum-area frame full-quality vs optimized at delivery size.
6. Compare enlarged actor crops for holes, silhouette collapse, visor/material damage, UV shifts, faceting, and grounding.
7. Render a short temporal segment to catch popping, texture crawl, shimmer, or unstable highlights.
8. Reduce EEVEE samples only when the same still and temporal checks pass.

A successful modifier application is transport status, not visual approval.

## 4. Render recoverably and review progressively

Render a numbered PNG sequence. While Blender continues, it is safe to encode an immutable early prefix or already-completed transition range for QA; never touch frames Blender may still be writing.

Useful progressive checks:

- opening 10–20 seconds with soundtrack;
- maximum-visibility cameo interval;
- first repeated Body/camera cycle boundary;
- second cycle boundary when available;
- ending and late secondary-performer loop.

Abort only for a reproducible blocker. A semantic reviewer’s broad claim must be checked against targeted final-raster frames or a short suspect clip.

## 5. Encode audio without losing the last visual frame

MP3 files may carry an attached cover-art video stream, so map streams explicitly:

```bash
ffmpeg -y -framerate 30 -start_number 1 \
  -i 'frames/frame_%04d.png' -i 'song.mp3' \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart output.mp4
```

Do not use `-shortest` by habit. In the validated 30 FPS example above, `-shortest` encoded 8756 video frames because the audio ended 0.019833 seconds before the 8757-frame image sequence. Omitting `-shortest` preserved all 8757 frames and produced only a sub-frame silent tail. Padding or deliberate trimming is also valid, but must be explicit.

## 6. Deterministic final acceptance

Require all of the following:

1. Programmatic PNG count equals the intended inclusive scene range, with no gaps.
2. Sampled images decode at the intended raster.
3. `ffprobe -count_frames` confirms video frame count, FPS, raster, pixel format, codecs, audio sample rate/channels, and per-stream durations.
4. A coverage sheet samples every dance family, every repeated cycle, the cameo’s best frame, full-song middle, near-ending, and final frame.
5. A boundary sheet includes original dance joins, mascot/secondary loops, camera-cycle joins, Body-cycle joins, and late loops.
6. Targeted motion clips cover opening, dense cameo, cycle transition, and ending.
7. A full-stream black/freeze scan reports no unexplained events.

Semantic video services may reject long or large local files. Preserve the delivery master, create a smaller QA derivative, and try short segments. If ingestion remains inconsistent, say so and rely on the deterministic metadata, frame sequence, contact sheets, and successfully reviewed targeted clips rather than inventing whole-video observations.
