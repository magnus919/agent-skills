# Panasonic LUMIX DC-S5 remote control

Accessed 2026-10-29. Primary source: [Panasonic LUMIX DC-S5 remote control project documentation](https://github.com/sapoepsilon/lumix-remote). Findings below are source-attributed; no hardware reproduction was performed in this investigation.

## Target and execution location

The project reports physical verification on **DC-S5 firmware 2.03**. A host Python service provides wireless camera control, live view, import and timelapse through reverse-engineered camera protocols. This is external software, not a replacement firmware feature.

## Compatibility boundary

Other listed LUMIX bodies use an untested generic profile. Screenshots from the bundled emulator are synthetic and do not establish hardware compatibility. A host emulator can test application behavior without proving actual BLE registration, stream decoding or recording control on another body.

## Next evidence

Check the exact transport/firmware profile and compare the official LUMIX SDK's model roster. Before control experiments, separate status requests from capture, recording, setting changes and file operations. This investigation made no connection and ran no control commands.
