# Flutter Reference — Dart, flutter CLI, iOS + Android

> **Last Updated:** 2026-08-03

Load this reference when the project is built with **Flutter** — a single Dart
codebase compiled to native iOS and Android binaries. It complements the
shared workflow in `SKILL.md` and the platform references ([ios.md](ios.md),
[android.md](android.md)): Flutter delegates signing, lifecycle, and store
mechanics to the underlying platforms, so this file focuses on the Flutter
layer — scaffolding, builds, device workflows, and testing.

## Flutter fundamentals

- **Flutter SDK** — install the current stable channel (`flutter stable`).
  Pin the Flutter version (via the `flutter` SDK manager or the repo's
  `.fvmrc`/FVM config) so CI and machines build the same binary.
- **Project structure** — `lib/` (Dart source), `test/` (tests), `pubspec.yaml`
  (dependencies and assets), and platform folders `android/`, `ios/`,
  `linux/`, `macos/`, `web/`, `windows/`. Cross-platform code lives in `lib/`;
  the platform folders are generated and rarely edited directly.
- **Dependencies** — `pubspec.yaml` with the `pubspec.lock` committed for
  reproducibility; `flutter pub get` resolves them. Prefer the Flutter
  ecosystem packages maintained by the Flutter team.
- **Rendering** — Flutter renders its own UI with Skia/Impeller; fonts,
  text, and layout behave consistently across platforms, which simplifies
  cross-device visual testing.

## Scaffolding

```sh
flutter create --org com.example --project-name my_app --platforms ios,android my_app
```

- **Project name matters** — it becomes the Dart package name and the default
  bundle ID prefix; changing it later is disruptive. `--org` sets the bundle
  identifier base (`com.example.my_app`).
- **App entry point** — `lib/main.dart` runs `runApp()` with the root widget;
  keep it thin and delegate to feature-level code.
- **State management** — choose per app size: `setState` for local state,
  Provider/Riverpod/Bloc for shared state. Keep state logic testable in Dart
  without a device.
- **Platform tooling** — iOS targets still need Xcode, Android targets still
  need the Android SDK/JDK; `flutter doctor` verifies the whole toolchain.

## Builds and signing

### Build commands

```sh
# Debug build + hot reload on a connected device
flutter run

# Release APK (Android)
flutter build apk --release

# Release App Bundle (Android, for Play Store)
flutter build appbundle --release

# iOS archive + export (requires macOS + Xcode; produces .ipa via Xcode)
flutter build ipa --release
```

### Signing

Flutter delegates signing to the platform toolchains:

- **Android** — signing is configured in `android/app/build.gradle.kts`
  exactly as for a native app: keystore + `signingConfigs`, with secrets via
  environment or a gitignored `key.properties`. `flutter build appbundle`
  produces the AAB that Play signs via Play App Signing.
- **iOS** — `flutter build ipa` runs the Xcode archive/export flow under the
  hood; configure automatic signing (developer team) in the Xcode project or
  supply an `ExportOptions.plist`. TestFlight and App Store upload work the
  same way as native iOS.
- **Flutter specific** — `flutter build` embeds the Dart AOT snapshot into
  the platform binary; `--release` differs from `--debug` in tree shaking and
  compilation, so test the release build.

## Devices and emulators

```sh
flutter devices          # list connected devices and emulators
flutter emulators        # list available emulators
flutter run -d <device>  # run on a specific device
```

- **Hot reload** — `flutter run` supports hot reload (state preserved) and hot
  restart (state reset) for fast iteration; hot reload does not run on
  release builds.
- **iOS simulator** — boot via Xcode or `open -a Simulator`; `flutter run -d
  "iPhone 16"`.
- **Android emulator** — start an AVD first; `flutter run` picks it up.
- **Physical devices** — USB debugging (Android) and trust the computer (iOS);
  test on real devices for networking, sensors, and performance.
- **Debug vs release parity** — `flutter run` (debug) enables hot reload but
  is slower and includes assertions; verify the release build (`flutter run
  --release`) before shipping.

## Lifecycle and backgrounding

- **App lifecycle** — `WidgetsBindingObserver` + `AppLifecycleState`
  (inactive/paused/resumed/detached) tells the widget tree about backgrounding
  and resumption. Persist state on `paused`, not on `resumed`.
- **Platform behavior underneath** — iOS and Android still enforce their own
  background rules; Flutter code stops executing when the app is suspended.
  Use platform channels or plugins (`WorkManager`, background fetch) for
  background work, and be aware that plugins wrap the platform APIs covered in
  [ios.md](ios.md) and [android.md](android.md).
- **Process death** — the OS can kill the app at any time; persist state to
  local storage rather than relying on widget state.

## Offline and sync

- **Local persistence** — `sqflite`/`drift` (SQLite) for structured data,
  `shared_preferences` for small settings, and file/asset storage for larger
  data. Keep database migrations versioned and tested.
- **Sync pattern** — persist locally first, queue mutations, and replay them
  against the API with retry and backoff when connectivity returns.
  `connectivity_plus` observes reachability; design for offline to degrade
  gracefully regardless.
- **Conflict resolution** — define an explicit strategy (last-write-wins,
  per-field merge, or conflict UI) so offline edits never silently clobber
  remote data.

## Testing

```sh
flutter test                       # unit + widget tests
flutter test integration_test      # integration tests on device/emulator
```

- **Widget tests** — fast, headless tests of widget trees (`WidgetTester`,
  `pumpAndSettle`); cover state, navigation, and rendering logic without a
  device.
- **Unit tests** — plain Dart tests for models, reducers, and services;
  dependency-inject network and storage so tests run offline.
- **Integration tests** — `integration_test` runs the real app on a device or
  emulator, driving the UI and asserting end-to-end behavior; run these on the
  device matrix (locally or on Firebase Test Lab) before release.
- **Golden/snapshot tests** — `matchesGoldenFile` renders widgets to images
  for visual regression; commit golden files with reviewed diffs.

## Store submission

Flutter apps ship through the same stores as native apps; the store-facing
work is platform mechanics:

- **Android** — upload `build/app/outputs/bundle/release/app-release.aab` to
  Play Console (internal/closed/open testing, data-safety declaration, staged
  rollout). See [android.md](android.md) for the full checklist.
- **iOS** — `flutter build ipa`, upload the `.ipa` to App Store Connect
  (TestFlight first), complete privacy labels and listing, submit for review.
  See [ios.md](ios.md) for the full checklist.
- **Version parity** — keep `version`/`build` aligned between `pubspec.yaml`
  and the platform configs so a release is identifiable across stores.

## Key references

- Flutter documentation (docs.flutter.dev) — current stable channel releases,
  platform integration guides, and release notes.
- Per-platform references in this skill — [ios.md](ios.md) and
  [android.md](android.md) for signing, lifecycle, and store mechanics.
