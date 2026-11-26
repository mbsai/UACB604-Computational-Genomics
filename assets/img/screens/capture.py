"""Re-take the website screenshots used in the slides.

    pip install playwright pillow && playwright install chromium
    python3 assets/img/screens/capture.py            # all pages
    python3 assets/img/screens/capture.py ncbi_gene  # one page

Raw full-page captures go to ./raw (not committed). annotate.py then crops
them and draws the numbered callouts into the .jpg files used by the slides.
Cookie banners are hidden (removed from the page), never accepted.
NCBI Gene, Nucleotide and Datasets pages and the UCSC browser ask automated browsers
to prove they are human, so those screenshots are taken by hand (see README).
"""
import sys, pathlib, time
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "raw"
RAW.mkdir(exist_ok=True)

PAGES = {
    # Lecture 1.5
    "ensembl":     "https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=ENSG00000141510",
    "uniprot":     "https://www.uniprot.org/uniprotkb/P04637/entry",
    # Lecture 2.4
    "ena_j02482":  "https://www.ebi.ac.uk/ena/browser/view/J02482",
    # Lecture 2.5
    "bioproject":  "https://www.ncbi.nlm.nih.gov/bioproject/PRJNA229998",
    "runselector": "https://www.ncbi.nlm.nih.gov/Traces/study/?acc=PRJNA229998",
    "ena_project": "https://www.ebi.ac.uk/ena/browser/view/PRJNA229998",
}

HIDE_BANNERS = """
for (const sel of ['#data-protection-banner', '.data-protection-banner', '#cookie-banner',
                   '.cookie-banner', '#ncbi-alerts', '.ncbi-alerts', '#cookiePopup',
                   '[class*="cookie-consent"]', '[id*="cookie"]', '[class*="CookieConsent"]',
                   '.usa-banner', '#ebi_banner', '.ebi-banner', '#ebiDataProtectionBanner',
                   '[class*="gdpr"]', '[class*="Banner_banner"]'])
  document.querySelectorAll(sel).forEach(e => e.remove());
// any fixed/sticky bar that talks about cookies
for (const e of document.querySelectorAll('body *')) {
  const cs = getComputedStyle(e);
  if ((cs.position === 'fixed' || cs.position === 'sticky') && /cookie/i.test(e.textContent || '')) e.remove();
}
// Ensembl's "Messages" side panel: press its close button
document.querySelectorAll('[class*="close" i], button[aria-label*="close" i]').forEach(b => {
  if (b.click && b.closest('[class*="message" i], [class*="sidebar" i], [class*="drawer" i]')) b.click();
});
"""

def grab(page, name, url):
    print(f"{name}: {url}")
    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    try:
        page.wait_for_load_state("networkidle", timeout=45_000)
    except Exception:
        pass
    time.sleep(6)                       # single-page apps (ENA, UniProt) render late
    page.evaluate(HIDE_BANNERS)
    if name == "ensembl":               # close the "Messages" side panel (its x button)
        page.mouse.click(1401, 139); time.sleep(2)
    time.sleep(1)
    page.screenshot(path=str(RAW / f"{name}.png"), full_page=True)

if __name__ == "__main__":
    want = sys.argv[1:] or list(PAGES)
    with sync_playwright() as p:
        exe = sorted(pathlib.Path.home().glob("Library/Caches/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell"))
        b = p.chromium.launch(executable_path=str(exe[-1])) if exe else p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2, locale="en-GB")
        page = ctx.new_page()
        for n in want:
            try:
                grab(page, n, PAGES[n])
            except Exception as e:
                print("  failed:", e)
        b.close()
