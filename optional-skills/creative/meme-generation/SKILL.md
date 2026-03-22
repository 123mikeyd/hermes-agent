---
name: meme-generation
description: Generate memes from a topic using template APIs, AI-generated art, or AI video (Veo, Kling, Hedra). Supports static images, animated video memes, lip-sync character videos, and post-processing with ffmpeg.
version: 2.0.0
author: adanaleycio, mikeyd, hermes-agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [creative, memes, humor, social-media]
    related_skills: [ascii-art]
    requires_toolsets: [terminal]
---

# Meme Generation

Generate memes using template-based APIs or fully custom AI-generated artwork with text overlays.

## When to Use

Use this skill when the user:
- wants to make a meme about a topic
- has a subject, situation, or frustration and wants a funny meme version
- asks for a relatable, sarcastic, or programmer-style meme idea
- wants caption ideas matched to a known meme format
- wants a completely original/custom meme (movie poster, fake presentation, etc.)

Do not use this skill when:
- the user wants a full graphic editor workflow
- the request is for hateful, abusive, or targeted harassment content
- the user wants a random joke without meme structure

## Quick Reference

| Input    | Meaning                                          |
|----------|--------------------------------------------------|
| topic    | The main subject of the meme                     |
| tone     | Optional style: relatable, programmer, sarcastic  |
| template | Optional specific meme template to use            |
| custom   | If true, generate original art instead of template |

### Template-to-Pattern Mapping

| Template ID        | Name                    | Lines | Best For                                    |
|--------------------|-------------------------|-------|---------------------------------------------|
| gru                | Gru's Plan              | 4     | A plan that fails at step 3 (repeat line 3 as line 4) |
| drake              | Drakeposting            | 2     | Rejecting one thing, approving another      |
| db                 | Distracted Boyfriend    | 3     | Line1=temptation, Line2=person, Line3=ignored thing |
| mordor             | One Does Not Simply     | 2     | Something that is harder than it sounds     |
| fine               | This is Fine            | 2     | Chaos, denial, pretending things are okay   |
| cmm                | Change My Mind          | 1     | Strong ironic opinion / hot take            |
| gb                 | Galaxy Brain            | 4     | Escalating irony or absurd superiority      |
| gandalf            | Confused Gandalf        | 2     | Confusion, forgetting, "I have no memory"   |
| buzz               | X, X Everywhere         | 2     | Something that is literally everywhere      |
| rollsafe           | Roll Safe               | 2     | Sarcastic "clever" advice                   |
| astronaut          | Always Has Been         | 4     | Revealing something was always true         |
| both               | Why Not Both?           | 2     | Refusing to choose between two options      |
| sparta             | This is Sparta!         | 2     | Aggressive rejection                        |
| success            | Success Kid             | 2     | Small victory celebration                   |

## Procedure

### Path A: Template-Based Meme (fast, one API call)

1. Read the user's topic and determine the core emotional pattern (chaos, distraction, dilemma, escalation, contradiction, failed plan, hot take).
2. Select the template that best matches that pattern using the table above.
3. Write captions that fit the template's line structure. Keep them short and punchy.
4. Generate the meme with memegen.link (free, no auth required):

```
GET https://api.memegen.link/images/{template_id}/{line1}/{line2}.png
```

- URL-encode each line with `urllib.parse.quote(text, safe='')`
- Lines are separated by `/` in the URL path
- Use `.png` extension for best quality
- To list all templates: `GET https://api.memegen.link/templates`
- To get template details: `GET https://api.memegen.link/templates/{id}`

Example:
```python
from urllib.parse import quote
import requests

line1 = quote("One does not simply", safe='')
line2 = quote("deploy on Friday", safe='')
url = f"https://api.memegen.link/images/mordor/{line1}/{line2}.png"
r = requests.get(url)
with open("/tmp/meme.png", "wb") as f:
    f.write(r.content)
```

5. If branding or extra overlays are needed, proceed to the Overlay step below.

### Path B: Custom/Object-Label Meme with Pillow (advanced, multi-step)

For memes that need avatar overlays, face replacements, or per-object labeling (like "Silent Protector", "Distracted Boyfriend" edits, etc.):

1. **Research first.** Before building, search Know Your Meme / imgflip / Google for popular versions of the template. Study how the best ones place labels, what font style they use, and what makes them effective. This avoids amateur-looking results.

