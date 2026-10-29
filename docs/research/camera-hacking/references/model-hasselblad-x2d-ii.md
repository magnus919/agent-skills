# Hasselblad X2D II 400 MP reconstruction

Accessed 2026-10-29. Primary source: [Hasselblad X2D II 400 MP reconstruction project documentation](https://github.com/Jimmy6Smiles/Hasselblad-X2DII-400MP-Source). Findings below are source-attributed; no hardware reproduction was performed in this investigation.

## Target and feature

The project targets **X2D II 100C**, originally **1.3.16.2**, and documents a **1.3.18.1 / 1.2.5-rc3** adaptation. It claims six-frame acquisition with in-camera reconstruction, RAW/JPEG outputs and no HEIF support. The maintainer reports successful capture on the adaptation on 2026-10-22.

## Build and coexistence limits

The publication is a source snapshot, not a complete installer or bit-for-bit rebuild of the full MOD. It explicitly leaves some reused imaging binaries outside complete source-to-binary reproduction. A historical directory name is not a reliable package version.

Feature modules register with shared runtime infrastructure; installer/runtime versions and ABI dependencies matter. Do not overwrite shared startup integration or mix historical and newer distribution packages.

## Next evidence

Resolve the actual distribution, source identity, runtime compatibility and recovery record. Independently inspect final image quality, motion artifacts, lens/storage combinations and interrupted-capture behavior before relying on the feature. No such tests were performed here.
