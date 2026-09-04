---
title: "Blender Music Video Production — Build and verify long-form Blender music videos"
sidebar_label: "Blender Music Video Production"
description: "Build and verify long-form Blender music videos"
---

{/* This page is auto-generated from the skill's SKILL.md by website/scripts/generate-skill-docs.py. Edit the source SKILL.md, not this page. */}

# Blender Music Video Production

Build and verify long-form Blender music videos.

## Skill metadata

| | |
|---|---|
| Source | Optional — install with `hermes skills install official/creative/blender-music-video-production` |
| Path | `optional-skills/creative\blender-music-video-production` |
| Version | `0.1.0` |
| Author | Mike (123mikeyd), Hermes Agent |
| License | MIT |
| Platforms | linux, macos, windows |
| Tags | `blender`, `animation`, `music-video`, `nla`, `ffmpeg`, `rendering` |
| Related skills | [`kanban-video-orchestrator`](/docs/user-guide/skills/optional/creative/creative-kanban-video-orchestrator) |

## Reference: full SKILL.md

:::info
The following is the complete skill definition that Hermes loads when this skill is triggered. This is what the agent sees as instructions when the skill is active.
:::

# Blender Music Video Production

Turn rigged Blender characters and animation Actions into a versioned,
reviewable, long-form music video. The workflow covers animation-library
intake, rig compatibility, ensemble staging, complete-song extension,
recoverable rendering, encoding, and deterministic delivery QA.

This skill does not provide models, animations, music, textures, or Blender
itself. It preserves user-supplied assets and requires source-specific license
compliance.

## When to Use

Use this skill when:

- a Blender character has multiple Actions that need cataloging or sequencing;
- several imports contain the same character with different dances;
- a hero, backup dancers, static cameos, or mascots must share one stage;
- the animation must be extended to a complete song;
- the final deliverable must include an editable `.blend` and verified video;
- a long render needs recoverable frames and evidence-based visual QA.

Do not use it for:

- one-shot transcoding with no Blender scene changes;
- live performance capture or real-time streaming;
- animation retargeting when the source and target skeletons are still unknown;
- publishing third-party assets whose licenses have not been confirmed.

## Prerequisites

- Blender installed; procedures are verified against Blender 5.2.
- FFmpeg and FFprobe available for encoding and metadata checks.
- Python available for contact sheets and file-count verification.
- Pillow available when running `scripts/contact_sheet.py`.
- User-supplied assets with known, acceptable licenses.
- Enough disk space for a numbered PNG sequence. Long-form 720p projects may
  produce thousands of frames and several gigabytes of intermediate files.

Before editing, use `terminal` to confirm Blender and FFmpeg versions. Use
`search_files` and `read_file` to locate the source scene and any project
instructions. Never inspect or print secrets while surveying the project.

## How to Run

Drive Blender through `terminal` with explicit source, script, and output paths:

```text
terminal(command='"<BLENDER>" -b "<SOURCE.blend>" --python "<SCRIPT.py>" -- "<OUTPUT.blend>"', timeout=600)
```

Render recoverably to numbered images rather than directly to a movie:

```text
terminal(command='"<BLENDER>" -b "<RENDER_READY.blend>" -a', background=true, notify=true)
```

Encode only after the image sequence passes frame-count and contact-sheet QA:

```text
terminal(command='ffmpeg -y -framerate 30 -start_number 1 -i "frames/frame_%04d.png" -i "music.wav" -map 0:v:0 -map 1:a:0 -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart output.mp4', timeout=600)
```

Use `vision_analyze` on representative stills and boundary sheets. Use
`video_analyze` on short encoded transition segments and the final deliverable
when the service accepts its size. Deterministic metadata and frame evidence
remain authoritative when a video-analysis service cannot ingest the file.

## Quick Reference

| Need | Required action | Completion criterion |
|---|---|---|
| Protect live work | Save Copy or inspect the matching autosave | Original filepath and dirty state remain safe |
| Catalog Actions | Inventory rigs, meshes, ranges, slots, and rest transforms | Every source clip has a reversible record |
| Reuse an Action | Compare ordered bones and complete rest matrices | Direct reuse only when compatibility is exact |
| Preserve travel | Separate skeletal Body motion from a MotionRoot | No positional reset at clip boundaries |
| Loop a backup | Repeat one protected native Action in NLA | Strip covers the hero's final frame |
| Consolidate imports | Keep one artist-placed rig/mesh visible | Duplicate carriers are hidden, not discarded |
| Add a song | Compare exact audio and animation durations | Every animated layer reaches song end |
| Animate a mascot | Use a protected closed Action and finite NLA repeat | Boundary delta stays inside ordinary motion |
| Add a static cameo | Measure camera visibility before optimizing | Full-quality source remains preserved |
| Render | Write numbered PNG files | Expected count, dimensions, and range match |
| Deliver | Encode H.264/AAC and run FFprobe | Frames, FPS, duration, streams, and size pass |

## Procedure

### 1. Protect and inventory the source

1. Check whether the open Blender scene has unsaved changes.
2. If it is dirty, inspect the matching Blender autosave in a separate
   background process or use Blender's Save Copy operation. Do not overwrite
   the live file merely to make it inspectable.
