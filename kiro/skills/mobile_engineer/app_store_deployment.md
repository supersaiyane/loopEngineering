---
id: app_store_deployment
version: 1.0.0
owners:
  - mobile_engineer
tags:
  - deployment
  - app-store
  - google-play
  - ci-cd
  - mobile
when_to_use: "When releasing a mobile app to the App Store or Google Play, setting up mobile CI/CD, or managing app signing and versioning."
inputs:
  - app bundle identifier
  - signing certificates
  - target stores (iOS/Android/both)
outputs:
  - EAS build config
  - CI/CD pipeline
  - release checklist
  - versioning strategy
---

> "Shipping to the App Store is a negotiation. Come prepared."

## EAS Build + Submit (Expo)

```json
// eas.json
{
  "cli": { "version": ">= 7.0.0" },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "ios": { "simulator": false }
    },
    "production": {
      "autoIncrement": true,
      "env": { "APP_ENV": "production" }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "dev@company.com",
        "ascAppId": "1234567890",
        "appleTeamId": "ABCDE12345"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json",
        "track": "internal"
      }
    }
  }
}
```

## CI/CD with GitHub Actions

```yaml
# .github/workflows/mobile-release.yml
name: Mobile Release
on:
  push:
    tags: ['v*']
jobs:
  build-and-submit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
      - name: Build iOS
        run: eas build --platform ios --profile production --non-interactive
      - name: Build Android
        run: eas build --platform android --profile production --non-interactive
      - name: Submit to stores
        run: eas submit --platform all --profile production --non-interactive
        env:
          GOOGLE_SERVICE_ACCOUNT_KEY: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_KEY }}
```

## Versioning Strategy

```
version (user-visible):  1.2.3   — bump on every release
buildNumber (iOS):        42      — auto-increment per build
versionCode (Android):    42      — auto-increment per build

Major: breaking changes or major feature
Minor: new features, backward compatible
Patch: bug fixes only
```

## Pre-Release Checklist

- [ ] Version bumped (`version` in app.json)
- [ ] Release notes written (both EN + localizations)
- [ ] Privacy manifest updated (iOS 17+ required)
- [ ] Tested on oldest supported OS version
- [ ] App Store screenshots updated if UI changed
- [ ] Crash-free rate ≥ 99.5% in TestFlight before production submit

## Validation Checklist

- [ ] `eas.json` has separate profiles: development / preview / production
- [ ] Signing credentials stored in EAS (not checked into git)
- [ ] CI builds triggered on git tags (not every push)
- [ ] TestFlight / Internal Track tested before production rollout
- [ ] OTA update (EAS Update) configured for hotfixes that don't require store review
