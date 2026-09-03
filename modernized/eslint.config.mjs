import nx from '@nx/eslint-plugin';

export default [
  ...nx.configs['flat/base'],
  ...nx.configs['flat/typescript'],
  {
    files: ['**/*.ts'],
    rules: {
      '@nx/enforce-module-boundaries': ['error', {
        enforceBuildableLibDependency: true,
        depConstraints: [
          { sourceTag: 'type:feature', onlyDependOnLibsWithTags: ['type:ui', 'type:state'] },
          { sourceTag: 'type:state', onlyDependOnLibsWithTags: ['type:data-access', 'type:platform'] },
          { sourceTag: 'type:data-access', onlyDependOnLibsWithTags: ['type:platform'] },
          { sourceTag: 'type:ui', onlyDependOnLibsWithTags: ['type:ui'] },
        ],
      }],
    },
  },
];
