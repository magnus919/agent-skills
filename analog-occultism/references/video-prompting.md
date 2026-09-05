# Video Prompting Reference

## Shot template

```text
SHOT: [duration and framing]. [Subject] remains recognizable and grounded in the
space. One [screen/projector/industrial practical] is the dominant light source.

CAMERA: slow [push-in/pull-back/lateral track], stable mechanical movement, slight
servo hesitation, shallow focus breathing, no handheld energy.

ACTION: [one restrained physical action]. Allow long pauses and incomplete
information. Reveal [specific detail] gradually, then return to an unresolved state.

SURFACE AND SIGNAL: near-monochrome charcoal, smoked gray, dirty silver, and aged
ivory; crushed blacks; clipped highlights; restrained scanlines, interlacing, grain,
dust, scratches, halation, phosphor bloom, mild jitter, and occasional horizontal
interference embedded in the recording.

SOUND: [ambient machine hum / projector chatter / room tone]. No music unless
requested. No dialogue unless a visible speaker is specified.

AVOID: frenetic cuts, whip pans, action-camera movement, constant stimulation,
bright neon, decorative digital glitch, gore, jump scares, polished CGI.
```

## Motion rules

Use one primary motion and one or two secondary changes. Primary motion can be a
camera move, mechanical actuation, gradual reveal, or a slow change in focus. Secondary
changes can be screen flicker, exposure breathing, dust crossing the beam, or tracking
instability. Do not animate every object. Tension comes from duration, darkness,
partial evidence, and the anticipation of recognition.

A loop should not resolve the mystery. End with the subject returning to its initial
configuration, the light failing to reveal the key detail, or the observer stopping
just before recognition.

## Mode selection

- **Text to video:** use when the shot is conceptual and no opening composition must
  be preserved.
- **Image to video:** use when a supplied or generated still establishes the subject,
  framing, light, and surface treatment. Describe only the motion and temporal change
  that should occur.
- **Keyframes:** use when a transformation or state change must remain coherent. Keep
  the same subject location, dominant light, and negative-space structure between
  keyframes; vary only the intended state.
- **Continuation:** use when extending a shot. Preserve the established camera
  behavior, exposure, sound bed, and unresolved tension rather than introducing a new
  visual language.

For FLUX 3, read the `video-generation` skill and its prompting guide before invoking
any generation tool. Respect that skill's duration, frame-index, audio, and result
polling requirements.

## Video verification

Use FFmpeg or FFprobe to record container, stream, frame rate, duration, dimensions,
and audio details. Extract a bounded set of frames from the beginning, middle, motion
change, and end. Inspect those frames for:

- the subject remains recognizable;
- the dominant practical source remains dominant;
- blacks, highlights, and restrained tint remain coherent;
- movement is deliberate rather than frantic;
- signal treatment is embedded but does not obscure the subject;
- no accidental logos, text mutations, anatomy defects, color explosions, or digital
  corruption appear in sampled moments.

A sample validates sampled moments only. Record the sampling rule, timestamps, and
limitations in a concise inspection note, using the `ffmpeg` skill's video inspection
report when that workflow is active.
