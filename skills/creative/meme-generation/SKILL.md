---
name: meme-generation
description: Generate memes from a topic using template APIs or original AI-generated art, with optional branding overlays.
version: 1.0.0
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

### Path B: Custom/Original Meme (creative, multi-step)

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

For meme-style text overlays:
```python
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)

# White text with black outline (classic meme style)
outline = 3
for dx in range(-outline, outline+1):
    for dy in range(-outline, outline+1):
        if dx != 0 or dy != 0:
            draw.text((x+dx, y+dy), text, font=font, fill=(0, 0, 0, 255))
draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
```

## Pitfalls

- Do NOT over-engineer with Pillow when memegen.link handles text placement perfectly in one API call. Use Pillow only for branding overlays or custom memes.
- Do NOT use imgflip API (requires account, CAPTCHA issues). Use memegen.link instead.
- Do NOT confuse the GitHub NousResearch org avatar (a waveform) with the actual Nous logo (anime girl with headphones). The real logo is on LobeHub CDN.
- Do NOT try to remove white backgrounds from the Nous logo -- it already has proper alpha transparency.
- Do NOT float logos or extra text over people's faces in template memes.
- Do NOT choose templates randomly; match the joke structure to the template pattern.
- Do NOT make captions too long -- short and punchy wins.
- Do NOT generate hateful, abusive, or personally targeted content.

## Verification

The output is correct if:
- The chosen template clearly matches the topic structure
- All captions are short, readable, and meme-appropriate
- The tone matches the user's request
- Any branding is cleanly placed in corners or above/below the image
- The result can be shared immediately without additional editing
- Text is fully readable and not obscured by image elements
