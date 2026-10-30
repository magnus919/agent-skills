# ImageServer Imagery Reference

Raleigh publishes aerial photography, land-cover, temperature, and elevation products through a public ArcGIS ImageServer directory.

## Base Directory

```text
https://maps.raleighnc.gov/images/rest/services?f=pjson
```

The CLI recursively discovers services in folders such as `Ortho`, `Temperature`, `Heat`, `LandCover`, and `Elevation`.

## Service Metadata

```text
https://maps.raleighnc.gov/images/rest/services/{ServiceName}/ImageServer?f=pjson
```

Inspect `capabilities` to determine supported operations. Common capabilities include `Catalog`, `Image`, and `Metadata`.

## Operations

### Export Image

```text
{serviceUrl}/exportImage?bbox={xmin},{ymin},{xmax},{ymax}&bboxSR=4326&imageSR=4326&size={width},{height}&format=jpgpng&f=image
```

`format=jpgpng` asks the server to choose the cheaper encoding, so the bytes may be JPEG or PNG regardless of the requested name. The CLI infers the concrete format from the output extension (`.png` → `png`, `.jpg`/`.jpeg` → `jpg`, `.tif`/`.tiff` → `tiff`, `.gif` → `gif`, `.bmp` → `bmp`), falls back to `jpgpng` with a warning for unknown extensions, and validates the returned magic bytes against the request. An explicit `--format` wins over the extension; a mismatch is reported instead of writing mislabeled bytes.

### Identify

```text
{serviceUrl}/identify?geometry={pointJson}&geometryType=esriGeometryPoint&outSR=4326&f=json
```

### Statistics

```text
{serviceUrl}/computeStatisticsHistograms?geometry={envelopeJson}&geometryType=esriGeometryEnvelope&outSR=4326&f=json
```

## Spatial Reference Must Be Embedded

The `inSR`/`sr` query parameter is ignored on these services. Pass `4326` coordinates but put the spatial reference inside the geometry:

```json
{"x": -78.65, "y": 35.75, "spatialReference": {"wkid": 4326}}
```

Without it, `identify` answers `"value": "NoData"` and `computeStatisticsHistograms` issues a slow or timing-out request in the native NC State Plane (wkid 102719 / 2264) frame. Embedding the SR fixed both failures live; the statistics call then returned in under a second.

## Notes

- Do not append `/0` to an ImageServer root.
- Large exports require explicit bounds; the CLI does not attempt full-service downloads by default.
- Image exports return raw bytes; verify the encoding instead of trusting `Content-Type`.
- `Orthos2025` advertises `maxImageWidth: 15000`, `maxImageHeight: 15000`, `maxRecordCount: 1000`, and `currentVersion: 12.1`; check `maxImageWidth`/`maxImageHeight` per service before requesting large sizes.
- Folders `Imagery` and `Utilities` return ArcGIS error 499 (token required) and are reported as restricted rather than treated as failures.