2. **Download the blank template** via browser (imgflip blocks curl; use browser_get_images to find the CDN URL like `i.imgflip.com/XXXXX.png`, then curl that).

3. **Avatar overlays (face replacement):**
   - Download avatars from GitHub (`github.com/USERNAME.png`) or HuggingFace CDN
   - **Remove the background via alpha channel** -- the simple, correct way:
     - Detect white (or black) background pixels using a threshold
     - Set their alpha to 0 (transparent)
     - Paste with the alpha mask -- the character's natural shape sits on the scene
     - Choose EITHER white OR black to remove, almost never both. Check each avatar individually.
   - Do NOT use circular masks, white borders, feathered edges, or background-color painting hacks. Those look worse than simple alpha removal.
   
   ```python
   import numpy as np
   def remove_bg(image, color="white", threshold=230):
       """Remove white or black bg pixels via alpha channel"""
       data = np.array(image.convert("RGBA"))
       r, g, b, a = data[:,:,0], data[:,:,1], data[:,:,2], data[:,:,3]
       if color == "white":
           mask = (r > threshold) & (g > threshold) & (b > threshold)
       elif color == "black":
           dark = 255 - threshold
           mask = (r < dark) & (g < dark) & (b < dark)
       data[:,:,3] = np.where(mask, 0, a)
       return Image.fromarray(data)
   ```
   
   - **Mirror/flip** avatars with `img.transpose(Image.FLIP_LEFT_RIGHT)` if they face the wrong direction for the composition
   - Position over the character's head -- use `vision_analyze` to check placement

4. **Object/projectile labeling (the "anime arrows" technique):**
   - **Angle the text** to match the trajectory of the objects (~30-45 degrees)
   - Use NEGATIVE angles (e.g., -35) for objects falling from top-left to bottom-right
   - Use POSITIVE angles for objects going the other direction
   - Place labels **floating near** each projectile, not in boxes
   - White bold text with thick black outline (3px) -- the classic meme standard
   - This looks far more dynamic than horizontal text in dark boxes

   ```python
   def make_angled_text(text, font, angle, fill=(255,255,255,255), outline=(0,0,0,255), outline_w=3):
       dummy = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
       bbox = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font)
       tw = bbox[2] - bbox[0] + outline_w * 2 + 6
       th = bbox[3] - bbox[1] + outline_w * 2 + 6
       txt_img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
       td = ImageDraw.Draw(txt_img)
       ox, oy = outline_w + 3, outline_w + 3 - bbox[1]
       for dx in range(-outline_w, outline_w + 1):
           for dy in range(-outline_w, outline_w + 1):
               if dx != 0 or dy != 0:
                   td.text((ox + dx, oy + dy), text, font=font, fill=outline)
       td.text((ox, oy), text, font=font, fill=fill)
       return txt_img.rotate(angle, expand=True, resample=Image.BICUBIC)
   ```

5. **Subject/protector labels:** Use rounded-rectangle pill backgrounds with transparency `(0, 0, 0, 200)` for text over busy areas. Color-code: blue for protector, green for protected, red for threats.

6. **Iterate with vision_analyze** -- check each version, fix positioning, then re-render. Common issues: avatar placed too low, text cut off at edges, wrong angle direction.

### Path B2: "Welcome to Heaven" / Memorial Photo Composite

For tribute memes where real, recognizable people must appear together:

1. **DO NOT use AI image generation for multiple real people** — AI generators blend all faces together. Only works for single-person images.
2. **Generate a CLEAN backdrop** with AI (clouds, heaven, golden light — NO people in the prompt).
3. **Download real photos** from Wikimedia Commons (use browser + browser_get_images to get CDN URLs, then curl with Referer header — direct curl gets blocked).
4. **Remove backgrounds** with the `rembg` library (uses u2net model for segmentation).
5. **Fade bottom edges** so figures blend into clouds instead of harsh rectangular crops — gradient alpha from 100% to 0% over the bottom 25-30% of each cutout. Also fade side edges slightly (8%) to soften rectangular photo borders.
6. **Add heavenly glow** around each figure (dilate alpha + gaussian blur + warm white overlay).
7. **Layout**: Leave a CENTER GAP in the back row so the front-center figure isn't covering anyone. Don't center a back-row figure directly behind the front figure.
8. **Jokes/text on memorial memes**: Keep respectful — avoid jokes that put the subject above God or threaten divine authority. "Heaven just got its toughest angel" > "He allowed heaven to have him."

