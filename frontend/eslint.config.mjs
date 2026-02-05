import nextConfig from 'eslint-config-next';
import prettierConfig from 'eslint-config-prettier';
import testingLibraryPlugin from 'eslint-plugin-testing-library';
import jestDomPlugin from 'eslint-plugin-jest-dom';
import tseslint from 'typescript-eslint';

const config = [
  {
    ignores: ['node_modules/**', 'build/**', 'public/**', '.next/**'],
  },
  ...nextConfig,
  prettierConfig,
  {
    rules: {
      'prefer-const': 0,
      'react/jsx-uses-vars': 1,
      'react/jsx-uses-react': 1,
      'strict': 0,
      'no-console': ['warn', { allow: ['error', 'info'] }],
      'no-unused-vars': 'off',
      'no-debugger': 'off',
      'no-extra-semi': 0,
      'react/no-unescaped-entities': ['error', { forbid: ['>', '}'] }],
    },
  },
  {
    files: ['**/*.ts', '**/*.tsx'],
    plugins: {
      '@typescript-eslint': tseslint.plugin,
    },
    rules: {
      '@typescript-eslint/no-extra-semi': 0,
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { args: 'all', argsIgnorePattern: '^_' },
      ],
    },
  },
  {
    files: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)'],
    plugins: {
      'testing-library': testingLibraryPlugin,
      'jest-dom': jestDomPlugin,
    },
    rules: {
      ...testingLibraryPlugin.configs.react.rules,
      ...jestDomPlugin.configs.recommended.rules,
      'react/display-name': 0,
      'testing-library/no-container': 'warn',
      'testing-library/no-node-access': 'warn',
    },
  },
];

export default config;
