"""Reproduce the notebook's title/year join with the Python standard library."""
from pathlib import Path
import csv, io, zipfile, math, statistics, json, hashlib
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
raw = ROOT / 'data/raw'
with zipfile.ZipFile(raw / 'kaggle_movies.zip') as z:
    content = z.read('movies.csv')
kaggle = list(csv.DictReader(io.StringIO(content.decode('utf-8-sig'))))
with (raw / 'imdb_2026-01-12.txt').open(encoding='utf-8-sig') as f:
    imdb = list(csv.DictReader(f, delimiter='\t'))
index = defaultdict(list)
for r in kaggle:
    index[(r['name'], int(r['year']))].append(r)
merged = [dict(k, **i) for i in imdb for k in index[(i['Title'], int(i['Year']))]]
seen, clean = set(), []
for r in merged:
    key = (r['Title'], r['Year'])
    if key in seen:
        continue
    seen.add(key)
    try:
        for col in ('budget', 'gross', 'votes', 'score'):
            r[col] = float(r[col])
    except ValueError:
        continue
    if not all(math.isfinite(r[c]) for c in ('budget', 'gross', 'votes', 'score')):
        continue
    if r['budget'] > 0 and r['gross'] > 0:
        clean.append(r)

def quantile(xs, p):
    xs = sorted(xs)
    pos = (len(xs)-1)*p
    lo = int(pos)
    return xs[lo] + (xs[min(lo+1,len(xs)-1)]-xs[lo])*(pos-lo)

subset = [r for r in clean if int(r['Year']) != 2020]
votes = [r['votes'] for r in subset if r['votes'] > 0]
cut = quantile(votes, .99)
low = [r for r in subset if r['budget'] < 15_000_000]
result = {
    'source_counts': {'kaggle':len(kaggle),'imdb':len(imdb)},
    'merged':len(merged), 'cleaned':len(clean), 'excluding_2020':len(subset),
    'years':[min(int(r['Year']) for r in clean),max(int(r['Year']) for r in clean)],
    'era': {},
    'vote_threshold_85pct_after_top1pct_removed':quantile([v for v in votes if v <= cut],.85),
    'low_budget_gross_budget_ratio':{'n':len(low),'mean':statistics.mean(r['gross']/r['budget'] for r in low),'median':statistics.median(r['gross']/r['budget'] for r in low)},
    'largest_ratios':[{'title':r['Title'],'year':r['Year'],'budget':r['budget'],'gross':r['gross'],'ratio':r['gross']/r['budget']} for r in sorted(low,key=lambda r:r['gross']/r['budget'],reverse=True)[:5]],
    'avengers':[{'title':r['Title'],'year':r['Year'],'id':r['IMDb code']} for r in clean if r['Title']=='The Avengers'],
    'sha256': {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in raw.iterdir() if p.is_file()},
}
for label, rows in [('through_2006',[r for r in clean if int(r['Year'])<=2006]),('from_2007',[r for r in clean if int(r['Year'])>=2007])]:
    result['era'][label] = {'n':len(rows), 'votes_gross_corr':statistics.correlation([r['votes'] for r in rows],[r['gross'] for r in rows]),'score_gross_corr':statistics.correlation([r['score'] for r in rows],[r['gross'] for r in rows])}
out=ROOT/'data/results'
out.mkdir(exist_ok=True)
(out/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