### Path C: Custom AI-Generated Meme (original artwork)

1. Use `image_generate` to create original artwork based on the concept.

   - Request space at top and bottom for text in the prompt.
   - Use portrait aspect ratio for poster-style, landscape for widescreen memes.
2. Use Pillow to add text overlays:
   - Title text: large bold font, gold or white with black outline.
   - Taglines: smaller italic/regular font below title.
   - Credits/footer: small font on semi-transparent dark bar at bottom.
3. Extend the canvas with black bars above/below if more text space is needed.

### Overlay Step: Adding Logos or Branding

When the user wants a logo or branding on the meme:

1. **Nous Research logo** is available from LobeHub CDN:
   ```
   https://registry.npmmirror.com/@lobehub/icons-static-png/latest/files/light/nousresearch.png
   ```
   - This is a 1024x1024 RGBA PNG
   - ALL pixels are (0,0,0) black with varying alpha for anti-aliasing
   - Background is already transparent (alpha=0)
   - Do NOT try to "remove white background" -- there is none

2. **To make the logo visible on dark backgrounds**, invert the RGB:
   ```python
   logo_data = logo.getdata()
   white_version = [(255, 255, 255, px[3]) for px in logo_data]
   logo.putdata(white_version)
   ```

3. **Create a circular badge** for clean presentation:
   ```python
   badge = Image.new("RGBA", (size, size), (0, 0, 0, 0))
   draw = ImageDraw.Draw(badge)
   draw.ellipse([0, 0, size-1, size-1], fill=(20, 20, 20, 190))
   logo_resized = logo_white.resize((size-10, size-10), Image.LANCZOS)
   badge.paste(logo_resized, (5, 5), logo_resized)
   ```

4. **Placement rules:**
   - Place logos in a CORNER of the image, not over faces
   - Place extra text (taglines, credits) ABOVE or BELOW the meme image
   - Use semi-transparent dark bars behind text on busy backgrounds
   - Extend the canvas with black bars if needed for clean text areas

### Text Styling with Pillow

### Font Priority

User prefers Courier New (Hermes = courier/messenger of the gods). Use in this order:
1. **Liberation Mono Bold** `/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf` (Courier New metric-compatible replacement, usually available)
2. **Mondwest** (if installed)
3. **Helvetica** or **DejaVu Sans Bold** as fallback

For meme-style text overlays:
```python
from PIL import Image, ImageDraw, ImageFont

# Courier New style (Liberation Mono Bold)
font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf", size)

# White text with black outline (classic meme style)
outline = 3
for dx in range(-outline, outline+1):
    for dy in range(-outline, outline+1):
        if dx != 0 or dy != 0:
            draw.text((x+dx, y+dy), text, font=font, fill=(0, 0, 0, 255))
draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
```

### Nous Research Team Assets (for Nous-related memes)

Avatars (download with curl, confirmed working):
| Person | Role | Avatar URL | Description |
|--------|------|-----------|-------------|
| Teknium | Head of Post Training | `https://cdn-avatars.huggingface.co/v1/production/uploads/6317aade83d8d2fd903192d9/erOwgMXc_CZih3uMoyTAp.jpeg` | Anime boy, green hair, red visor, leaves |
| Jeffrey Quesnelle | CEO, @theemozilla | `https://github.com/jquesnelle.png` | Minion character |
| Karan Malhotra | Head of Behavior, @karan4d | `https://github.com/conceptofmind.png` | Greek Odysseus marble sculpture |
| Bowen Peng | Researcher, @bloc97_ | `https://github.com/bloc97.png` | Vault Boy holding Nuka-Cola |

Note: Shivani Mitra (co-founder) has left Nous Research -- do not include her.

Logos:
- **Nous logo (LobeHub CDN):** `https://registry.npmmirror.com/@lobehub/icons-static-png/latest/files/light/nousresearch.png` -- 1024x1024 RGBA, black pixels with alpha. Invert to white for dark backgrounds.
- **Nous mascot:** Anime girl with bob haircut, headphones, waveform in hair. Blue line art. Copy at `https://files.catbox.moe/8oagmh.png`
- The GitHub org avatar (waveform) is NOT the real logo.

### Path D: AI Video Meme (Veo via Gemini API)

For short AI-generated meme videos (8 seconds, extendable to ~148s). Requires Google Gemini API credentials.

