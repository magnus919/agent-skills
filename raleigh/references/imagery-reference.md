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

### Identify

```text
{serviceUrl}/identify?geometry={pointJson}&geometryType=esriGeometryPoint&inSR=4326&outSR=4326&f=json
```

### Statistics

```text
{serviceUrl}/computeStatisticsHistograms?geometry={envelopeJson}&geometryType=esriGeometryEnvelope&inSR=4326&outSR=4326&f=json
```

## Notes

- Do not append `/0` to an ImageServer root.
- Large exports require explicit bounds; the CLI does not attempt full-service downloads by default.
- Image exports return raw bytes; the file extension should match the requested format.
