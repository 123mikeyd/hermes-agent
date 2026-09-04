# Industrial PBR look-dev for character stages

Use this reference when a user supplies web-hosted wall or floor materials and wants to audition them in a Blender character-performance scene before obtaining final-resolution assets.

## Separate acquisition from look-dev

Classify every asset as one of:

1. **Official licensed download** — safe to pack or ship according to its license.
2. **Public preview maps** — suitable only for private look-dev; keep external and unpacked.
3. **Page render/thumbnail** — visual reference only, not a PBR material.

Do not bypass account, credit, or subscription controls. If only public preview maps are retrievable, record the source URL, actual pixel dimensions, acquisition status, and replacement requirement on the material and scene. Verify dimensions from the decoded image; a filename containing `600` may still resolve to a smaller image. Require an official full-resolution replacement before final rendering or distribution.

## Wire preview PBR maps correctly

- Albedo/base color: `sRGB`.
- AO, height, metallic, normal, roughness, and emissive masks: `Non-Color`.
- Multiply AO into albedo conservatively; do not let preview AO become a second directional-light bake.
- Feed normal through a Normal Map node and height through a restrained Bump node; avoid true displacement during a fast audition.
- Remap roughness into a safe range rather than accepting mirror-like preview values blindly.
- Tint and limit emissive masks. Static, low-output technical details are safer than flashing/pulsing stage lights.
- Keep image datablocks externally linked and unpacked while the asset is provisional.

Fresh-reopen the `.blend` and assert every expected map exists, points to a real file, has the intended colorspace, remains unpacked, and reaches the correct Principled input.

## Wall integration: protect the performer

A strong square hard-surface panel should remain a square modular UV panel rather than being stretched across a broad wall.

1. Build repeated square modules with real thickness and bevels.
2. Put high-detail texture mainly at the sides.
3. Create a darker, quieter central recess behind the performer's head and torso.
4. Break repetition reversibly with alternating U/V mirroring, 180-degree UV rotation, slight depth staggering, and real mullions/trim.
5. Reduce wall value and saturation until the performer—not the texture—is the first read.
6. Judge geometric/emissive lines in screen space. Scaling a whole portal may leave one diagonal tangent against the hair; move, dim, or remove the individual offending segment.

Tested look-dev values such as roughly half-value wall albedo are starting points, not universal constants.

## Floor integration: preserve footwork and stability

Do not cover the main dance area with a dense industrial floor merely because the map is seamless.

1. Keep one authoritative matte central performance surface.
2. Use detailed floor maps on outer service-deck modules, side walkways, or maintenance bays.
3. Size and place modules from the evaluated root-motion envelope, not by eye. Require explicit clearance between every module AABB and the sampled path envelope.
4. Avoid coplanar layers. Put narrow decorative modules at a measurable Z separation (a few millimetres is enough for look-dev), and solidify downward so their visible top stays fixed.
5. Add a separate dark frame below the textured top, also vertically separated from the platform.
6. Keep pale service modules dark enough that a foreground corner does not become the secondary focal point.
7. Start with minimal texture density. Prefer exactly one centered service panel on each side unless more are requested; repeated modules often make the floor busier without improving the story. If the artist specifies an exact count, remove both the unused textured tops and their frames, then verify the survivors are symmetric about the platform center, share the intended depth coordinate, remain vertically separated from the main floor, and still clear the sampled root-motion envelope.
8. Dense vents and chevrons may shimmer under motion; a still can reject obvious spatial aliasing but cannot prove temporal stability. Review animated camera playback before the full render.

## Diagnose floor shimmer before changing materials

When a floor flickers, first measure the world-space top Z of every broad overlapping surface. Two broad surfaces at the same height are a deterministic z-fighting repro; polygon count is not the cause, while high metallic/low roughness usually only makes the symptom louder. The fix is one walkable top surface plus separated skirts/inlays, not random roughness changes.

## Preserve interactive art-direction edits

When the artist adjusts geometry in the live viewport, treat those edits as approved source data rather than rebuilding from the prior generated file.

1. Check the title-bar dirty marker and save the live file before running a background derivative.
2. Inventory the edited objects' exact location, rotation, scale, dimensions, material slots, and modifier state from the saved file.
3. Build the successor from that exact saved version and fresh-reopen it.
4. Assert the edited transform/dimension values survived unchanged. Do not silently resize matching frames, neighboring modules, or other props unless the artist asks.
5. Keep one authoritative Blender window: save the live predecessor, verify the successor, close the predecessor gracefully, then open only the new review file.

## Separate rear architecture from ground lighting

A color request may target only one spatial role even when several objects share the same material.

- Enumerate explicit object allowlists such as rear portal segments, tower cores, and wall accents versus ground circuit paths and perimeter rings.
- Reassign materials only to the requested allowlist; verify the untouched group still references its original materials.
- Converting rear emissive bars to dark brushed metal can quiet the background while leaving ground lines to guide footwork. Verify that the replacement shader has no emission connection and that metallic/roughness values read as structure rather than black plastic.
- Do not assume changing a whole shared material is safe: duplicated material slots or per-object reassignment are preferable when ground and rear elements must diverge.

## Prepare a future wall-image slot without guessing content

1. Use a renderable UV-mapped plane, not an Image Empty, when the artwork must appear in the final render.
2. Record the intended aspect ratio, physical dimensions, source status, and `awaiting artwork` state as object/material metadata.
3. Give the slot a neutral placeholder and real frame thickness, but do not invent, crop, or substitute content before the artist supplies the image.
4. Keep preview images external until approved; pack or relink only the final licensed source.
5. Check foreground braces and portals in screen space after the real image is present. A frame can be material-correct yet still obstruct the active image area; move or hide individual braces only with the artwork visible and artist approval.

## Character-first lighting and camera QA

- Use a neutral or slightly warm key to separate a green/cyan character from a green/cyan environment.
- Add a controlled cool rim for hair, shoulders, arms, and coat edges.
- Keep the central background quieter than side architecture.
- Preserve full-body/foot framing for dance work even when tightening the camera.
- Project evaluated mesh vertices with `world_to_camera_view` at each clip's start/mid/end; require positive depth and in-frame X/Y bounds.
- Check contact shadows and the wall-floor junction. A featureless black strip often reads as an accidental void; add base trim, reflected light, or deliberate trench structure.

## A/B render loop

Render the same representative animation frame before and after each look-dev revision. Verify the actual PNG dimensions, then compare:

- performer versus background priority;
- silhouette tangents at hair, shoulders, arms, and props;
- wall repetition and apparent flatness;
- empty foreground area;
- floor detail versus readable feet;
- contact shadow and wall-floor transition;
- clipping, glare, and emissive competition.

A structurally valid material graph is not a visual pass. Stop for artist review when the revision is meaningfully better but one composition issue remains; do not silently iterate the whole set into a different design.
