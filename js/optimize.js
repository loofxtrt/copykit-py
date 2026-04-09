import { readFileSync, writeFileSync, mkdirSync } from 'fs';
import { basename, join } from 'path';
import { optimize } from 'svgo';

// pega o caminho passado no terminal
const inputPath = process.argv[2];

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

    // limpeza equivalente ao SVGOMG
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

// cria pasta optimized se não existir
mkdirSync('optimized', { recursive: true });

// nome do arquivo final
const outputPath = join('optimized', basename(inputPath));

// salva
writeFileSync(outputPath, result.data);

console.log('✔ SVG otimizado salvo em:', outputPath);