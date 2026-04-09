import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { basename, join } from 'path';
import { optimize } from 'svgo';

// args obrigatórios
const inputPath = process.argv[2];
const outputDir = process.argv[3];

// sem validação extra — vai quebrar se faltar

// lê o SVG
const svg = readFileSync(inputPath, 'utf-8');

// otimiza
const result = optimize(svg, {
  path: inputPath,
  js2svg: {
    pretty: true,
    indent: 2
  },
  plugins: [
    {
      name: 'preset-default',
      params: {
        overrides: {
          removeViewBox: false
        }
      }
    },
    {
      name: 'cleanupIds',
      params: {
        minify: true
      }
    },
    'removeEditorsNSData',
    'removeUselessDefs',
    'removeEmptyContainers',
    'removeUnknownsAndDefaults',
    'removeComments',
    'removeMetadata',
    'removeTitle',
    'removeDesc'
  ]
});

// cria pasta de saída
mkdirSync(outputDir, { recursive: true });

// monta caminho final
const outputPath = join(outputDir, basename(inputPath));

// salva
writeFileSync(outputPath, result.data);

console.log('✔ SVG otimizado salvo em:', outputPath);