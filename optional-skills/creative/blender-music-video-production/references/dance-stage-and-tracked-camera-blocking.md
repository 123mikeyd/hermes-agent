# Dance stage and tracked-camera blocking

Use this reference after a finite dance library has artist-approved semantic names, categories, corrected Body Actions, and separate RootMotion Actions. The goal is a reviewable stage-and-camera `.blend`, not a render.

## Choose a coherent reel

1. Sequence by motion language rather than catalog order. A reliable progression is grounded footwork → fluid/showman choreography → sharp mechanical movement.
2. Include every approved clip from the selected families only when the artist asks to see how they line up. Preserve unrelated meme or ensemble clips in the library but leave them inactive.
3. Record the exact sequence in scene metadata, timeline markers, and an embedded shot-plan Text block.
4. Build the stage scene as a versioned derivative of the verified animation library. Never add cameras, lights, or set geometry to the library master.

## Rebuild presentation Actions from approved pairs

When corrected Body and RootMotion Actions already exist, do not retarget the raw carriers again:

1. Assign each approved Body Action to the canonical rig and its paired RootMotion Action to the MotionRoot.
2. Evaluate every native frame and capture the pose-bone basis matrices plus the MotionRoot location relative to the clip's first frame.
3. Bake new presentation-only Body and RootMotion Actions in the chosen order.
4. At each boundary, blend body bases over a short reviewed interval (12 frames at 30 FPS is a validated starting point), but start the incoming root path at the exact accumulated outgoing endpoint.
5. Protect both presentation Actions with Fake User. Keep all reusable per-clip Actions untouched.
6. Fresh-reopen and assert nonzero within-clip pose motion and zero/negligible root displacement across every boundary.

## Size the stage from actual travel

1. Evaluate the full combined root path before creating geometry.
2. Compute its XY envelope and maximum radius around the envelope center.
3. Set the usable platform radius from that measured radius plus performer clearance; use a practical minimum for mostly closed-loop dances.
4. Keep the walkable platform top exactly at world Z=0 unless evaluated foot-contact evidence requires a deliberate offset.
5. Put generated objects in one clearly named collection and prefix them consistently so the stage can be replaced without touching the performer.
6. Use a simple readable hierarchy: dark surrounding floor, raised-looking but ground-aligned performance disk, perimeter accent, and sparse backdrop panels. Do not clutter the foot area.

## Diagnose shimmering or glitching floors

Treat floor flicker as a geometry problem until evidence proves otherwise.

1. Build a tight red-capable probe that reports every broad floor object's world-space minimum/maximum Z, material roughness/metallic values, and top-surface separation.
2. If two overlapping broad meshes have top faces at the same world Z (within a small tolerance such as `1e-4 m`), classify the symptom as z-fighting. Polygon count is not the cause; glossy or metallic shading may make the flicker more conspicuous but does not create the depth ambiguity.
3. Fix the geometry at the source: keep one authoritative walkable top at world Z=0, place edge skirts and surrounding floors measurably lower, and remove the redundant broad surface. Do not merely increase roughness and leave coplanar faces in place.
4. Narrow emissive rings or circuit inlays may sit slightly above or below the platform, but give them an explicit nonzero separation and keep them out of the foot-contact lane.
5. Fresh-reopen the derivative and rerun the same probe. The test turns green only when the redundant surface is gone and all broad floor tops are separated.

## Design the stage from character narrative

Do not default to anonymous concert panels when the character has a strong role or ideology.

1. Translate the character into three set-language decisions: **function** (what this place does), **provenance** (who built or reclaimed it), and **mood** (how it should feel while the character performs).
2. Express those decisions through a few large readable forms rather than prop clutter. For example, a technological insurgent can dance on a reclaimed uplink platform with a single matte polygonal floor, restrained circuit paths, an open signal portal, and slightly asymmetric relay towers. This communicates resistance technology without inventing literal lore text or logos.
3. Keep emissive accents subordinate to the performer. Use static, restrained colors during approval; avoid flashing inspection lights and avoid reflections that compete with feet.
4. Save the redesign as another versioned derivative so the artist can compare it against the prior stage without touching the animation library or approved sequence.
5. For a clean viewport review, hide light objects and tracking empties with viewport-only visibility, disable relationship lines/extras/selection outlines in the 3D View, keep their render visibility intact, open Camera Perspective at frame 1, and leave playback stopped.

## Audition third-party PBR wall materials safely

A material page may expose low-resolution previews even when its official full-resolution package requires an account, credits, or a separate download. A public image URL is not proof that the preview is licensed as the final production asset.

