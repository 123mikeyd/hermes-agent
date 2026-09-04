# Multi-performer render and QA

Use this note for long Blender dance or action renders with a hero plus one or more secondary performers.

## Camera acceptance before rendering

A camera-space intersection test is too weak: an actor can technically intersect the frame while only a glove or narrow body sliver is visible.

1. Preserve artist-placed actor transforms in the source scene.
2. Evaluate each renderable character mesh through the final camera at every labeled section start, midpoint, and endpoint, plus frames containing the actor's widest gestures.
3. Project evaluated mesh bounds—not object origins or armature bounds—and record visible fraction and edge margins.
4. Require the intended body coverage explicitly: for a full-body dance shot, head, hands, and feet need positive margins. A fragment at an edge is a failure.
5. If the hero-tracking camera loses the backup performer, first widen or retarget the camera toward a group framing target. Do not silently move the artist's performer. If staging versus framing is an artistic tradeoff, show it and ask.
6. Render a labeled preflight coverage sheet before the expensive sequence. Include all hero sections and secondary loop extrema.

## Recoverable long-render workflow

1. Save a versioned render derivative; leave the animation library and artist-approved source untouched.
2. Render numbered PNGs at the intended FPS and raster. Verify external images resolve before starting.
3. Benchmark one representative frame to estimate cost and check the real render engine.
4. While the full sequence continues, encode only an immutable completed prefix for an early motion review. Later, inspect an action-heavy late segment. Never read the frame currently being written or mutate the sequence directory.
5. After completion, programmatically require the exact expected frame set with no gaps or extras.
6. Encode the delivery master with H.264/yuv420p/faststart (or the requested format). Keep the PNGs until acceptance so isolated ranges can be rerendered.

Example:

```bash
ffmpeg -y -framerate 30 -start_number 1 \
  -i 'frames/frame_%04d.png' \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -movflags +faststart output.mp4
```

## Verification evidence hierarchy

Use each tool for what it can prove:

- **Blender structural probes:** NLA coverage, repeat count, evaluated pose deltas, late-scene motion, floor clearance, camera projections.
- **Rendered PNG frames:** geometry, textures, signs, lighting, exact boundaries, actor visibility.
- **`ffprobe -count_frames`:** codec, streams, audio presence, raster, FPS, duration, pixel format, frame count.
- **Focused video excerpts:** temporal continuity, loop hitches, flicker, camera motion.
- **Full-video semantic review:** overall watchability and section-level issues; not authoritative for tiny geometry defects or stream metadata.

If reviews conflict, name the suspect frame range and inspect the original-resolution frames or a tight actor crop. A full-video model may infer nonexistent audio or mistake low-poly clothing for stretched geometry; a sparse contact sheet may miss an in-between temporal hitch. Resolve the exact claim instead of averaging opinions.

When semantic video review cannot reliably ingest a long local master, preserve the master and make a compact QA derivative, then split it into bounded consecutive excerpts. Record exactly which intervals were actually reviewed. If excerpt ingestion remains inconsistent, stop retrying and close acceptance with deterministic full-timeline coverage/boundary sheets, `ffprobe`, black/freeze scans, and short known-good excerpts; never describe partial semantic coverage as a full-video review.

## Final acceptance

- Exact frame count and no gaps.
- Coverage sheet spans every labeled Action/section.
- Adjacent-frame sheet spans every hero transition and representative secondary-loop wraps.
- Every intended performer is recognizably framed wherever the shot promises ensemble coverage.
- Targeted excerpts show no freeze, teleport, bind pose, deformation, or stage flicker.
- `ffprobe` confirms the delivery metadata and whether audio is absent or present.
- Deliver both the editable versioned `.blend` and encoded video, with any known framing compromise stated plainly.