3. Save a versioned derivative before adding NLA strips, camera work, stage
   assets, or audio.
4. Inventory the scene's FPS, frame range, active camera, meshes, armatures,
   Actions, Action Slots, NLA tracks, materials, packed images, and external
   paths.

Completion criterion: the source remains recoverable and the inventory names
every object and datablock that later automation will touch.

See `references/blender-unsaved-action-auditions.md` and
`references/bare-armature-dance-carrier-libraries.md`.

### 2. Validate and catalog animation

1. Audition each native rig-and-mesh pair before consolidation. Render a
   consistently framed still at a representative pose.
2. Treat matching bone names as necessary but insufficient. Compare ordered
   names, hierarchy, bone directions, roll, and complete rest matrices.
3. When rest transforms match, duplicate the source Action, retain source
   metadata, enable Fake User, and test the copy on the canonical rig.
4. When rest transforms differ, bake a target-specific corrected Action. Do
   not directly assign incompatible local rotations and hope the mesh survives.
5. Keep Body and RootMotion Actions separate. Accumulate each new root path
   from the prior clip's exact endpoint.

Completion criterion: each approved motion has a protected, named Action and
representative target-rig renders with normal hands, sleeves, shoulders, and
legs.

See `references/rest-pose-corrected-dance-retargeting.md`.

### 3. Build one visible performer per character

1. Choose the canonical actor from the artist's deliberate placement and
   approved mesh, not import order.
2. Parent that rig to a persistent lineup or MotionRoot object while preserving
   the evaluated world transform.
3. Place distinct Actions into an editable NLA playlist with explicit timing,
   extrapolation, and overlap values.
4. Move redundant rig-and-mesh imports into a hidden source-carrier collection.
   Keep their original Actions protected for audit and recovery.
5. Reopen the output and compare the copied Actions against source poses at
   start, midpoint, and end.

Completion criterion: exactly one render-visible instance remains for each
character, every requested Action exists on it, and duplicate imports no longer
overlap the hero.

See `references/same-character-multi-import-dance-consolidation.md`.

### 4. Sequence the ensemble

1. Keep the hero's Body and MotionRoot layers independent.
2. Loop each secondary dancer on its own verified native Action. Use the
   interval between Action endpoints, not the inclusive frame count, when
   calculating NLA repeats.
3. Compare every wrap delta against ordinary within-clip motion and prove
   nonzero late-scene motion.
4. Validate performer framing from evaluated render-mesh bounds. A glove or
   bounding-box sliver touching the edge is not readable coverage.
5. Preserve artist-approved placement. If a tracking camera crops a side actor,
   widen or retarget the camera before silently moving that actor.

Completion criterion: every required performer remains animated through the
scene end, loop boundaries are ordinary motion, and intentional camera-edge
appearances are documented separately from animation failures.

See `references/secondary-dancer-continuous-nla-loops.md` and
`references/multi-performer-render-and-qa.md`.

### 5. Block the stage, camera, and display

1. Size the performance surface from the evaluated root-motion envelope.
2. Use one authoritative broad walkable surface. Separate lower skirts and
   narrow inlays vertically to prevent z-fighting.
3. Keep detailed PBR floor modules outside the measured dance path. Treat
   public preview maps as provisional look-development assets.
4. Track a torso-height target parented to the hero's MotionRoot. Use sparse,
   section-level camera beats and restrained static lighting.
5. Put wall media on a renderable UV-mapped plane. Fit mismatched aspect ratios
   without destructive stretch or crop unless the artist explicitly requests
   it.
6. Validate artwork, physical frame, and labels as separate screen-space bounds.

Completion criterion: representative wide and dance-pose renders preserve feet,
character silhouette, stage hierarchy, display integrity, and stable floor
shading.

See `references/dance-stage-and-tracked-camera-blocking.md`,
`references/industrial-pbr-stage-lookdev.md`, and
`references/wall-display-media-and-camera-fit.md`.

### 6. Fit the complete song

1. Inspect the supplied audio with `terminal` and FFprobe. Record codec, sample
   rate, channels, duration, and file size.
2. If the audio and animation lengths differ, ask whether to trim, select an
   excerpt, or extend the choreography. Do not make a destructive musical edit
   by assumption.
3. For a complete-song extension, update every time-dependent layer: hero Body,
   MotionRoot policy, secondary NLA loops, camera object, camera data/lens, and
   scene end.
4. In Blender 5.2, create a sound strip with
   `scene.sequence_editor_create().strips.new_sound(...)` and use audio-sync
   playback.
5. Repeat camera object and camera-data slots independently when one multi-slot
   Action drives both.

Completion criterion: the sound strip starts with the scene, reaches the intended
end, and every dancer plus the camera has nonzero valid evaluation at the final
frames.

See `references/full-song-blender-music-video-extension.md`.

### 7. Add restrained background motion and cameos

1. Give a flying mascot a dedicated root and reusable closed Action. A compact
   horizontal figure-eight with a smaller vertical bob reads as insect-like
   motion without becoming a second focal performance.
