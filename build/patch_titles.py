#!/usr/bin/env python3
"""Rewrite search snippets (title + meta description + og/twitter) of pages that already sit on
page 1 of Google (avg position 6-13) but get no clicks — answer first, with the page's own worked
example numbers. Numbers come from each page's worked example; never invent figures.
Run at deploy before patch_hreflang.py:  python3 build/patch_titles.py _site"""
import html, pathlib, re, sys

SITE = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "_site")

T = {
    "en/home/tv-series-duration-calculator.html": (
        "Binge-Watch Calculator: Hours & Days to Finish Any TV Series",
        "16 episodes of 65 min (3 min intro skipped) = 16 h 32 min — 9 days at 2 h a day. Enter episodes, runtime, speed (1.25×–2×) and hours per day for your finish date."),
    "en/science/cell-doubling-time-calculator.html": (
        "Cell Doubling Time Calculator: Td = t·ln2 ÷ ln(N/N₀)",
        "Enter start and end cell counts and the time between them: 1×10⁵ → 8×10⁵ cells in 72 h = 24 h doubling time (3 doublings). Growth rate per hour included."),
    "en/money/balance-transfer-calculator.html": (
        "Balance Transfer Calculator: 0% Intro APR Savings vs Staying Put",
        "Moving $6,000 at 22.9% APR to a 0% card for 18 months (3% fee, $300 a month) saves $1,419 in interest. Compare month by month with your own numbers."),
    "en/home/reading-challenge-calculator.html": (
        "Reading Challenge Calculator: Pages per Day to Hit Your Book Goal",
        "6 books of 300 pages left with 52 days to go = 35 pages a day (about 52 min at 40 pages an hour). Enter your yearly goal to see your daily pace and if you are on track."),
}


def esc(x):
    return html.escape(x, quote=True)


def patch(p, title, desc):
    s = p.read_text(encoding="utf-8")
    o = s
    full = title if "Hong Life" in title else title
    s = re.sub(r"<title>.*?</title>", lambda m: f"<title>{esc(full)}</title>", s, count=1, flags=re.S)
    for pat, val in ((r'(<meta name="description" content=")[^"]*', desc),
                     (r'(<meta property="og:title" content=")[^"]*', title),
                     (r'(<meta property="og:description" content=")[^"]*', desc),
                     (r'(<meta name="twitter:title" content=")[^"]*', title),
                     (r'(<meta name="twitter:description" content=")[^"]*', desc)):
        s = re.sub(pat, lambda m: m.group(1) + esc(val), s, count=1)
    if s != o:
        p.write_text(s, encoding="utf-8")
        return True
    return False


n = 0
for rel, (t, d) in T.items():
    p = SITE / rel
    if p.exists() and patch(p, t, d):
        n += 1
print("titles patched:", n, "/", len(T))
