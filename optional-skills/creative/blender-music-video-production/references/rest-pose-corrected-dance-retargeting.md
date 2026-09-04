# Rest-pose-corrected dance retargeting

Use this reference when animation-only or bare-armature dance imports share bone names with a skinned canonical character, yet direct Action assignment sends hands far away, stretches sleeves into ribbons, collapses shoulders, or otherwise looks “wonky.”

## Recognize the failure class

A remote hand connected by a long strip of sleeve is not automatically a character-scale problem or a weight-paint problem. Diagnose in this order:

1. Render the canonical rig’s own known-good Action on its matching mesh. If that Action is clean, preserve the mesh, armature, weights, object scale, and rest pose.
2. Compare source and canonical armatures:
   - ordered bone names and parent hierarchy;
   - object scale and mesh/armature world matrices;
   - arm-chain bone lengths;
   - complete rest matrices, especially shoulders, upper arms, forearms, and hands.
3. Inspect Action channels in Blender 5.2 through Action layers, strips, channelbags, and F-curves. Measure:
   - non-root `pose.bones[...].location` values;
   - every bone’s scale curves;
   - root/hips translation separately.
4. If arm lengths match, non-root locations are effectively zero, scales remain one, and only rest orientations differ, the problem is **rest-pose orientation mismatch**. Do not resize the character, lengthen bones, repaint weights, or keep the raw Action directly on the canonical rig.

A raw T-pose-style carrier Action can be numerically valid on its source while producing remote hands on an A-pose or otherwise revised canonical rig. Matching names are not enough.

## Preserve source data

- Keep every imported Action unchanged on its native carrier and enable Fake User.
- Work in a versioned cinematic derivative, never the animation-library master or unsaved live window.
- Keep exactly one visible canonical mesh+rig pair.
- Append old Actions without appending old character meshes or armatures when the final cast must retain one identity.
- Use reversible labels for generic clips and preserve source names/ranges in a report.

## Absolute-local-rotation bake

For each source frame, evaluate the source carrier on its own rig. For every target bone in parent-first order:

1. Compute the source bone’s evaluated local pose matrix:
   - child: `source_parent_pose.inverted() @ source_pose`
   - root: `source_pose`
2. Extract the source local rotation.
3. Compute the target bone’s rest-local matrix:
   - child: `target_parent_rest.inverted() @ target_rest`
   - root: `target_rest`
4. Build the desired target-local pose using:
   - the **target rest-local translation** (preserves canonical bone length and joint placement);
   - the **source evaluated local rotation** (removes the incompatible source-rest arm offset);
   - unit scale.
5. Convert desired target-local pose to target basis with:
   `basis = target_rest_local.inverted() @ desired_target_local`
6. Assign/key the target pose bone’s Location, Quaternion Rotation, and Scale from that basis.
7. For the root/hips only, preserve desired vertical bounce deliberately. Put world travel on a parent MotionRoot or compensate X/Y separately; discard non-root translation and imported scale.

This differs from two common failures:

- **Direct NLA/raw Action assignment** preserves source-relative rotation offsets against the wrong target rest orientation.
- **Naive pose-matrix copying** can inherit source joint positions or produce unstable target basis values when parent evaluation is not handled explicitly.

## Audition before full rendering

1. Render the canonical character’s known-good baseline Action first.
2. For every corrected dance, render at least quarter, midpoint, and three-quarter samples.
3. Inspect actual hands, wrists, sleeves, shoulders, elbows, feet, coat tails, and floor contact. Do not let long coat panels be mistaken for arms; zoom or inspect isolated frames when uncertain.
4. Require ordinary anatomical arm reach. Reject any hand several torso widths away, ribbon-like sleeve, telescoping arm, detached wrist, collapsed shoulder, or one-frame bind pose.
5. When a long Action contains a risky interval, audition several 90-frame (or delivery-sized) windows and record the approved source range rather than editing the protected Action.
6. Review all clip boundaries. Unrelated dances may not blend credibly; short dip-to-black transitions are safer than exposing a pose snap or inventing one bad in-between frame.

## Full showcase integration

- Keep the same canonical mesh and armature visible for Moonwalk, earlier dances, and newly retargeted dances.
- Build separate protected Actions for logical sections, then sequence those target-specific Actions through NLA.
- A background performer must receive its own target-specific rest-corrected bake. A matching bone-name list does not make the hero’s local rotations directly portable to a differently proportioned secondary rig.
- Place a secondary dancer with a parent lineup/root Empty. Verify that the hero remains dominant and the background dancer is smaller, behind, fully visible, and genuinely animated.
- Reassert scene FPS after the last FBX import; FBX import can reset it.

## Viewport approval gate and the hidden-source trap

Before building a multi-clip reel, produce one full-length `PREVIEW` file and let the artist play it in Blender.

