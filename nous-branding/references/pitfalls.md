# Nous Branding — Pitfalls & Known Failure Modes

This document catalogs known failure modes, gotchas, and mitigations accumulated across multiple sessions of generating Nous-branded images. Use it as a troubleshooting reference when output doesn't match expectations.

---

## 1. Mascot Generation Failures

### 1.1 Sad / Melancholic Expression

**Symptom:** The Nous Girl looks sad, crying, or melancholic.

**Cause:** Image models default to a melancholic expression for manga-style characters when the prompt doesn't specify otherwise.

**Fix:** Always include: `"Neutral calm attentive expression — not sad, not crying"` in the character description. This must be explicit negation — "calm" alone is insufficient.

### 1.2 Dark / Black Headphones

**Symptom:** The mascot appears with black or dark-colored headphones matching the scene's palette.

**Cause:** The model matches the headphones to the scene's dominant colors instead of the brand's canonical white headphones.

**Fix:** Always state both the color AND the headphone structure: `"White over-ear headphones — the cushioned white band arches across the crown."`

### 1.3 Teardrop / Facial Markings

**Symptom:** A teardrop appears under the eye, or the face has tattoos, scars, or cyberpunk markings.

**Cause:** The model free-associates "manga" or "cyberpunk" with facial markings.

**Fix:** Include explicit exclusions: `"No tattoos, no scars, no markings, clean clear skin. No teardrop."`

### 1.4 Wrong Ethnicity

**Symptom:** The Nous Girl appears Asian instead of French/Caucasian.

**Cause:** Image models default to Asian features when the prompt specifies "anime" or "manga" style.

**Fix:** Explicitly state: `"French Caucasian, fair skin, light-colored eyes (blue or grey), delicate European features, about 13 years old — NOT Asian."`

### 1.5 Wrong Clothing / Costume

**Symptom:** The character is dressed in a hoodie, dark cyberpunk outfit, or elaborate costume instead of the brand's white collared shirt.

**Cause:** The model matches the character's clothing to the scene's aesthetic rather than the brand specification.

**Fix:** Always state `"white collared shirt"` and add `"not a hoodie, not a dark top"` for complex scenes.

### 1.6 Generic Anime Instead of Retro Manga

**Symptom:** Output looks like modern glossy anime rather than 1970s-80s cel-shaded manga.

**Fix:** Use the exact phrase `"1970s-80s cel-shaded manga style, high-contrast black ink on white paper"`.

---

## 2. Image Editing / Reference Workflow Pitfalls

### 2.1 Text Disappears from Edited Images

**Symptom:** When editing an image that contains text (meme captions, labels, headlines), the model corrupts or drops the text.

**Fix:** Regenerate with `"Keep all text exactly as shown. Do not change or remove any text."` Or add text as a post-processing step. This is a known limitation of the `/v1/images/edits` endpoint.

### 2.2 Square Input Requirement

**Symptom:** The edits endpoint rejects non-square input images.

**Fix:** The `generate-with-ref.py` script handles this by center-cropping to 1024x1024. Use `--pad` to pad with average edge color instead of cropping.

### 2.3 Reference Is Not a Guarantee

**Symptom:** Uploading the official Nous Girl badge as a reference doesn't guarantee the output matches the canonical design.

**Cause:** `/v1/images/edits` does not extract style embeddings like IPAdapter or ControlNet. The reference provides pixel-level context but style transfer is not guaranteed.

**Fix:** Always restate all key identifiers in the text prompt (white headphones, black hair, white collared shirt, neutral expression) AND all exclusions (no teardrop, no markings). Prefer the sketch sheet (`nous-girl-sketch-sheet.png`) over a single-pose badge for better character understanding.

### 2.4 Multi-Pass Editing Complexity

**Symptom:** Each editing pass degrades image quality or loses fidelity.

**Fix:** Limit to 3-4 passes maximum. Each pass handles ONE transformation. The working sequence: character swap → style conversion → demographic correction. More passes introduce cumulative artifacts.

### 2.5 Aspect Ratio Confusion

**Symptom:** Output is cropped or distorted when using non-square source images.

**Fix:** The edits endpoint outputs landscape (1536x1024), portrait (1024x1536), or square (1024x1024). Set the desired output size explicitly via the `size` parameter in `generate-with-ref.py` or via `--aspect` flag.

---

## 3. Safety / Moderation Blocks

### 3.1 OpenAI Moderation Rejects Horror Content

**Symptom:** The safety system blocks prompts containing ominous language, body horror descriptors, or threat-adjacent vocabulary.

