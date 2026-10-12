# CivicShield Pro

**Rights in reach.**

CivicShield Pro is a multilingual mobile app that helps people understand their rights, communicate across language barriers, organize important information, and find professional support.

Created by **Deetya Chakilam** for the Congressional App Challenge.

**Repository:** [github.com/turtle8789/BayAreaCivicShield](https://github.com/turtle8789/BayAreaCivicShield)

![CivicShield Pro logo](artifacts/mobile/assets/images/icon.png)

> CivicShield Pro provides general educational and organizational information. It is not legal advice, an emergency service, or a replacement for a qualified lawyer. Laws vary by jurisdiction; verify information with an appropriate professional.

## Why CivicShield?

Language barriers can make everyday interactions and unfamiliar legal situations harder to navigate. CivicShield brings rights education, translation, document tools, and support resources together in an accessible interface.

## Features

- **Know Your Rights:** Browse educational guidance for traffic stops, police encounters, searches, arrests, immigration encounters, and other situations. An interactive quiz helps reinforce understanding.
- **Translation:** Access multilingual statements and translation tools for difficult interactions. Speech-related capabilities depend on device permissions, platform support, and network availability.
- **Document Analyzer:** Scan or upload documents, extract text, and identify important dates, deadlines, and organizational next steps. OpenAI-powered image analysis assists with text extraction; results should be checked against the original document.
- **Encounter Log:** Record the date, location, people involved, and notes about an encounter.
- **Privacy and backups:** App Lock, automatic locking, biometric options on supported devices, and encrypted backup tools help protect sensitive records.
- **Legal Aid Near Me:** Search by location for legal aid organizations, lawyers, and courthouses.
- **Resource Center:** Search curated legal resources, educational materials, immigration support, and crisis hotlines, with website and calling options.
- **Community Forum:** Browse discussions and create posts. In the current implementation, user-created posts and helpful votes are stored locally; this is not yet a shared, live community service.
- **Accessibility and localization:** Language selection, right-to-left layouts for supported languages, adjustable text size, and high-contrast options.

## Technology

The project began with a Python prototype. The current mobile application uses:

- **TypeScript / JavaScript**
- **React Native and Expo**
- **Expo Router** for navigation
- **AsyncStorage** for local app persistence
- **Node.js and Express** for the supporting API
- **OpenAI** for document image text extraction
- **pnpm workspaces** for package management

This repository also includes React-based demonstration videos.

## Repository structure

| Directory | Purpose |
| --- | --- |
| `artifacts/mobile/` | CivicShield Pro Expo mobile app |
| `artifacts/api-server/` | Supporting Express API, including document OCR |
| `artifacts/civicshield-demo/` | Landscape competition demonstration |
| `artifacts/civicshield-vertical/` | Vertical demonstration |
| `lib/` | Shared workspace packages |

## Running the project

### Prerequisites

- Node.js and pnpm
- Expo Go or a compatible development environment for mobile testing
- A configured supporting API for document image analysis

Install dependencies from the repository root:

```bash
pnpm install
```

### Mobile app outside the configured workspace

Start the Expo development server:

```bash
pnpm --filter @workspace/mobile exec expo start
```

Follow Expo's instructions to open the app on a supported device or emulator.

The current mobile configuration derives the API address from the development workspace. For a separate local installation, configure `extra.apiBaseUrl` in `artifacts/mobile/app.config.js` to point to an API reachable by your device. Without this configuration, document image OCR reports that its API is not configured.

### Supporting API

Start the API in a separate terminal:

```bash
PORT=5000 pnpm --filter @workspace/api-server run dev
```

The OCR route requires `AI_INTEGRATIONS_OPENAI_API_KEY` and `AI_INTEGRATIONS_OPENAI_BASE_URL` in the server environment. These must match your supported OpenAI connection. Never commit credentials to the repository.

### Configured workspace

The existing development workflows start the mobile app and API with the workspace's proxy configuration:

```bash
pnpm --filter @workspace/mobile run dev
pnpm --filter @workspace/api-server run dev
```

## Development checks

Run mobile checks:

```bash
pnpm --filter @workspace/mobile run typecheck
pnpm --filter @workspace/mobile run test
```

Run workspace checks:

```bash
pnpm run typecheck
pnpm run build
```

## Privacy and limitations

- Core user records and preferences are stored locally. Clearing app storage or uninstalling the app can remove local information; use and verify backups before doing so.
- Document image analysis sends the submitted image to the supporting API and its AI provider. Consider the sensitivity of a document before uploading it.
- Translations, extracted text, dates, and educational guidance can contain errors. They do not establish legal rights or replace professional interpretation.
- Search results and organization listings do not guarantee availability or service quality.
- The local Community Forum implementation does not synchronize posts between users.

## Development and AI assistance

The original Python prototype was created by Deetya. Replit Agent assisted with migration to TypeScript, implementation, debugging, and demonstration-video revisions. Deetya defined the project goals and feature priorities, supplied founder footage, and directed the final design and presentation.

OpenAI is also used in the app's document image analysis workflow.

## Future improvements

- Expand language coverage.
- Add moderated ratings and reviews for legal-service search results.
- Add native-language voice input for resource searches and encounter records.
- Seek additional review from legal professionals, language reviewers, and community users.
- Develop a shared community service with appropriate moderation and privacy safeguards.

## Feedback

Report bugs or suggest improvements through the [GitHub Issues page](https://github.com/turtle8789/BayAreaCivicShield/issues). Do not include private encounter records, sensitive documents, or credentials in public issues.
