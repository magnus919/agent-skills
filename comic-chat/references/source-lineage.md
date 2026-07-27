# Source Lineage

The bundled assets derive from Microsoft’s [`comic-chat`](https://github.com/microsoft/comic-chat) repository at revision `48a162249484ab8d116c243e8203b0956d350c09`, using `v2.5-beta-1/comicart`. `assets/LICENSE` preserves the upstream MIT license and copyright notice.

`convert_art.py` converts every v2.5 BGB backdrop into a lossless PNG and every v2.5 AVB avatar into PNG foreground/mask layers plus a JSON manifest. The source format uses magic `0x8181`, zlib-compressed DIB pixels, source palette records, and an offset-adjustment record. The converter validates headers, dimensions, palette encoding, offsets, and decompressed byte counts before writing PNG output.

The renderer reads only the bundled PNGs and manifests at runtime. For complex avatars it preserves source layer coordinates, `HEADMASK`, `TORSOMASK`, and `TORSOFIRST` order, using the documented `MERGEPAINT` then `SRCAND` behavior. It is a narrow, deterministic renderer rather than a claim of pixel-perfect Windows-app emulation.

To regenerate the pack from a controlled checkout of the pinned source:

```sh
python3 scripts/convert_art.py \
  --source-dir /path/to/comic-chat/v2.5-beta-1/comicart \
  --output-dir assets/v2.5-beta-1/backdrop \
  --avatars-output-dir assets/v2.5-beta-1/avatars
```
