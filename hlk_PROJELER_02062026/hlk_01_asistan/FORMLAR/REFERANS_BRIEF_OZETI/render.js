/**
 * Brief Özeti — Puppeteer render (Basit Form)
 * Kullanım: node render.js sample-data.json cikti.png
 */
const path = require('path');
const { renderForm } = require('../shared/render-common');

async function renderBriefOzet(data, outputPath) {
  await renderForm(path.join(__dirname, 'template.html'), data, outputPath, {
    viewportWidth: 1100, viewportHeight: 800,
  });
}

module.exports = { renderBriefOzet };
if (require.main === module) {
  const data = JSON.parse(require('fs').readFileSync(process.argv[2] || 'sample-data.json', 'utf-8'));
  renderBriefOzet(data, process.argv[3] || 'cikti.png');
}
