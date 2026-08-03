# iOS Reference — Swift, Xcode, App Store

> **Last Updated:** 2026-08-03

Load this reference when the target platform is **iOS** — native Swift apps
built with Xcode, or an iOS target inside a Flutter or React Native project
(that tooling is covered in [flutter.md](flutter.md) and
[react-native.md](react-native.md); this file is the platform layer under
them). It complements the shared workflow in `SKILL.md`; this file is the
iOS-specific detail for scaffolding, building and signing, simulator and
device testing, and App Store submission.

## iOS fundamentals

An iOS app is a signed, structured bundle (`.app`) archived into an `.ipa` for
distribution:

- **Xcode project** — `.xcodeproj` (single target) or `.xcworkspace` (when
  using CocoaPods or Swift Package Manager workspace integration). The project
  file holds build settings, targets, schemes, and signing configuration.
- **Build products** — the `.app` bundle contains the compiled binary
  (Mach-O), `Info.plist` (bundle ID, version, permissions), entitlements, and
  resources. Xcode "Archive" produces the `.xcarchive` used for store upload.
- **Distribution artifacts** — `.ipa` (signed `.app` inside a `Payload/`
  directory) for TestFlight and App Store, and `.xcarchive` for archival and
  re-export. Ad-hoc and enterprise distribution reuse the same `.ipa` format
  with different signing profiles.

Keep `Info.plist` keys (bundle identifier, `CFBundleShortVersionString`,
`CFBundleVersion`, usage-description strings for camera/location/etc.) accurate
and reviewed — store review and crash reporting both depend on them.

## Scaffolding

- **New native app** — create the project in Xcode or with `xcodebuild`
  templates; choose SwiftUI for new apps (UIKit remains for legacy or
  fine-grained control). Set the deployment target to the minimum iOS version
  you committed to in scope.
- **Dependencies** — prefer Swift Package Manager (SPM) for new work;
  CocoaPods is still common in existing codebases. Commit the lockfile
  (`Package.resolved`, `Podfile.lock`) so builds are reproducible.
- **App structure** — keep the app entry point (the `@main` `App`/`AppDelegate`
  and scene) thin, and organize the rest by feature rather than by type.
- **Signing early** — set up a development team and automatic signing before
  the first device run; the simulator can build unsigned, but a device needs a
  valid signing identity and provisioning profile.

## Builds and signing

### Signing model

iOS signing has two assets, both managed per Apple Developer account:

- **Certificates** — a development certificate (for device installs) and a
  distribution certificate (for TestFlight/App Store). Certificates are tied
  to the account; distribution certificates can be shared between machines but
  should be kept in secure storage.
- **Provisioning profiles** — bind a certificate to app IDs and (for
  development) devices. Profiles expire and must be renewed; automatic signing
  in Xcode handles this when a developer account is configured.

### Signing practices

- **Automatic signing for development** — let Xcode manage profiles against
  the developer account for local device builds.
- **Release signing in CI** — export the distribution certificate and profile
  as secrets; never commit `.p12`, `.mobileprovision`, or private keys to the
  repository. Use `xcodebuild -exportArchive -exportOptionsPlist` with the
  `-exportOptionsPlist` file committed (it contains no secrets) so CI produces
  the same artifact as a local Archive.
- **Two app IDs, two signing identities** — a development build and a release
  build are different signed artifacts. Verify both sign correctly; a profile
  mismatch is the most common first-upload rejection.

### Build commands

```sh
# Build for a simulator (no signing needed)
xcodebuild -workspace App.xcworkspace -scheme App -configuration Debug \
  -sdk iphonesimulator build

# Archive for distribution (signs with the distribution identity)
xcodebuild -workspace App.xcworkspace -scheme App -configuration Release \
  -archivePath build/App.xcarchive archive

# Export an .ipa for TestFlight / App Store from the archive
xcodebuild -exportArchive -archivePath build/App.xcarchive \
  -exportOptionsPlist ExportOptions.plist -exportPath build/ipa
```

## Simulators and devices

- **Simulators** — `xcrun simctl` lists, boots, installs, and launches
  simulators headlessly, which makes it scriptable for CI smoke tests:

  ```sh
  xcrun simctl list devices
  xcrun simctl boot "iPhone 16"
  xcrun simctl install booted build/App.app
  xcrun simctl launch booted com.example.app
  ```

- **Physical devices** — a device build requires the device's UDID in a
  development provisioning profile. Verify on a physical device: real
  networking, background execution, push, and sensors behave differently from
  the simulator.
- **Debugging** — `xcodebuild` + Instruments for profiling; `log stream` and
  unified logging (OSLog) for diagnostics on device. Crash reports appear in
  Xcode Organizer and App Store Connect once TestFlight testers use the app.

## Lifecycle and backgrounding

- **Scene-based lifecycle** — modern iOS apps manage `Scene` lifecycle
  (active/inactive/background); the app delegate owns launch and termination.
  Persist state in `sceneDidEnterBackground` or at state transitions — do not
  assume the app will be resumed.
- **Background modes** — background execution requires a declared background
  mode (audio, location, background fetch, push notifications) in
  `Info.plist` capabilities. Apple reviews these declarations; use them only
  for their stated purpose.
- **Push notifications** — the app must register for remote notifications and
  handle both foreground presentation and background delivery; silent pushes
  are rate-limited by the OS.
- **Process death** — the OS can terminate the app at any time. Save
  user-visible state and restore it on launch rather than keeping it in
  memory.

## Offline and sync

- **Local persistence** — Core Data or SwiftData for relational models,
  `FileManager`/Documents for files, `UserDefaults` for small settings.
  Consider that `UserDefaults` is not a database.
- **Sync pattern** — persist locally first, then sync: queue writes in a local
  store, replay them against the API when connectivity returns, and resolve
  conflicts with an explicit strategy. `URLSession` with `waitsForConnectivity`
  and background URL sessions handle retries and large transfers.
- **Reachability** — use `NWPathMonitor` to react to connectivity changes, but
  design so a lost network degrades gracefully instead of crashing.

## Testing

- **Unit tests** — XCTest with the `@testable import` pattern; run in the
  simulator (`xcodebuild test`).
- **UI tests** — XCUITest drives the real app via accessibility identifiers;
  keep those identifiers stable and semantic.
- **Snapshot/visual tests** — libraries such as Swift Snapshot Testing render
  views to images for regression detection; keep fixtures in-repo and
  reviewed.
- **Performance** — measure launch time, frame rate, and memory with
  Instruments (or XCTest metrics) on a physical device; simulator numbers are
  not representative.

## Store submission

1. **TestFlight first** — upload the archive to App Store Connect
   (`xcrun altool`/`notarytool` or Xcode Organizer), distribute to internal
   and external testers, and let real devices exercise the app before review.
2. **App Store Connect setup** — the app record, bundle ID, pricing, and
   availability; export compliance questions; and the build must match the
   uploaded binary.
3. **Review readiness** — privacy nutrition labels for collected data,
   `Info.plist` usage descriptions, a complete store listing (screenshots for
   the required device sizes), and a working demo account or demo mode if the
   app requires sign-in. The App Review guidelines are enforced by humans;
   flaky sign-in, hidden features, and misleading metadata are common
   rejection causes.
4. **Staged release** — submit for review with a gradual release or schedule
   the release so a regression reaches few users first. Monitor crash rates
   after release.

## Key references

- Apple Developer Program and App Store Connect documentation
  (developer.apple.com/app-store/submitting).
- Xcode release notes and current SDK requirements near submission time —
  minimum Xcode and iOS SDK versions change annually.
