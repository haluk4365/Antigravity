/**
 * HLK Live Activity Center (LAC) — Puppeteer render (Component Mimarisi)
 * Kullanım: node render.js sample-data.json cikti.png
 */
const path = require('path');
const { renderForm } = require('../shared/render-common');

async function renderLAC(data, outputPath) {
  await renderForm(path.join(__dirname, 'template.html'), data, outputPath, {
    componentsDir: path.join(__dirname, 'components'),
    viewportWidth: 1440,
    viewportHeight: 900,
    fullPage: true,
  });
}

module.exports = { renderLAC };

if (require.main === module) {
  const data = JSON.parse(require('fs').readFileSync(process.argv[2] || 'sample-data.json', 'utf-8'));
  renderLAC(data, process.argv[3] || 'cikti.png');
}
