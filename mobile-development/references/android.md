# Android Reference — Kotlin, Gradle, Google Play

> **Last Updated:** 2026-08-03

Load this reference when the target platform is **Android** — native Kotlin
apps built with Gradle, or an Android target inside a Flutter or React Native
project (tooling for those is in [flutter.md](flutter.md) and
[react-native.md](react-native.md); this file is the platform layer under
them). It complements the shared workflow in `SKILL.md`; this file is the
Android-specific detail for scaffolding, building and signing, emulator and
device testing, and Play Store submission.

## Android fundamentals

An Android app is a compiled, signed package built by Gradle:

- **Gradle project** — a project root with `settings.gradle(.kts)`, an `app`
  module with `build.gradle(.kts)`, and `gradle/libs.versions.toml` for version
  catalog dependency management. Kotlin DSL (`.kts`) is the current default.
- **Manifest** — `AndroidManifest.xml` declares the application, activities,
  services, receivers, permissions, and the minimum/target SDK.
- **Build outputs** — `assembleDebug`/`assembleRelease` produce APKs;
  `bundleRelease` produces an **Android App Bundle (AAB)**, the required
  submission format for new apps on Google Play (since 2021, and still the
  rule). Google Play derives per-device APKs from the AAB via **Play App
  Signing**.
- **Gradle wrapper** — commit `gradlew` and `gradle/wrapper/` so builds use a
  pinned Gradle version on every machine and CI runner.

Keep the version name (`versionName`) and version code (`versionCode`, a
monotonic integer) in `build.gradle.kts` — Play rejects a build whose version
code is lower than a previous upload.

## Scaffolding

- **New native app** — create the project in Android Studio or with the Gradle
  template (`gradle init`); choose Kotlin and Jetpack Compose for new UI.
- **Minimum and target SDK** — set `minSdk` to the oldest Android version in
  scope and keep `targetSdk` current; Play enforces minimum target API levels
  for new and updated submissions, and raised target levels are announced
  annually.
- **Dependencies** — prefer version catalogs (`libs.versions.toml`) and commit
  the lockfile (`gradle.lockfile` or dependency locking) for reproducibility.
- **App structure** — a single-activity app with Compose navigation for new
  work; keep the manifest minimal and declare only the permissions the app
  actually uses.

## Builds and signing

### Signing model

- **Local signing** — a Java keystore (`.jks`/`.keystore`) with an alias,
  configured via `signingConfigs` in `build.gradle.kts`. Signing configs must
  never be committed with their passwords; read them from environment
  variables or a secrets store at build time.
- **Play App Signing** — Google holds the app signing key; the **upload key**
  you sign with is only used to upload the AAB to Play. Upload keys can be
  rotated without user-visible changes; losing the upload key requires Play
  Console support intervention.
- **Keystore custody** — the release keystore is a production secret: back it
  up, store it outside the repository, and restrict access. Losing it means
  the app can no longer be updated under the same identity.

### Signing practices

- **Debug builds sign automatically** with the debug keystore — never ship
  them.
- **Release builds in CI** — inject keystore path, passwords, and aliases via
  CI secrets; keep `keystore.properties` (or equivalent) out of version
  control. Use `signingConfig` referenced from a file that CI can generate.
- **Two build types** — `debug` and `release` differ in signing, shrinking
  (R8/ProGuard), and manifest merging. Smoke-test the signed release artifact,
  not just the debug build.

### Build commands

```sh
# Debug APK (fast iteration)
./gradlew assembleDebug

# Release APK (signed, shrunk)
./gradlew assembleRelease

# Release App Bundle (required for Play Store submission)
./gradlew bundleRelease
```

The AAB lives in `app/build/outputs/bundle/release/`; the signed APK in
`app/build/outputs/apk/release/`. Verify the APK signature with
`apksigner verify --print-certs app-release.apk` before distribution.

## Emulators and devices

- **Emulators (AVD)** — Android Studio AVD Manager creates virtual devices;
  headless emulators are scriptable for CI:

  ```sh
  emulator -avd Pixel_8 -no-window -no-audio -no-boot-anim &
  adb wait-for-device
  adb install app/build/outputs/apk/debug/app-debug.apk
  adb shell am start -n com.example.app/.MainActivity
  ```

- **Physical devices** — enable USB debugging and use `adb devices` to verify
  the connection; real devices reveal networking, battery, and sensor
  behavior the emulator hides.
- **Debugging** — `adb logcat` for logs, `adb shell dumpsys` for system
  state, and Android Studio Profiler for CPU/memory/network. `adb reverse`
  maps device ports to the host for local API servers.
- **Device matrix** — cover the min SDK, the current SDK, and a mid-range
  device; use Firebase Test Lab (or a farm) for broad matrix coverage without
  local hardware.

## Lifecycle and backgrounding

- **Component lifecycle** — Activities/Fragments move through
  started/paused/stopped states; ViewModels survive configuration changes and
  should own UI state. `Process death` can destroy everything else.
- **State persistence** — save and restore instance state (`SavedStateHandle`,
  `rememberSaveable` in Compose) for process death; persist anything important
  to a durable store.
- **Background work is restricted** — Android restricts background execution
  and network. Use `WorkManager` for deferrable, guaranteed work, and
  foreground services (with a visible notification) only for user-visible
  tasks. `AlarmManager` is for alarms, not general scheduling.
- **Doze and app standby** — the system batches background work when idle;
  test offline sync and push handling under Doze, not just with the screen on.

## Offline and sync

- **Local persistence** — Room (SQLite ORM) for structured data, DataStore
  (Preferences/Proto) for settings, and file storage under the app's
  internal/external storage. Keep the database schema versioned with
  migrations tested.
- **Sync pattern** — write locally, then sync: queue writes, replay them with
  retry and backoff when connectivity returns, and resolve conflicts
  explicitly. `WorkManager` with network constraints is the idiomatic sync
  trigger.
- **Connectivity** — use `ConnectivityManager`/NetworkCallback to observe
  connectivity, but design for a lost network degrading gracefully.

## Testing

- **Unit tests** — JUnit + MockK/mockito for logic; Robolectric runs
  Android-framework code on the JVM for fast local tests.
- **Instrumented/UI tests** — Espresso (Views) or Compose UI tests
  (`createAndroidComposeRule`) drive the real app on an emulator/device.
- **Snapshot tests** — Compose Preview-based snapshot testing (e.g.,
  Roborazzi, Paparazzi) catches UI regressions without a device.
- **Device farms** — run the instrumentation suite on Firebase Test Lab
  across the device matrix; a test passing on one API level is not a
  guarantee across them.

## Store submission

1. **Play Console setup** — the $25 developer account, app record, and
   developer verification (new developers complete identity verification and
   a closed-test requirement with at least 12 testers for 14 days before
   production access).
2. **Upload the AAB** — upload `app-release.aab` to an internal, closed, or
   open testing track first; run internal testing with your own devices before
   production. Play generates and signs per-device APKs via Play App Signing.
3. **Store listing and policies** — screenshots, feature graphic, privacy
   policy URL, and a **data safety** declaration matching what the app
   collects. Play policy review rejects apps for undeclared data collection,
   broken core functionality, and misleading metadata.
4. **Staged rollout** — use phased rollouts (e.g., 10% → 50% → 100%) and
   monitor crash and ANR rates in Play Console before full release. Pause the
   rollout immediately if a serious regression appears.

## Key references

- Google Play Console help and policy center (support.google.com/googleplay)
  — current data-safety and testing-track requirements.
- Android developer documentation (developer.android.com) — target API
  level deadlines and app bundle guidance change annually.