**Prerequisites:**
- `GEMINI_API_KEY` or `GOOGLE_API_KEY` environment variable
- The `google-genai` Python package (install via pip)
- Paid Google AI Studio plan (Veo is paid preview)

**Capabilities:**
- Text-to-video (8s clips, 720p/1080p/4K)
- Image-to-video (animate a still image — great for meme templates)
- Native audio generation (dialogue, SFX, ambient)
- Video extension (add 7s chunks, up to 20 times / ~148s total)
- Reference images for character consistency (up to 3)
- First/last frame interpolation

**Basic text-to-video:**

```python
import time
from google import genai
from google.genai import types

client = genai.Client()  # Uses GEMINI_API_KEY env var

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Frodo Baggins holds a glowing AI chip instead of the One Ring, "
           "Mount Doom erupts behind him, cinematic dramatic lighting, "
           "Man: 'One Nous will rule them all.'",
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        resolution="1080p",
        duration_seconds="8",
        person_generation="allow_all",
    ),
)

# Poll until done (11s to 6min depending on load)
while not operation.done:
    print("Waiting for video generation...")
    time.sleep(10)
    operation = client.operations.get(operation)

# Download result
generated_video = operation.response.generated_videos[0]
client.files.download(file=generated_video.video)
generated_video.video.save("/tmp/meme_video.mp4")
print("Done!")
```

**Image-to-video (animate a meme still):**

```python
from PIL import Image as PILImage

img = PILImage.open("/tmp/meme_template.png")

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="The character slowly turns to face camera with intense stare, "
           "dramatic zoom in, fire erupts in background, epic orchestral music",
    image=img,
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9", resolution="720p",
        duration_seconds="8", person_generation="allow_all",
    ),
)
```

**Video extension (make it longer):**

```python
# Only works with Veo-generated videos (stored 2 days), 720p only
extend_op = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Camera pulls back to reveal the full scene, dramatic reveal",
    video=generated_video.video,  # from previous generation
    config=types.GenerateVideosConfig(duration_seconds="8"),
)
```

**Veo prompt tips for memes:**
- Include dialogue in quotes: `Man: "That's no ordinary model."`
- Describe sound effects: "record scratch, dramatic bass drop"
- Use cinematic terms: "dolly shot", "slow motion", "dramatic zoom"
- Reference film styles: "shot like a Christopher Nolan film", "anime style"
- Don't use negatives ("no walls") — use the negative_prompt field instead
- Keep subject descriptions specific and visual
- For meme punchlines: describe the reveal/reaction moment in the prompt

**Adding text overlays after generation:**

Veo generates raw video without text. Add meme captions with ffmpeg drawtext:

```bash
ffmpeg -i meme_video.mp4 -vf \
  "drawtext=text='ONE NOUS WILL RULE THEM ALL':\
  fontsize=48:fontcolor=white:borderw=3:bordercolor=black:\
  x=(w-text_w)/2:y=h-80:\
  fontfile=/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf" \
  -c:a copy output_with_text.mp4
```

**Model versions:**

| Model | Speed | Audio | Max Res | Use Case |
|-------|-------|-------|---------|----------|
| veo-3.1-generate-preview | Normal | Yes | 4K | Best quality, cinematic |
| veo-3.1-fast-generate-preview | Fast | Yes | 720p | Quick iterations |
| veo-2.0-generate-001 | Normal | Silent | 720p | Legacy, no audio |

**Limitations:**
- Videos stored only 2 days — download immediately
- All output has SynthID watermark (invisible, for AI detection)
- Safety filters may block some prompts (not charged if blocked)
- Extension only works at 720p
- Latency: 11 seconds to 6 minutes per generation

## Path D: AI Video Meme (Veo / Google Gemini)

Generate short AI video memes using Google's Veo model through the Gemini API. Produces 8-second 720p/1080p/4K video clips with native audio. Powers "sigma edit" and "What if X was directed by Y" style meme videos.

**Requirements:** `GOOGLE_API_KEY` env var. Package: `google-genai`. Paid Google AI Studio plan.

### Text-to-Video (from a meme concept)
```python
import time
from google import genai
from google.genai import types

client = genai.Client()

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Frodo Baggins standing in Mount Doom, holding a glowing blue token, "
           "dramatic cinematic lighting, embers floating, he says: 'One Nous will rule them all', "
           "deep dramatic voice, fire crackling ambient sound",
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9", resolution="1080p", duration_seconds="8",
        person_generation="allow_all",
    ),
)

while not operation.done:  # Poll (11s to 6 min)
    time.sleep(10)
    operation = client.operations.get(operation)

video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("/tmp/meme_video.mp4")
```

