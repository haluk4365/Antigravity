/**
 * HLK Referans Form — Shared Render Utilities
 * Tüm render.js dosyaları bu modülü kullanır.
 *
 * Kullanım:
 *   const { renderForm, loadComponents } = require('../shared/render-common');
 *   renderForm('template.html', data, 'cikti.png');
 *
 * Versiyon: V1.0
 */

const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');

/**
 * HTML template içindeki {{DATA_JSON}} placeholder'ını JSON verisi ile değiştirir.
 * Component dosyaları da aynı şekilde işlenir.
 */
function injectData(html, data) {
  return html.replace('{{DATA_JSON}}', JSON.stringify(data));
}

/**
 * Component dosyalarını yükler ve {{COMPONENT:adi}} placeholder'larını değiştirir.
 * Component'ler form klasöründeki components/ alt dizininden okunur.
 */
function loadComponents(templateHtml, componentsDir) {
  let html = templateHtml;

  // {{COMPONENT:adi}} pattern'ini ara ve değiştir
  const compRegex = /\{\{COMPONENT:(\w+)\}\}/g;
  let match;
  while ((match = compRegex.exec(templateHtml)) !== null) {
    const compName = match[1];
    const compPath = path.join(componentsDir, `${compName}.html`);
    if (fs.existsSync(compPath)) {
      const compContent = fs.readFileSync(compPath, 'utf-8');
      html = html.replace(match[0], compContent);
    } else {
      console.warn(`[WARN] Component bulunamadı: ${compPath}`);
      html = html.replace(match[0], `<!-- COMPONENT EKSIK: ${compName} -->`);
    }
  }

  return html;
}

/**
 * Ana render fonksiyonu.
 * @param {string} templatePath - template.html dosya yolu
 * @param {object} data - sample-data.json içeriği
 * @param {string} outputPath - çıktı PNG dosya yolu
 * @param {object} opts - opsiyonlar
 * @param {string} opts.componentsDir - components/ klasör yolu (component mimarisi için)
 * @param {number} opts.viewportWidth - viewport genişliği (varsayılan: 1100)
 * @param {number} opts.viewportHeight - viewport yüksekliği (varsayılan: 800)
 * @param {boolean} opts.fullPage - tam sayfa screenshot (varsayılan: false)
 * @param {string} opts.selector - screenshot alınacak element selector (varsayılan: '#sheet')
 */
async function renderForm(templatePath, data, outputPath, opts = {}) {
  const {
    componentsDir = null,
    viewportWidth = 1100,
    viewportHeight = 800,
    fullPage = false,
    selector = '#sheet',
  } = opts;

  let html = fs.readFileSync(templatePath, 'utf-8');

  // Component'leri yükle
  if (componentsDir && fs.existsSync(componentsDir)) {
    html = loadComponents(html, componentsDir);
  }

  // Veriyi enjekte et
  html = injectData(html, data);

  // MASTER-010: CSS dosyalarını inline et — page.setContent() relative path çözmez
  html = html.replace(/<link[^>]*href="([^"]*\.css)"[^>]*\/?>/g, (match, href) => {
    const cssPath = path.resolve(path.dirname(templatePath), href);
    if (fs.existsSync(cssPath)) {
      const css = fs.readFileSync(cssPath, 'utf-8');
      console.log(`[CSS INLINE] ${href} → ${css.length} bytes`);
      return `<style>${css}</style>`;
    }
    console.warn(`[CSS EKSIK] ${cssPath}`);
    return match;
  });

  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  });

  const page = await browser.newPage();
  await page.setViewport({
    width: viewportWidth,
    height: viewportHeight,
    deviceScaleFactor: 2,
  });
  await page.setContent(html, { waitUntil: 'networkidle0' });

  if (fullPage) {
    await page.screenshot({ path: outputPath, fullPage: true });
  } else {
    const el = await page.$(selector);
    if (el) {
      await el.screenshot({ path: outputPath });
    } else {
      await page.screenshot({ path: outputPath });
    }
  }

  await browser.close();
  console.log('Oluşturuldu:', outputPath);
}

/**
 * CLi kullanımı:
 *   node render.js [data.json] [cikti.png]
 */
function cliMain(renderFn, defaultDataPath, defaultOutputPath) {
  if (require.main === module) {
    const dataPath = process.argv[2] || defaultDataPath || 'sample-data.json';
    const outPath = process.argv[3] || defaultOutputPath || 'cikti.png';
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
    renderFn(data, outPath);
  }
}

module.exports = { renderForm, loadComponents, injectData, cliMain };