2. Project the evaluated mascot through every camera beat and preserve full
   silhouette margins, not merely an in-frame origin.
3. For static background actors, compute meaningful visibility intervals and
   render the frame with greatest screen coverage.
4. Preserve a full-quality scene before optimizing any heavy cameo. Decimate
   only static background geometry and duplicate or downscale only its unique
   textures.
5. Compare full-quality and optimized stills, then render a temporal test at the
   intended delivery raster.

Completion criterion: mascot loops close without a hitch; cameo identity,
silhouette, materials, grounding, and temporal stability survive optimization.

See `references/background-mascot-flight-loops.md` and
`references/long-form-music-video-render-and-static-cameo-optimization.md`.

### 8. Gate the full render

Render representative frames for:

- every Action start, midpoint, and end;
- every NLA and full-sequence cycle boundary;
- every camera transition;
- the mascot wrap;
- the widest secondary-performer gestures;
- the static cameo's maximum-coverage moment;
- the middle and final frame of the complete-song extension.

Use `scripts/contact_sheet.py` to build a labeled coverage sheet and an adjacent
boundary-pair sheet. Use `scripts/verify_wall_display_camera_fit.py` when a wall
display or labels must remain readable. Use
`scripts/diagnose_run_alignment.py` for locomotion direction and floor clearance.

Completion criterion: all stills and short temporal tests pass before the
long render begins.

### 9. Render and encode recoverably

1. Save a final render-only derivative.
2. Render a numbered PNG sequence. Do not depend on a single in-progress movie
   file for a multi-hour job.
3. Count files and verify dimensions before encoding.
4. Encode H.264 video with `yuv420p` and AAC audio. Preserve the complete visual
   frame count even when the audio is a few milliseconds shorter.
5. Keep the frame sequence until the final movie passes QA; selective rerenders
   can then replace only affected ranges.

Completion criterion: every expected source frame exists and FFmpeg exits
successfully with the intended video and audio streams.

### 10. Verify the deliverable

1. Run FFprobe with frame counting. Record dimensions, codec, pixel format,
   average frame rate, frame count, duration, audio sample rate, channels, and
   byte size.
2. Build final coverage and boundary sheets from the actual rendered sequence.
3. Run black-frame and long-freeze detection across the encoded movie.
4. Review short encoded segments around the opening, cameo, each full-sequence
   transition, and ending. If whole-file video analysis fails, keep the failure
   honest and rely on deterministic metadata plus segmented evidence.
5. Reopen the final `.blend`, record the verified movie path and QA evidence,
   and deliver both artifacts.

Completion criterion: the final movie's declared metadata matches its real
streams, all sampled boundaries pass, and the editable source remains available.

## Pitfalls

- **Direct-to-MP4 rendering:** it still computes every frame and loses recovery
  options if Blender stops. Use numbered images first.
- **Inclusive frame arithmetic:** an Action spanning frames 1–124 repeats over
  123 intervals. Using 124 creates a recurring hitch.
- **Equal bone names:** they do not prove compatible rest orientations.
- **Hidden rig evaluation:** hiding a carrier too early can make a diagnostic
  pose appear frozen. Compare Actions before hiding source rigs.
- **Action Slot mismatch:** Blender 5.2 multi-slot Actions may need separate
  object and data NLA strips.
- **Camera-origin checks:** an origin can be in frame while most of the mesh is
  cropped. Project evaluated bounds.
- **Floor shimmer:** first test for broad coplanar surfaces. Polygon count and
  roughness are not substitutes for eliminating z-fighting.
- **Static million-vertex cameos:** they can multiply frame time even when only
  briefly visible. Optimize only in a protected render derivative.
- **Audio-shorter-than-video:** `-shortest` may discard the final video frame.
  Preserve the full frame sequence and tolerate a millisecond-scale silent tail
  when necessary.
- **Video-analysis availability:** a service may reject long or large local
  files. Never claim it reviewed media it could not ingest.

## Verification

Before delivery, require all of the following:

- [ ] source scene preserved and versioned derivative created;
- [ ] every Action cataloged with source mapping and Fake User protection;
- [ ] direct Action reuse supported by exact rest-transform compatibility;
- [ ] one visible canonical rig and mesh per performer;
- [ ] Body and MotionRoot continuity proven at every hero boundary;
- [ ] secondary loops cover the final frame and retain late motion;
- [ ] full song, camera object, camera data, and all performers share the same
      intended timeline;
- [ ] mascot and static-cameo visibility validated through the real camera;
- [ ] representative stills and temporal tests passed;
- [ ] numbered frame count equals the requested scene range;
- [ ] FFprobe confirms codec, dimensions, FPS, frame count, duration, and audio;
- [ ] final coverage and boundary sheets contain no bind pose, teleport,
      missing actor, deformation, black frame, or corrupted ending;
- [ ] editable `.blend`, encoded video, and honest QA notes are delivered.

## Acknowledgments

This workflow was developed using user-supplied 3D models created with Meshy
and animation clips obtained from Mixamo. Those services and their assets are
not bundled with this skill. Blender, FFmpeg, Meshy, and Mixamo retain their
respective names, terms, and licenses.