### Image-to-Video (animate a static meme from Path A/B/C)
```python
image = types.Image.from_file("/tmp/static_meme.png")
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="The character slowly turns to camera, dramatic zoom, embers floating",
    image=image,
    config=types.GenerateVideosConfig(aspect_ratio="16:9", duration_seconds="8"),
)
```

### Chained Scenes (Sequential Generation)
Build a multi-scene narrative by feeding each clip's output as the seed for the next. Veo extends from the final second of the previous clip, maintaining visual continuity.

```python
# Scene 1: Establish
op1 = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="A hooded figure walks through a dark forest, torchlight flickering, distant thunder",
    config=types.GenerateVideosConfig(aspect_ratio="16:9", duration_seconds="8", resolution="720p"),
)
while not op1.done:
    time.sleep(10); op1 = client.operations.get(op1)
scene1 = op1.response.generated_videos[0]

# Scene 2: Continue from scene 1's ending
op2 = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=scene1.video,  # Seeds from final second of scene 1
    prompt="The figure stops and turns to camera, revealing glowing blue eyes, dramatic zoom in",
    config=types.GenerateVideosConfig(number_of_videos=1, resolution="720p"),
)
while not op2.done:
    time.sleep(10); op2 = client.operations.get(op2)
scene2 = op2.response.generated_videos[0]

# Scene 3: Continue again
op3 = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    video=scene2.video,
    prompt="Camera pulls back to reveal an army of glowing figures, epic wide shot, orchestral swell",
    config=types.GenerateVideosConfig(number_of_videos=1, resolution="720p"),
)
# ... poll and download

# Concatenate all scenes
# ffmpeg -f concat -safe 0 -i scenes.txt -c copy final_narrative.mp4
```

**Chain tips:**
- Max 20 extensions (148 seconds total) per chain
- 720p only for extensions (start scene can be higher)
- Each extension adds ~7 seconds
- Re-anchor periodically with a fresh reference frame to prevent artifact accumulation
- Change the prompt between scenes for narrative progression
- Download ALL scenes immediately — Veo stores them only 2 days

### Transition Effects (Frame Interpolation)
Generate smooth transitions between two specific frames. Give Veo a first and last frame, and it creates the motion between them. Perfect for meme reveals, dramatic before/after, or scene transitions.

```python
from google.genai import types

# Load start and end frames
first_frame = types.Image.from_file("/tmp/scene_start.png")
last_frame = types.Image.from_file("/tmp/scene_end.png")

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Smooth cinematic transition, slow camera movement, dramatic lighting change",
    image=first_frame,       # Starting composition
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        duration_seconds="8",
        last_frame=last_frame,  # Ending composition — Veo fills in the middle
    ),
)
```

**Interpolation use cases for memes:**
- **The Reveal**: Start with a normal image, end with the meme punchline version
- **Before/After**: Static meme → animated aftermath
- **Scene transitions**: End of one scene → start of the next, Veo generates a smooth morph
- **Drake format animated**: Drake rejecting (frame 1) → Drake approving (frame 2), Veo animates the turn

### Veo Prompt Tips
- Dialogue in quotes: `Man: "That's no ordinary ring."`
- Audio cues: "dramatic orchestra hit", "bass-boosted phonk music"
- Camera: "dolly shot", "slow zoom in", "dramatic low angle"
- Style: "cinematic", "film noir", "anime style", "dark fantasy"
- Negative prompts go in separate field, NOT in the main prompt
- Videos stored 2 days only — download immediately
- SynthID watermark embedded in all outputs

---

## Path E: AI Video Meme (Kling AI)

Generate video memes using Kling AI's image-to-video. Strong for character consistency, facial identity, and cinematic narrative. Up to 15 seconds per clip.

**Requirements:** Kling API key from klingai.com developer portal. Paid plan.

