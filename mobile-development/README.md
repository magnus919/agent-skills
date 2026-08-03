# Mobile Development

Mobile development methodology for iOS, Android, Flutter, and React Native — project scaffolding, builds and code signing, device and emulator testing, store submission, app lifecycle and backgrounding, offline and sync, and mobile-specific testing. One skill for all four frameworks, with per-framework depth in references.

## Why Install This Skill

Your agent stops treating mobile apps as "a website that runs on a phone" and starts applying the actual discipline of mobile engineering: reproducible builds, correct signing, lifecycle-aware state handling, offline-first storage, and store submission that does not bounce in review. The catalog previously had zero mobile coverage; this skill closes that gap with one family skill that follows the same pattern as `frontend-engineering`.

After installing, your agent can scaffold a new app in any of the four stacks, set up and audit builds and code signing for iOS and Android, plan device and emulator testing, prepare TestFlight and Play Console submissions, reason about backgrounding and process death, design offline and sync behavior, and write mobile-appropriate tests — with framework-specific detail one reference away instead of buried in a generic prompt.

## What You Get

| Directory | Purpose |
|-----------|---------|
| `SKILL.md` | Core methodology: shared mobile workflow (scaffold → build and sign → test → ship), ownership boundaries, mobile-specific concerns (lifecycle, offline/sync, testing), trigger conditions, reference index |
| `references/ios.md` | iOS deep-dive: Xcode projects, certificates and provisioning, `xcodebuild` archive/export, simulators, lifecycle and backgrounding, App Store submission |
| `references/android.md` | Android deep-dive: Gradle and Kotlin, keystores and Play App Signing, APK/AAB builds, emulators and `adb`, lifecycle and WorkManager, Play Console submission |
| `references/flutter.md` | Flutter deep-dive: `flutter create`, `flutter build apk/appbundle/ipa`, signing delegation, hot reload, widget/integration tests, store shipping |
| `references/react-native.md` | React Native deep-dive: RN CLI vs Expo/EAS, Metro, app signing via platform toolchains, AppState, offline stores, Jest and Detox, store shipping |
| `evals/` | Output-quality eval manifest for the skill's methodology cases |

## Quick Start

Start by loading `SKILL.md` and the reference for the framework you are building:

```bash
# Native iOS — archive and export a signed .ipa for TestFlight
xcodebuild -workspace App.xcworkspace -scheme App -configuration Release \
  -archivePath build/App.xcarchive archive

# Native Android — produce the signed AAB Google Play requires
./gradlew bundleRelease

# Flutter — one codebase, both stores
flutter build appbundle --release   # Android → Play
flutter build ipa --release         # iOS → TestFlight / App Store

# React Native (Expo) — cloud builds with managed credentials
npx eas build --platform all --profile production
```

Then use the shared workflow: scaffold the project, build and sign it, test on a simulator/emulator *and* a physical device, and ship to a testing track (TestFlight, internal Play testing) before production review.

## Triggers

- Creating a new mobile app project for iOS, Android, Flutter, or React Native
- Building, signing, or archiving a mobile release (`.ipa`, APK, AAB)
- Testing on simulators, emulators, or physical devices; device-farm test planning
- Submitting to the App Store (TestFlight/App Store Connect) or Google Play (Play Console)
- Reasoning about app lifecycle, backgrounding, process death, offline storage, or data sync
- Reviewing mobile test coverage, performance, or store-readiness

## Requirements

- Platform toolchains as needed: Xcode (iOS, macOS), Android SDK/JDK + Gradle (Android), Flutter SDK (Flutter), Node.js + Metro (React Native)
- Apple Developer Program account for iOS signing and TestFlight; Google Play developer account for Android distribution
- No Python or runtime dependencies for the skill itself — it is reference material only
