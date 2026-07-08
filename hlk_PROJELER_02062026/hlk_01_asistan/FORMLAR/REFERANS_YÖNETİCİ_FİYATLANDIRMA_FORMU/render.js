/**
 * Yönetici Fiyatlandırma Formu — Puppeteer render (Component Mimarisi)
 * Kullanım: node render.js sample-data.json cikti.png
 */
const path = require('path');
const { renderForm } = require('../shared/render-common');

async function renderPricing(data, outputPath) {
  await renderForm(path.join(__dirname, 'template.html'), data, outputPath, {
    componentsDir: path.join(__dirname, 'components'),
    viewportWidth: 1100,
    viewportHeight: 800,
  });
}

module.exports = { renderPricing };

if (require.main === module) {
  const data = JSON.parse(require('fs').readFileSync(process.argv[2] || 'sample-data.json', 'utf-8'));
  renderPricing(data, process.argv[3] || 'cikti.png');
}