1. During the bake, keep the source carrier **evaluable**. A carrier object can report `hide_set(False)` yet still be disabled because its parent collection has `hide_viewport=True`; clear both object and collection viewport hiding before sampling. `hide_render=True` is safe when no source mesh should appear.
2. Hide source carriers only after the target Action is fully keyed. Sampling a viewport-disabled carrier can return one stale pose for every frame, producing a frozen target Action that still saves successfully.
3. Do not mistake different static midpoint poses across several clips for animation. Verify motion **within one clip** by measuring adjacent evaluated pose matrices over its full frame range; require a nonzero maximum/median pose delta and inspect playback.
4. Keep the canonical target armature evaluable in the preview. If hiding the armature stops evaluated playback or modifier updates, leave it visible with an unobtrusive `STICK` display rather than hiding it. Hide the raw-carrier collection, select the canonical mesh, frame it in Material Preview, set the exact Action range, and start at frame 1.
5. Reopen the saved preview in a fresh process and assert: canonical mesh parent/modifier target, one active target-specific Action, no unintended NLA tracks, exact FPS/range, all carriers hidden, nonzero within-clip motion, and plausible shoulder-to-hand reach relative to the canonical arm-chain length.
6. Open the verified preview in a **separate Blender window**, leaving any unsaved live source untouched. Stop there. The artist plays the full Action and approves hands, shoulders, elbows, sleeves, coat, feet, and motion quality before any batch retarget or video render begins.

A successful save, valid key count, or multi-clip contact sheet is not proof of motion. The preview gate specifically prevents a frozen bake from being promoted into a polished-looking but invalid full reel.

## Accumulate original root travel across approved dances

When the artist approves the corrected body motion and asks to restore travel, do not put source hips X/Y back into the canonical skeletal Action. Preserve travel as reusable root data:

1. While the source carrier is evaluable, sample its evaluated hips position for every native frame. Convert each sample into world units with the source object transform, then subtract the clip’s first sample. This produces a relative path whose first point is exactly zero.
2. Keep the corrected Body Action in place: preserve hips Z bounce deliberately, but keep hips X/Y on the canonical rig fixed.
3. Parent the canonical rig to a `Character_MotionRoot` Empty without changing its world transform. Key the relative X/Y path on that Empty, with Z normally left at zero.
4. Save separate protected Actions for every clip, for example `Dance01_UNNAMED_Body_RestCorrected` and `Dance01_UNNAMED_RootMotion`. Fake User both. These pairs are the reusable library units; a combined preview Action is only presentation data.
5. To sequence a second traveling clip without a reset, accumulate its path from the first clip’s evaluated endpoint:
   `combined_next(frame) = previous_end + (next_relative(frame))`.
   Because `next_relative(start) == 0`, the two root frames at the boundary must occupy the same world point.
6. Blend the body pose over a short reviewed interval (a validated starting point is about 12 frames at 30 FPS), but do not blend the root toward world zero. Keep the next clip’s native relative path advancing from the accumulated endpoint.
7. Verify the fresh file numerically: root boundary distance is zero or negligible; the body boundary delta is no larger than nearby natural frame deltas; both clips have nonzero within-clip pose motion; and shoulder-to-hand reach remains plausible.
8. Distinguish a **natural return** from a reset. A dance can travel several metres and finish close to its own start. If the accumulated endpoint is therefore near the original world position, report that source behavior rather than claiming the root was reset.

## Semantic naming and cataloging

Do not guess dance names from generic `mixamo.com` labels or a few static poses.

1. Use reversible placeholders such as `D01 — UNNAMED` and `D02 — UNNAMED` while the artist auditions the full clips.
2. Add exact timeline markers at every clip start and embed a Text catalog in the `.blend`.
3. Maintain a CSV/JSON sidecar containing catalog ID, provisional display name, source Action/range, duration, Body Action, RootMotion Action, travel extents/path length, continuous-preview range, and approval status.
4. Open the continuous preview in a separate Blender window and stop before rendering. Ask the artist to provide names after watching each marked interval.
5. Once names are approved, rename the Body Action, RootMotion Action, timeline marker, embedded catalog entry, and sidecar row together. Preserve source identifiers in custom properties so semantic renaming never breaks provenance.

## Category-aware incremental approval loop

Treat catalog order, preview order, and inclusion policy as separate data. A raw clip can keep catalog ID `D02` while being excluded from the current preview and the next approved clip `D03` follows `D01` directly.

