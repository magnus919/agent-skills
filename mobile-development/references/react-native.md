# React Native Reference — Metro, Expo, iOS + Android

> **Last Updated:** 2026-08-03

Load this reference when the project is built with **React Native** — a
JavaScript/TypeScript codebase rendering native UI components on iOS and
Android. It complements the shared workflow in `SKILL.md` and the platform
references ([ios.md](ios.md), [android.md](android.md)): React Native
delegates signing, lifecycle, and store mechanics to the underlying
platforms, so this file focuses on the React Native layer — scaffolding,
builds, device workflows, and testing, including the Expo toolchain.

## React Native fundamentals

- **Two toolchains** — the **React Native CLI** (`@react-native-community/cli`,
  bare workflow, owns the `ios/` and `android/` folders) and **Expo**
  (`create-expo-app`, managed workflow with `expo prebuild`/EAS for native
  code when needed). Expo is the recommended starting point for new apps; the
  CLI is for apps that need full native control from day one.
- **Metro bundler** — Metro compiles and bundles the JS/TS into the native
  binary; the Metro config (`metro.config.js`) controls transforms, and the
  Metro dev server powers fast refresh during development.
- **New Architecture** — current React Native releases (0.7x/0.8x line, with
  Expo SDK 56 bundling the stable line) default to the New Architecture
  (Fabric + TurboModules). Verify third-party libraries support the New
  Architecture before adoption.
- **Dependencies** — `package.json` with `package-lock.json`/`yarn.lock`
  committed; use the React Native/Expo version alignment (`npx
  expo install` keeps packages SDK-compatible).

## Scaffolding

```sh
# Expo (recommended for new apps)
npx create-expo-app@latest MyApp

# React Native CLI (bare workflow)
npx @react-native-community/cli@latest init MyApp
```

- **App entry point** — `App.tsx` renders the root component; keep it thin
  and route via React Navigation (or Expo Router) rather than hand-rolled
  navigation state.
- **Platform folders** — the CLI keeps `ios/` and `android/` in the repo;
  Expo hides them until `expo prebuild`. Treat generated platform folders as
  build outputs, not app code.
- **TypeScript** — use TypeScript from the start; the default templates are
  typed and the ecosystem type definitions are mature.
- **Environment config** — app config (`app.json`/`app.config.js` for Expo,
  `.env` for secrets via `expo-constants` or a config loader); never commit
  real secrets.

## Builds and signing

### Build commands

```sh
# Dev server with fast refresh (Metro)
npx expo start        # Expo: QR code / dev client
npm run start         # RN CLI: Metro dev server

# Android release APK/AAB
cd android && ./gradlew assembleRelease      # RN CLI
npx expo run:android --variant release      # Expo with prebuild
npx eas build --platform android --profile production   # EAS cloud build

# iOS archive + export (requires macOS + Xcode)
cd ios && xcodebuild -workspace MyApp.xcworkspace -scheme MyApp -configuration Release archive
npx eas build --platform ios --profile production          # EAS cloud build
```

### Signing

React Native delegates signing to the platform toolchains:

- **RN CLI** — Android signing via `android/app/build.gradle.kts` keystore
  config (as native Android); iOS via the Xcode project's automatic signing or
  an `ExportOptions.plist` (as native iOS). See [android.md](android.md) and
  [ios.md](ios.md) for the platform details.
- **Expo / EAS** — EAS Build can manage credentials: it generates and stores
  keystores and Apple certificates (with `eas credentials`), handles
  provisioning, and can run in a cloud environment without a Mac for iOS
  builds. Credentials live in Expo's secure storage or your own
  `credentials.json` (gitignored).
- **Signing secrets** — keystores, `.p12`, provisioning profiles, and Expo
  credentials are production secrets; never commit them, and back them up so
  an app can be updated under the same identity.

## Devices and emulators

