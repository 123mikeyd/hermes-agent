# Full-song Blender music-video extension

Use this when an artist supplies a finished song after a shorter animation preview already exists.

## 1. Inspect and make the creative decision explicit

- Run `ffprobe` on the supplied file. Record duration, sample rate, channel layout, codec, and any extra attached-picture stream.
- Compare exact song duration with `scene.frame_end / FPS`. Do not silently truncate a longer song or stretch audio to fit.
- Ask the artist to choose full song, fade/cut to the existing picture, or a selected excerpt when those outcomes differ materially.
- Preserve the supplied master unchanged. Copy it to a stable project `Assets/Audio/` path and verify the copy before linking Blender to it.
- Do not normalize, fade, or alter loudness unless requested. Album art and lyric metadata are not the playback stream.

## 2. Add the sound in Blender 5.2

Blender 5.2 exposes top-level sequencer strips through `SequenceEditor.strips`, not the older `sequences` collection:

```python
scene = bpy.context.scene
seq = scene.sequence_editor_create()
strip = seq.strips.new_sound(
    name="Song Title — Artist",
    filepath=str(audio_path),
    channel=1,
    frame_start=1,
)
strip.volume = 1.0
strip.pan = 0.0
scene.sync_mode = "AUDIO_SYNC"
```

Set FPS explicitly after imports. Derive the end frame from the decoded duration and verify the sound strip's actual start/end after a fresh reopen. Keep `scene.render.use_sequencer = False` when rendering the 3D scene to PNG; mux the audio into the encoded MP4 later.

## 3. Extend choreography without world resets

- Keep the verified source Actions protected with Fake User.
- If the hero has separate Body and MotionRoot Actions, repeat only the Body presentation Action with short NLA overlaps and let the original MotionRoot hold its final evaluated location. This produces additional dancing in place without teleporting back to the first path position.
- Set `use_auto_blend = False` before explicit `blend_in`/`blend_out` values.
- Extend every secondary performer independently. Exact loop repeat count is `ceil((scene_end - strip_start) / (action_frame_end - action_frame_start))`.
- For a multi-dance side performer, continue the established Action order and overlap policy rather than replacing the curated playlist with a single repeated clip.
- Require nonzero adjacent-frame pose deltas near the new final frame for every intended dancer.

## 4. Extend a multi-slot camera Action

A Blender 5.2 camera Action may contain both an Object slot and a Camera-data slot. Repeating the object transform alone can leave lens animation frozen.

1. Inspect `camera.animation_data.action_slot_handle` and `camera.data.animation_data.action_slot_handle`.
2. Build matching NLA cycles on both `camera` and `camera.data` from the protected Action.
3. Use a longer camera overlap than the body overlap when a gradual reframe is preferable.
4. Fresh-reopen and assert that object strips use the Object slot while data strips use the Camera slot.
5. Render the start, midpoint, and end of each camera overlap. Camera cropping of side performers is a framing failure, not proof their animation stopped.

## 5. Verification gate

Before a full-song render, verify:

- scene range and FPS match the sound strip;
- exactly the intended sound strip is unmuted at the requested volume;
- the external audio path resolves from the saved `.blend`;
- hero Body NLA covers song end while MotionRoot remains continuous;
- every backup/side dancer covers song end and has nonzero late motion;
- camera object and lens-data NLA both cover song end;
- contact sheets around each body/camera cycle boundary show no bind pose, teleport, stage loss, or severe camera jump;
- representative middle and final frames are populated and intentional;
- the scene remains marked `NOT RENDERED` until the artist approves viewport playback.

For final delivery, render a recoverable numbered PNG sequence, encode H.264 video, mux the untouched or approved audio stream, then use `ffprobe -count_frames` to verify frame count, duration, raster, FPS, codec, audio presence, sample rate, and channels.