1. After the artist names a clip, preserve the display name exactly as supplied. Use a filesystem/API-safe Action identifier if needed, but store the exact display name in Action custom properties and the catalog.
2. Assign an artist-approved category and mixing policy. A useful split is `Cool Dance Moves` versus `Silly Meme Dances`, with an explicit rule such as “set aside; use only in intentionally silly or meme-themed videos.”
3. Rename and protect the complete reusable bundle together: corrected Body Action, RootMotion Action, source provenance properties, timeline marker, embedded Text catalog, and CSV/JSON row.
4. Setting a clip aside means its protected Body and RootMotion Actions remain in the `.blend` with Fake User, but neither is assigned to the current hero or MotionRoot and its preview range is recorded as `SET ASIDE`.
5. Add only the next eligible raw carrier to the preview. Keep that carrier and its collection evaluable during sampling, create full-length corrected Body and RootMotion Actions, then hide the carrier after baking.
6. Rebuild the active timeline from the **most recently approved compatible handoff clip plus exactly one unnamed candidate** by default. If the artist explicitly requests a small batch (for example, “show two or three more”), include exactly that many consecutive unnamed candidates after one short handoff clip; do not interpret the request as permission to replay the entire catalog. Keep all earlier approved Body/RootMotion Actions protected with Fake User and represented in the catalog, but inactive unless requested. Start every candidate path at the prior clip's accumulated endpoint; no skipped or batched catalog boundary may reset to world zero.
7. Give the handoff and every candidate an exact start marker and sidecar frame range. Open the fresh preview in a separate Blender window and stop before rendering. For a batch, ask the artist to reply by stable IDs (`D07 = …`, `D08 = …`) so names cannot shift between clips. Only after the artist classifies the shown candidates should the loop advance.
8. Verify that set-aside Action names are absent from the active hero and MotionRoot Actions, boundary root distance is zero/negligible, the new clip has nonzero travel and within-clip pose motion, and sampled shoulder-to-hand reach remains within the canonical arm chain.

This preserves meme or novelty material without allowing it to contaminate a coherent movement family, and it supports an enjoyable one-clip-at-a-time curation session instead of another premature full render.

## Promote categories as the movement vocabulary becomes clear

Treat broad categories as provisional. Once the artist recognizes a coherent family, update the catalog rather than leaving everything under a generic `Cool Dance Moves` bucket.

- Use an artist/style family such as `Michael Jackson Dance Moves`, with a narrower style tag such as `Smooth Criminal`, when multiple approved clips belong together.
- Use a movement family such as `C-Walk Dance Moves` when the artist expects more related clips later. When another reviewed clip joins that family, derive the next numeric suffix from existing approved catalog entries and apply it only after the artist confirms the classification (`C-walk01`, `C-walk02`, …); preserve the artist's exact capitalization and punctuation.
- Keep novelty material in `Silly Meme Dances` with an explicit mixing policy; a protected meme Action can remain reusable without entering the current serious/cool preview.
- When a clip merely resembles a franchise, regional genre, or pop act, do not assert that provenance. Prefer a neutral functional numbered family such as `Boy_Band_Dance01`, put it under a broad category such as `Group Dance Moves`, and store uncertain style hints separately. Record ensemble intent—recommended cast count or formation and whether the clip is reserved for synchronized group scenes—in both Body/RootMotion metadata and the sidecar catalog.
- Preserve the artist's exact display spelling in catalog fields. Action datablock identifiers may use safe separators, but custom properties and sidecars must retain the approved display name.
- A current preview should contain an approved family or compatible handoff clip plus exactly one unnamed candidate. Do not replay every approved clip on every naming pass when the artist asks to move to the next family.

## Single-preview-window hygiene

Multiple open versioned Blender previews create a real review hazard: playback or saving may target a superseded file even when the newest file exists on disk.

1. Build and fresh-reopen the successor `.blend` in the background first. Verify Actions, categories, markers, MotionRoot continuity, hand reach, and `NOT RENDERED` status.
2. If the artist explicitly asks to save and close all Blender windows, pause playback and save each intentionally retained window. Confirm the title-bar dirty marker clears before closing it.
3. Close windows gracefully. Do not use a force-kill while unsaved windows exist; it can discard the artist's viewport or Action edits.
4. After each close, refresh the live window list. Same-application automation can retain a stale HWND or target a different Blender process after the top window closes.
5. Require zero Blender windows before launching the successor. Then open exactly one preview and verify its full title/path, frame range, frame-1 state, selected canonical mesh, and expected first timeline marker. The successor may retain the complete approved Action library as inactive datablocks, but its active timeline should normally contain only the latest compatible handoff clip and one unnamed candidate.
6. Leave playback stopped. The artist presses Spacebar, reviews the unnamed interval, and supplies the next semantic name; rendering remains blocked.

## Deterministic verification

Before delivery, verify all of the following from fresh processes and actual outputs:

- canonical mesh parent and Armature-modifier target;
- one intended visible hero rig/mesh, with no older lookalike rig in the cast;
- target-specific Action/NLA names and exact strip count;
- representative three-point coverage for every dance;
- background-dancer phase sheet when present;
- boundary-pair sheet and any transition masks;
- complete PNG frame range with no gaps;
- H.264/yuv420p encode, FPS, duration, dimensions, and counted frames via `ffprobe -count_frames`;
- decoded midpoint samples extracted from the actual MP4, not only source PNGs.

If whole-video analysis is unavailable, do not claim it ran. Use the rendered coverage, actual-MP4 extracted samples, frame count, full decode test, and fresh Blender inventory as the acceptance evidence.