```sh
npx expo start              # scan QR with Expo Go or a dev client
npx expo run:ios            # build and run on the iOS simulator
npx expo run:android        # build and run on an Android emulator
```

- **Expo Go vs dev client** — Expo Go runs the JS without a native build (fast
  iteration); a development build (dev client) is required for custom native
  modules. Test both the debug JS experience and the release bundle.
- **Fast refresh** — Metro hot-reloads edited JS while preserving state;
  restart the app (not just refresh) after native or config changes.
- **Physical devices** — Android: USB debugging or Expo Go via QR; iOS: Expo
  Go via QR on the same network. Real devices expose networking, permissions,
  and performance differences from simulators.
- **Debug vs release parity** — the release bundle is minified, tree-shaken,
  and runs without the dev server; smoke-test `--variant release`/production
  builds before store submission.

## Lifecycle and backgrounding

- **AppState** — `AppState` (active/background/inactive) is the
  cross-platform lifecycle signal; persist state on `background` and resume
  cleanly on `active`. `AppState.addEventListener` covers both platforms.
- **Background execution** — JS stops when the app is backgrounded; use
  platform mechanisms (headless tasks, background fetch, push) via native
  modules or libraries. iOS and Android background rules from
  [ios.md](ios.md) and [android.md](android.md) apply underneath.
- **Process death** — the OS can kill the app at any time; persist
  user-visible state to local storage rather than relying on in-memory React
  state.

## Offline and sync

- **Local persistence** — `AsyncStorage` (small key-value), `MMKV`
  (performant key-value), or SQLite-based stores (`react-native-sqlite-storage`,
  WatermelonDB, Realm) for structured offline data. Keep schemas versioned.
- **Sync pattern** — persist locally first, queue mutations, and replay them
  against the API with retry and backoff when connectivity returns.
  `@react-native-community/netinfo` observes reachability; design for offline
  to degrade gracefully regardless.
- **Conflict resolution** — define an explicit strategy (last-write-wins,
  per-field merge, or conflict UI) so offline edits never silently clobber
  remote data.

## Testing

```sh
npm test                 # Jest unit/component tests
npx detox test           # Detox E2E tests on iOS/Android
```

- **Unit/component tests** — Jest with React Native Testing Library;
  dependency-inject services and mock native modules so tests run headless.
- **E2E tests** — **Detox** drives the real app on a simulator/emulator with
  native synchronization; test critical user flows (sign-in, checkout, sync)
  on both platforms. Detox requires the app to build for testing.
- **Expo testing** — `jest-expo` preset with `@testing-library/react-native`
  for component tests; `expo prebuild` + Detox or Maestro for E2E.
- **Device farms** — run E2E suites across the device matrix (Firebase Test
  Lab, BrowserStack) before release; a flow that passes on one device is not a
  guarantee across versions and screen sizes.
- **Performance** — measure JS thread time, native render, and memory with
  the React Native DevTools/Perf Monitor or platform profilers on a device;
  Hermes is the default JS engine for the current releases.

## Store submission

React Native apps ship through the same stores as native apps:

- **Android** — upload the signed AAB (`android/app/build/outputs/bundle/
  release/app-release.aab`, or the EAS-produced artifact) to Play Console with
  internal/closed/open testing, data-safety declaration, and staged rollout.
  See [android.md](android.md).
- **iOS** — archive via Xcode or EAS, upload the `.ipa` to App Store Connect
  (TestFlight first), complete privacy labels and listing, submit for review.
  See [ios.md](ios.md).
- **Version parity** — keep `version` in `app.json`/`package.json` aligned
  with the platform build numbers so a release is identifiable across stores
  and in crash reports.

## Key references

- React Native documentation (reactnative.dev) — New Architecture, Hermes, and
  release notes.
- Expo documentation (docs.expo.dev) — SDK versions, EAS Build credentials,
  and upgrade guides.
- Per-platform references in this skill — [ios.md](ios.md) and
  [android.md](android.md) for signing, lifecycle, and store mechanics.