### Image-to-Video
```python
import requests, time, os

KLING_BASE = "https://api-singapore.klingai.com"
headers = {"Authorization": f"Bearer {os.environ['KLING_API_KEY']}", "Content-Type": "application/json"}

# Start generation
resp = requests.post(f"{KLING_BASE}/v1/videos/image2video", headers=headers, json={
    "model_name": "kling-v3",
    "image": "https://example.com/meme_image.png",
    "prompt": "Character slowly turns to face camera with menacing smile, dramatic lighting, smoke",
    "duration": "5", "mode": "pro", "sound": "on",
})
task_id = resp.json()["data"]["task_id"]

# Poll
while True:
    time.sleep(10)
    status = requests.get(f"{KLING_BASE}/v1/videos/image2video/{task_id}", headers=headers).json()["data"]
    if status["task_status"] == "succeed":
        video_url = status["task_result"]["videos"][0]["url"]
        with open("/tmp/kling_meme.mp4", "wb") as f:
            f.write(requests.get(video_url).content)
        break
    elif status["task_status"] == "failed":
        break
```

### Kling Advanced Features
- **Camera control**: `"camera_control": {"type": "forward_up"}` for dramatic swoops
- **Motion brush**: `"dynamic_masks"` with coordinate trajectories for precise animation
- **Multi-shot**: `"multi_shot": true` + `"multi_prompt"` array for storyboard sequences (up to 6 shots)
- **Voice**: `"voice_list"` with voice IDs, use `<<<voice_1>>>` in prompt for dialogue
- **End frame**: `"image_tail"` for start→end interpolation
- `"mode": "pro"` = slow but quality; `"mode": "std"` = fast, for testing
- Base64 images: raw string only, NO `data:image/png;base64,` prefix
- Assets retained 30 days

---

## Path F: Lip-Sync Video (Hedra)

Generate talking-head or singing videos where a character performs to audio. Perfect for music videos, meme narration, AI spokesperson content.

**Requirements:** Hedra API key from hedra.com/api-profile. Requires paid Creator plan or above.

### CLI Usage (via hedra-api-starter repo)
```bash
# Lip sync to audio file (singing, speech)
uv run main.py \
    --aspect_ratio 16:9 --resolution 720p \
    --text_prompt "Anime girl singing passionately, subtle head movement, maintain illustration style" \
    --audio_file /path/to/song_segment.mp3 \
    --image /path/to/character.png

# Text-to-speech mode
uv run main.py \
    --aspect_ratio 9:16 --resolution 540p \
    --text_prompt "A man speaking to camera" \
    --voice_id "f412c62f-e94f-41c0-bfc6-97f63289941c" \
    --voice_text "One does not simply deploy on Friday." \
    --image /path/to/character.png

# List available voices
uv run main.py --list_voices
```

### Hedra Prompt Tips for Stylized Art
- ALWAYS include "maintain the art style" or "do not change the illustration style"
- Use "subtle" / "gentle" / "slight" motion descriptors — too much breaks stylized art
- For illustrations: add "2D animation style, flat illustration, no 3D" to prevent realism drift
- Specify color palette explicitly: "monochromatic blue on black background"
- Best results: front-facing or 3/4 angle, mouth closed/slightly open, good lighting
- Start with 5-second test clips before full length to verify style preservation

### Hedra for Music Videos
1. Cut song into 15-30 second segments at verse/chorus/bridge boundaries
2. Match each segment to a character pose image that fits the energy
3. Generate lip-synced clips per segment with appropriate prompts
4. Assemble in video editor with transitions between poses
5. Layer effects (ASCII art, code, particles) on top in editor

### Hedra Models (accessible within the platform)
- **Hedra Omnia**: Best quality, jointly reasons over vision + text + audio
- **Kling 3**: Strong character consistency (also available standalone via Path E)
- **Veo 3.1**: Also available within Hedra (same model as Path D)
- **Seedance / MiniMax**: Additional style options

---

## Video Post-Processing (ffmpeg)

After generating video memes with any provider, use ffmpeg for finishing.

### Burn Text Captions onto Video
```bash
ffmpeg -i meme.mp4 -vf \
  "drawtext=text='ONE NOUS':fontfile=LiberationSans-Bold.ttf:fontsize=72:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=40, \
   drawtext=text='WILL RULE THEM ALL':fontfile=LiberationSans-Bold.ttf:fontsize=72:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=h-text_h-40" \
  -c:a copy output.mp4
```