1. Inspect the asset page and distinguish the official downloadable package from gallery or map-preview derivatives. Never guess license rights, bypass an account wall, or describe a preview as the purchased/full-quality asset.
2. When the artist explicitly asks to see how it looks, a publicly served preview set may be used for a private, reversible look-dev derivative. Label it `PREVIEW`, record the source page URL, map resolution, and replacement requirement in material/scene metadata, and keep the images externally linked and unpacked.
3. Fetch the complete available preview set together—typically albedo, AO, height, metallic, normal, and roughness—and verify every file opens. Measure actual pixel dimensions; a filename containing `600` can still return a smaller image.
4. Use sRGB for albedo only. Set AO, height, metallic, normal, and roughness to Non-Color. Multiply AO into albedo conservatively, feed the normal texture through a Normal Map node, and combine height through a low-strength Bump node rather than destructive displacement during the audition.
5. Preserve authored aspect ratio. Strong symmetric hatches or panel motifs should become repeated square modules with explicit UVs, thickness, bevels, and dark framing—not one stretched texture across a broad wall. Repetition is part of the visual test and should remain easy to remove.
6. Put the audition wall in its own named collection inside another versioned stage derivative. Keep the approved stage, dance presentation Actions, and camera intact; place the wall behind the established portal/set silhouette rather than rebuilding the whole shot around an unapproved texture.
7. Fresh-reopen and verify map count, actual dimensions, file existence, packed state, color spaces, node links, module count, UV presence, modifiers, canonical sequence Actions, camera framing, and explicit `NOT RENDERED` status. Open exactly one clean Camera Perspective preview for artist judgment.
8. If approved, obtain the official full-resolution package through the normal licensed download path, swap image datablocks without changing UVs or material topology, and repeat viewport/render QA before production. If not approved, remove the isolated wall collection without touching the stage.

## Promote a wall audition without losing the performer

A technically correct PBR wall can still fail the shot by becoming brighter, busier, or more saturated than the character. Use an actual same-frame render as the visual-hierarchy gate.

1. Render one representative full-body frame before and after the wall revision at the intended raster and camera. Compare subject priority, silhouette clarity, floor occupancy, pattern repetition, and bright-line tangencies; viewport material preview is not enough.
2. Treat a strong symmetric hatch texture as **side-wall dressing**, not uniform wallpaper. Preserve a darker, low-detail recess directly behind the head and torso so hair, shoulders, and hand gestures read cleanly.
3. Break obvious repetition reversibly: mirror or rotate selected UV islands, stagger modules slightly in depth, and add modeled mullions/recess trim that cast real shadows. Do not distort the source aspect ratio or bake destructive edits into provisional maps.
4. Reduce wall value/saturation and environment emission before flattening the character grade. If the performer and set share green/cyan hues, add a restrained neutral or warm-neutral key plus a controlled contrasting rim; keep the background subordinate.
5. Inspect screen-space tangents at representative poses. Enlarging an entire portal or frame does **not** prove that a diagonal cleared the hair—the offending segment can remain aimed into the head. Move, dim, mask, or remove that individual segment, or adjust the camera, then rerender the same frame.
6. Tighten excess foreground only after projecting the evaluated character at each clip's start/mid/end. Preserve complete feet and widest gestures while making the performer larger; floor graphics should lead toward the character rather than become isolated secondary focal objects.
7. Re-render the exact comparison frame and report remaining flaws honestly. A meaningful improvement is not automatically final approval; keep the full animation render blocked until the artist accepts the wall, silhouette, and crop.

## Build a restrained tracked camera

1. Parent a target Empty to the MotionRoot at torso height. Track it with the camera using negative Z and Y up.
2. Keep camera movement separate from character root motion. Key a small number of section-level positions/lenses rather than chasing every step.
3. Establish visual grammar before detail: wider for grounded footwork, gentle side offsets for fluid choreography, and slightly tighter coverage for a sharp finale.
4. Use static key/fill/rim lighting during approval. Do not add pulsing or flashing inspection lighting.
5. Open the saved file in Camera Perspective at frame 1 with playback stopped so the artist can review choreography, stage, and camera together.

## Deterministic no-render QA

Before opening the viewport preview, fresh-reopen the exact output and verify:

- expected FPS, resolution, frame range, render engine, and explicit `NOT RENDERED` status;
- active presentation Body and RootMotion Actions;
- one marker per clip plus section-level camera markers;
- nonzero sampled pose motion in every clip;
- zero/negligible MotionRoot reset at every boundary;
- plausible sampled shoulder-to-hand reach;
- stage collection, expected lights, camera Action, lens Action, tracking target, and DOF target;
- the evaluated deformed mesh remains inside the camera frame at each clip's start, midpoint, and end by projecting vertices with `world_to_camera_view`;
- every sampled camera-space depth is positive;
- evaluated mesh/floor clearance is recorded and visually reviewed when coat tails or accessories extend below the foot plane;
- no frame-output directory or rendered frames were created.

Structural camera-space QA proves coverage, not aesthetics. The artist must still play the sequence in Blender and approve stage readability, transitions, camera energy, floor contact, and the character's visual dominance before any real shot render.
