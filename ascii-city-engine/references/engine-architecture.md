# Engine Architecture

## Coordinate and world model

Use a right-handed local coordinate system in meters: `x` east, `y` north, `z` up. The terrain is a regular grid with origin `(ox, oy)`, spacing `r`, and elevations `H[row][col]`. Bilinear interpolation defines the ground:

```text
terrain(x, y) -> z | null
u=(x-ox)/r; v=(y-oy)/r
z=(1-fu)(1-fv)H[j][i] + fu(1-fv)H[j][i+1]
  + (1-fu)fvH[j+1][i] + fu*fvH[j+1][i+1]
```

Return `null` when outside the grid or any interpolation corner is null. A null cell is darkness and is not walkable.

A building record contains:

```text
{id, footprint:[[x,y],...], base_elev_m, height_m, color,
 provenance:{source, url?, license?, retrieved?, confidence:0..1}}
```

The closed footprint is solid from `base_elev_m` to `base_elev_m + height_m`. The camera is `{x,y,heading_rad,fov_rad,eye_height_m}`; derive its vertical coordinates from terrain rather than storing an independent flying `z`.

## Pedestrian physics

At the accepted position:

```text
feet_z = terrain(x, y)
eye_z  = feet_z + eye_height_m
```

For proposed horizontal movement from `p0` to `p1`:

```text
z0 = terrain(p0.x,p0.y); z1 = terrain(p1.x,p1.y)
if z1 is null: reject
height_delta = abs(z1-z0)
horizontal = hypot(p1.x-p0.x,p1.y-p0.y)
slope = height_delta / max(horizontal, 1e-9)
if height_delta > max_step_m or slope > max_slope: reject
if player circle at p1 touches/intersects any building footprint: reject
otherwise accept; feet_z=z1
```

Use `max_step_m=0.45`, `max_slope=0.35`, and player radius `0.30 m` as starting values. Point-in-polygon plus minimum point-to-edge distance detects circle/polygon intersection. Treat equality as collision. If a diagonal proposal fails, test its x-only and y-only components separately to slide along walls without crossing them.

## Raycast-to-ASCII-grid pipeline

Render a fixed grid such as 100 columns by 36 rows on Canvas 2D. Each screen column casts a horizontal ray at angle

```text
ray_angle = heading - FOV/2 + (column+0.5)/columns * FOV
ray(t) = camera_xy + t * [cos(ray_angle), sin(ray_angle)]
```

March `t` from a near plane to `max_distance` (for example, 150 m) in increments no larger than half the terrain resolution. At each sample:

1. Evaluate terrain. Null means no ground sample.
2. Test whether the point lies in a building footprint. The first solid hit supplies wall distance, top elevation, stable color, and building ID.
3. Project vertical values using corrected distance `d=t*cos(ray_angle-heading)` to avoid fish-eye distortion:
   `screen_y = horizon - focal_px*(world_z-eye_z)/max(d,epsilon)` where `focal_px=(columns/2)/tan(FOV/2)`.
4. Fill the visible wall interval and terrain below it into character-grid cells only when nearer than that cell's depth buffer.
5. If the ray reaches maximum distance without geometry, explicitly reset the column to sky/darkness; never reuse a previous frame.

Pseudocode:

```text
clear(chars=' ', fg=sky, depth=infinity)
for sx in columns:
  ray = make_ray(sx)
  for t in march(near,max_distance,step):
    sample terrain and solids
    project visible span
    for sy in span: if corrected_distance < depth[sy][sx]: write cell
    if opaque building covers remaining span: break
paint character grid to Canvas 2D
```

## Glyph density, brightness, and color

Map normalized distance `q=clamp(d/max_distance,0,1)` to a concrete near-to-far density ladder:

```text
q < .12: '@'
q < .25: '%'
q < .42: '#'
q < .60: '+'
q < .78: ':'
otherwise: '.'
```

Scale foreground brightness with `brightness=0.25+0.75*(1-q)^1.4`; terrain can use `.,:;+=xX#@` according to both distance and local slope. Glyph cell dimensions stay fixed; apparent size changes through projected vertical span, while density and brightness fall with distance.

For stable building color, honor a valid pack-provided color. Otherwise hash the UTF-8 building ID with FNV-1a, select hue `hash % 360`, and use fixed saturation/lightness such as `hsl(hue 65% 58%)`. Recompute deterministically or cache by ID; never pick random colors per frame. Adjacent equal colors are acceptable.

Dynamic cars or pedestrians may be depth-tested billboard ASCII sprites anchored at `terrain(x,y)`. They are optional and do not alter static collision.

## Street furniture, signs, and surface cues

A dense pack adds three enrichment layers, all depth-tested against the same buffer:

- **Props (street furniture).** Each prop renders as a one-cell billboard at `terrain(x,y)` plus a small height offset, using the documented per-kind glyph (`traffic_signal=T, tree=t, bus_stop=B, bench=b, bollard=o, fire_hydrant=f, crossing==, street_lamp=i`; fallback `?`) and a per-kind color faded by distance. Props are spatially indexed (a grid keyed on the terrain resolution) so the per-ray-sample lookup stays near-constant; do not linear-scan the whole prop list per ray.
- **Signs (street-name text).** Each sign is a perspective-projected text billboard rendered as an overlay pass after the raycast loop. Project the world anchor to a screen column from its angle relative to heading, place the row from `terrain(x,y)` plus a sign height, truncate the text deterministically with distance, and write characters left-to-right through the depth buffer. Text always comes from a recorded source `name`, never generated.
- **Surface material and lighting.** Road surfaces may carry `surface` and `lit`. Map material to a ground glyph (for example asphalt `.`, concrete `:`, paving `;`, cobble `,`) and brighten lit roads slightly at night-style falloff, so the ground plane reads as pavement rather than void. Marked crosswalks (`crossing:markings` or `crossing` props) render as a distinct ground band at their recorded location.

The scaffold's HUD surfaces two wayfinding aids computed from the same data: the named street the player is standing on (nearest named surface within tolerance) and the name/address of the building the player faces within a proximity threshold. Both read from pack records, never hardcoded strings.

## Reference scaffold

`../assets/ascii-city-engine.html` is a single dependency-free file. It reads the pack's `manifest.json` for the spawn coordinate and first world tile (falling back to `world/tile-0.json`), builds terrain, footprint, prop, sign, and surface indices, applies the movement rules above, and renders colored characters on Canvas 2D. Serve the repository root over HTTP because browsers commonly block `fetch` from `file://` URLs.