### Add / Replace Audio
```bash
# Replace audio with music
ffmpeg -i meme.mp4 -i phonk.mp3 -map 0:v -map 1:a -shortest -c:v copy output.mp4

# Mix original + overlay
ffmpeg -i meme.mp4 -i music.mp3 -filter_complex \
  "[0:a]volume=1.0[a1];[1:a]volume=0.3[a2];[a1][a2]amix=inputs=2:duration=shortest" \
  -c:v copy output.mp4
```

### Convert to GIF
```bash
ffmpeg -i meme.mp4 -vf "fps=15,scale=480:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" -loop 0 output.gif
```

### Concatenate Clips
```bash
printf "file '%s'\n" clip1.mp4 clip2.mp4 clip3.mp4 > list.txt
ffmpeg -f concat -safe 0 -i list.txt -c copy final.mp4
```

---

## Provider Credential Check

| Feature | Required Key | Free Tier? |
|---------|-------------|------------|
| Static template meme (Path A) | None | Yes (memegen.link) |
| Custom Pillow meme (Path B) | None | Yes |
| AI-generated art meme (Path C) | FAL_KEY or built-in | Yes (via Hermes) |
| Veo video meme (Path D) | GOOGLE_API_KEY | No (paid Google AI) |
| Kling video meme (Path E) | KLING_API_KEY | No (paid Kling) |
| Hedra lip-sync (Path F) | HEDRA_API_KEY | No (Creator plan+) |

**Fallback**: If no video API keys are available, generate a high-quality static meme with Path A/B/C and suggest the user manually upload to Kling/Hedra/Veo web interfaces.

## Pitfalls

- Do NOT over-engineer with Pillow when memegen.link handles text placement perfectly in one API call. Use Pillow only for branding overlays or custom memes.
- Do NOT use imgflip API (requires account, CAPTCHA issues). Use memegen.link instead.
- Do NOT confuse the GitHub NousResearch org avatar (a waveform) with the actual Nous logo (anime girl with headphones). The real logo is on LobeHub CDN.
- Do NOT try to remove white backgrounds from the Nous logo -- it already has proper alpha transparency.
- Do NOT float logos or extra text over people's faces in template memes.
- Do NOT choose templates randomly; match the joke structure to the template pattern.
- Do NOT make captions too long -- short and punchy wins.
- Do NOT generate hateful, abusive, or personally targeted content.
- Do NOT place text labels in dark boxes for object-labeling memes -- use angled floating text with outlines instead (study popular examples first).
- Do NOT tilt projectile labels the WRONG direction -- negative angles for top-left-to-bottom-right trajectory, positive for the reverse.
- Do NOT skip the research step for custom template memes. Always look at 3-5 popular versions on Know Your Meme / imgflip before building to understand the visual conventions.
- Do NOT forget to mirror/flip avatars when the face points the wrong direction for the meme's composition.
- Do NOT use circular masks, white borders, feathered edges, or background-color painting to composite avatars. Just remove the bg color via alpha channel and paste. Simple > clever.
- Do NOT remove both white AND black backgrounds at the same time. Check each avatar and pick one. Some have white bg, some have dark/black bg.
- Do NOT use vision_analyze as the sole judge of whether text is cut off -- verify with actual pixel math (`textbbox()` vs image dimensions).
- imgflip blocks direct curl downloads; use browser_get_images to find the `i.imgflip.com` CDN URL, then curl THAT with a user-agent string.
- **Video pitfalls (Path D/E/F):**
- Do NOT forget to download Veo videos within 2 days — they expire.
- Do NOT add `data:image/png;base64,` prefix for Kling Base64 images — raw string only.
- Do NOT use high motion/creativity settings with stylized art in Hedra/Kling — it destroys the art style. Keep motion LOW.
- Do NOT skip the 5-second test clip when trying a new image+prompt combo for video — burn one cheap generation before committing to a full render.
- Do NOT try to generate videos without the required API keys — check the credential table first and suggest web UI fallback if keys are missing.
- Do NOT chain more than 20 Veo extensions — that's the hard limit (148 seconds total).
- Kling `image_tail`, `dynamic_masks`, and `camera_control` are mutually exclusive — only one per request.
- Hedra works best with front-facing or 3/4 angle source images. Profile shots produce poor lip sync.

## Verification

The output is correct if:
- The chosen template clearly matches the topic structure
- All captions are short, readable, and meme-appropriate
- The tone matches the user's request
- Any branding is cleanly placed in corners or above/below the image
- The result can be shared immediately without additional editing
- Text is fully readable and not obscured by image elements
