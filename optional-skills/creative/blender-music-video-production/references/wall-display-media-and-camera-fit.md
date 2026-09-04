# Wall displays, still artwork, and animated media

Use this reference when a Blender cinematic includes a framed wall display, poster, monitor, portrait, GIF, or video texture behind an animated character. The goal is a renderable, replaceable media surface whose content survives aspect-ratio handling and every animated camera beat.

## Preserve the supplied artwork

1. Copy the user-supplied source into a durable project asset directory without modifying the original.
2. Record source path, decoded dimensions, color space, provisional/final status, and whether the image is packed.
3. For an undecided artwork version, keep it externally linked and easy to replace. Pack only when portability is approved.
4. Never crop, stretch, generatively extend, recolor, or animate the supplied art without approval. Store the fit policy (`contain`, `cover`, or explicit crop) as metadata.
5. Use a renderable UV-mapped plane or shallow display mesh. An Image Empty is only a viewport reference and will not render.

## Contain square art inside a widescreen display

For a square image placed intact inside a 16:9 display, use dark sidebars rather than stretching or cropping:

1. Feed UV through a Mapping node.
2. Set X scale to `16/9`.
3. Set X location to `-(16/9 - 1)/2` (approximately `-0.3888889`).
4. Set the Image Texture extension to `CLIP`.
5. Mix the texture over a quiet dark background using the texture Alpha output.
6. Connect the result to Base Color and, if the display needs self-illumination, to low-strength Emission. Avoid a bright white billboard that competes with the performer.

Generalize the same method from source aspect `A_s` into display aspect `A_d`: scale the wider UV axis by `A_d/A_s`, center it with half the excess, clip outside 0–1, and mix over sidebars.

## Separate structure from screen content

- Put the screen, physical frame, foreground braces, wall material, and architectural light bars in separately named objects/collections.
- Change materials with explicit allowlists. A request to turn rear green/cyan bars into steel must not alter similarly colored floor circuits or perimeter rings.
- Prefer non-emissive brushed metal around a bright portrait. It gives edge highlights without creating a halo at character height.
- Do not move foreground braces merely because a placeholder looks crowded. Insert the real art first, render it, then decide whether braces frame, obstruct, or should sit behind the media surface.

## GIF and video textures

Do not rely on direct GIF playback for a production wall display. Preserve the GIF, inspect it with `ffprobe`, then create a deterministic derivative:

- **MP4 movie texture:** best for compact opaque playback.
- **PNG image sequence:** best for transparency and exact per-frame control.

Blender Image Texture data supports Movie and Image Sequence sources. Set and verify:

- source type;
- frame duration;
- start frame and offset;
- Cyclic only when an intentional loop is wanted;
- Auto Refresh for viewport review;
- color space and alpha mode;
- scene FPS versus source FPS.

Blender evaluates movie textures at scene frame rate, so convert or retime explicitly when rates differ. For a dance shot, keep the main wall content static unless animation adds story value. A restrained intro/outro loop or gentle motion is usually safer than a continuously active high-contrast GIF behind the performer.

## Camera-fit verification

Correct UV mapping does **not** prove the artwork is visible. A full uncropped image can still be cut off by the shot camera.

1. Compute the physical content rectangle inside the display, not only the outer screen bounds. For contained square art on 16:9, the content width equals the display height.
2. Transform the content corners into world space.
3. Project them through every relevant animated camera using `bpy_extras.object_utils.world_to_camera_view`.
4. Require positive depth and `0 < x,y < 1` with deliberate safety margin. Check the frame as well as the artwork if the frame must remain visible.
5. Test the widest establishing camera and representative dance cameras; camera animation can crop content differently at each beat.
6. If the content fails, test candidate display sizes/heights numerically before editing. A smaller/lower display can preserve the performer’s full-body framing better than globally widening every camera.
7. Render the same representative frames after the change. Structural projection checks prove containment, while rendered stills prove recognition, brightness, tangents, obstruction, and hierarchy.

## Labels and shot-level visibility

Treat a wordmark or caption above a display as a separate visual deliverable from the artwork.

1. Resolve the exact installed font file rather than trusting a family-name guess. Store the requested text, font path, case, material, and placement as metadata; assert the curve body matches exactly.
2. Prefer non-emissive or very restrained metallic lettering around a bright image. Verify the label in an actual render because small 3D text may be misread in Material Preview or by image analysis even when the curve data is correct.
3. Project and review three independent rectangles: artwork content, physical frame, and label. Passing the portrait does not prove the top frame or label is in shot.
4. Render both the establishing camera and representative close dance cameras. If the label is readable in the wide shot but leaves the tighter shot, decide whether that is intentional environmental storytelling or a failure of the shot requirement.
5. Do not repeatedly shrink a recognizable portrait merely to keep every surrounding element visible. When compositions conflict, preserve artwork legibility and choose one explicit policy: establishing-shot-only signage, a camera revision, a lower/inside-frame label, or shot-specific visibility.
6. Keep spelling verification deterministic. OCR or visual review judges legibility and hierarchy; the Blender text body and loaded font filepath prove the authored word and typeface.
7. For paired labels above and below a portrait, center both on the display's X axis and evaluate them independently. The upper word can leave a close shot while the lower word is hidden by the performer; decide whether the pair is establishing-shot branding or must survive every camera beat.
8. Do not “correct” authored punctuation from OCR alone. Bevel highlights can resemble a period and small monospaced/slab-serif text can be misclassified visually; `Curve.body` is the source of truth, while the render is the legibility check.

Run `scripts/verify_wall_display_camera_fit.py` in background Blender with `-- report.json ObjectName...` to project each display component at the scene bounds and every marker-defined camera beat before rendering.

## Review checklist

- Full source art visible with no unapproved crop or distortion
- Portrait eyes/head and all required frame edges inside camera
- Performer remains primary subject
- Screen brightness does not dominate the environment
- Foreground braces do not cross the face or important text
- No screen/bar tangent appears to grow from the performer’s head
- Wall art remains readable in wide and dance-pose frames
- User-adjusted stage props retain their saved transforms
- Ground emissives unchanged when only rear architecture was edited
- GIF/video derivative inspected, timed, looped, and refreshed deliberately
- Editable `.blend`, source media, and generated derivatives remain separately identifiable

## Authoritative Blender references

- https://docs.blender.org/manual/en/latest/render/shader_nodes/textures/image.html
- https://docs.blender.org/manual/en/latest/editors/image/image_settings.html
