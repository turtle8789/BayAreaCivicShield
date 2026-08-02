import type { Config } from 'jest';

const config: Config = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  // Resolve the "@/" path alias used throughout the mobile package
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  // Only run files in __tests__ or *.test.ts — not the Expo entry points
  testMatch: ['**/__tests__/**/*.test.ts', '**/*.test.ts'],
  // Ignore Expo/Metro-managed directories
  testPathIgnorePatterns: ['/node_modules/', '/.expo/'],
  // ts-jest transform config (keep the default compiler options from the
  // project tsconfig but loosen moduleResolution so Jest can find modules)
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: {
          // Use the project's strict settings but relax module resolution for Jest
          strict: true,
          esModuleInterop: true,
          moduleResolution: 'node',
          allowSyntheticDefaultImports: true,
          baseUrl: '.',
          paths: {
            '@/*': ['./*'],
          },
        },
      },
    ],
  },
};

export default config;