**Fix:** Strip all emotional/response language from the prompt. Describe only neutral visual phenomena. Instead of "horrifying spiral consuming the town," use "spiral shapes in the clouds and on buildings." The concept survives through visual contrast alone — no need to label it as horror.

**Known blockers:** terrifying, disturbing, grotesque, contorted, twisted (when applied to figures), Uzumaki, body horror.

### 3.2 Threatening Character Descriptions

**Symptom:** `/v1/images/edits` blocks prompts with "henchmen," "weapons," "crime scene," or threatening-character groups.

**Fix:** Rephrase as neutral physical descriptions: "a group of men in dark suits" not "henchmen." Remove weapon references. Describe the scene's visual elements without labeling their intent.

---

## 4. Provider-Specific Quirks

### 4.1 OpenAI /v1/images/edits

| Issue | Workaround |
|-------|------------|
| Text vanishes from edits | Include explicit preservation instructions |
| Square input only | Use `--pad` flag to preserve non-square content |
| Extra auto-generated text (labels, headlines) | Explicitly specify "ONLY the following text: [exact text]. No other text anywhere." |
| Reference doesn't guarantee fidelity | Restate all identifiers in prompt |

### 4.2 DALL-E 3 (Text-Only)

| Issue | Workaround |
|-------|------------|
| Can't use reference images | Must specify all details in the prompt text |
| Sad default expression | Explicit negation required |
| Wrong headphones | Must specify color and structure |
| Safety system blocks horror | Strip emotional language, describe visual phenomena only |

### 4.3 ComfyUI / IPAdapter

| Issue | Workaround |
|-------|------------|
| Reference can overpower prompt | Lower denoise to 0.6-0.7 |
| Texture/loss of analog feel | Post-process with `scripts/postprocess.py` |
| Style transfer incomplete | Use Reference-Only ControlNet not just IPAdapter |

---

## 5. Prompt Engineering Anti-Patterns

### 5.1 Not Specifying Emotional State

The single most important lesson: if the prompt says anything about the character's emotional state without specifying "not sad," the model defaults to sad. Always end character descriptions with explicit negations of the default failure modes.

### 5.2 Not Specifying Ethnicity

For manga-style characters, the model defaults to Asian features. Always state "French Caucasian" for the Nous Girl.

### 5.3 Assuming Reference Images Replace Text Description

Uploading a reference image does NOT replace the need for a detailed text prompt. The reference influences style and composition, but the model still needs to know what to generate. Always provide:
- Character identifiers (hair, headphones, shirt)
- Palette constraints (hex values if possible)
- Expression (with exclusions)
- What NOT to include (teardrop, markings, dark headphones)

---

## 6. Pipeline / Tooling Pitfalls

### 6.1 `generate-with-ref.py` Crashes

If the script crashes, check:
- Python dependencies: `pillow` installed?
- Reference path exists: `ls -la assets/`
- Config file readable: `~/.hermes/config.yaml`
- Active image provider set in config

### 6.2 Post-Processing Too Aggressive

If `scripts/postprocess.py --mode imprint` destroys too much detail, reduce intensity or switch mode:
- `--intensity 0.45` for fine linework
- `--mode nous` for legacy luminous targets (no xerox/registration/scuffs)
- `--mode standard` for light touch only

### 6.3 Reference Images Are Placeholders

The assets in `assets/` are full-resolution reference images. If the skill was installed via `cp -r` and the assets directory is empty, sync from the repo:
```bash
cp -r /path/to/agent-skills/nous-branding/assets/ ~/.hermes/skills/creative/nous-branding/assets/
```

---

## Quick Reference: Fixes for Common Problems

| Problem | Fix |
|---------|-----|
| Sad expression | Add "not sad, not crying" to prompt |
| Black headphones | Specify "white over-ear headphones" + "cushioned white band arches across crown" |
| Teardrop/markings | Add "no tattoos, no scars, no markings, no teardrop" |
| Wrong ethnicity | Add "French Caucasian, NOT Asian" |
| Wrong clothing | Add "white collared shirt, not a hoodie" |
| Glossy anime instead of manga | Use "1970s-80s cel-shaded manga style, high-contrast black ink on white paper" |
| Text disappears in edits | Add "Keep all text exactly as shown" or add text post-process |
| Image too clean | Run `python3 scripts/postprocess.py input.png output.png --mode imprint --intensity 0.7` |
| Reference not matching | Use sketch sheet, restate all identifiers in prompt |
