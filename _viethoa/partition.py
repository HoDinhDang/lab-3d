# Extract every Chinese-bearing JS string literal from the lessons and split them into shards.
import re, glob, json, sys, os
root, work = sys.argv[1], sys.argv[2]
NSHARDS = int(sys.argv[3]) if len(sys.argv) > 3 else 8
ESC = re.compile(r'\\u([0-9A-Fa-f]{4})|\\x([0-9A-Fa-f]{2})')
LIT = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|`(?:[^`\\]|\\.)*`')
CJK = re.compile(r'[一-鿿]')

def decode(body):
    # only decode non-ASCII escapes so " / \ etc. stay escaped
    def rep(m):
        cp = int(m.group(1) or m.group(2), 16)
        return chr(cp) if cp >= 0x80 else m.group(0)
    return ESC.sub(rep, body)

cat = {c['slug']: c for c in json.load(open(os.path.join(root, 'catalog.json'), encoding='utf-8'))}
order = {'phys': 0, 'chem': 1, 'bio': 2, 'geo': 3}
uses = {}  # decoded body -> list of slugs
for f in sorted(glob.glob(os.path.join(root, 'courses', '*.html'))):
    slug = os.path.basename(f)[:-5]
    s = open(f, encoding='utf-8').read()
    for m in LIT.finditer(s, s.find('<script')):
        body = decode(m.group(0)[1:-1])
        if CJK.search(body):
            uses.setdefault(body, [])
            if slug not in uses[body]: uses[body].append(slug)

# Embedded CSS / GLSL sources: only their comments carry Chinese, so translate comments as units
COMMENT = re.compile(r'/\*[\s\S]*?\*/|//[^\n]*|(?<=content:")[^"]*(?=")')
def is_code(b):
    return len(b) > 400 and bool(re.search(r'void main|uniform |precision |^\s*/\*|:root|\{\s*[\w-]+\s*:', b))
codelits = [b for b in uses if is_code(b)]
for b in codelits:
    sl = uses.pop(b)
    left = COMMENT.sub('', b)
    if CJK.search(left): print('!! code literal still has Chinese outside comments:', CJK.findall(left)[:10])
    for c in COMMENT.findall(b):
        if CJK.search(c):
            uses.setdefault(c, [])
            uses[c] += [s for s in sl if s not in uses[c]]
json.dump(codelits, open(os.path.join(work, 'codelits.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print('code literals', len(codelits))

common = [b for b, sl in uses.items() if len(sl) >= 3]
by_lesson = {}
for b, sl in uses.items():
    if len(sl) < 3: by_lesson.setdefault(sl[0], []).append(b)
size = lambda bs: sum(len(CJK.findall(b)) for b in bs)
lessons = sorted(by_lesson, key=lambda s: (order.get(cat[s]['subject'], 9), s))
total = sum(size(by_lesson[s]) for s in lessons)
target = total / NSHARDS
shards, cur, acc = [], [], 0
for s in lessons:
    cur.append(s); acc += size(by_lesson[s])
    if acc >= target and len(shards) < NSHARDS - 1:
        shards.append(cur); cur, acc = [], 0
if cur: shards.append(cur)

os.makedirs(os.path.join(work, 'src'), exist_ok=True)
os.makedirs(os.path.join(work, 'out'), exist_ok=True)
manifest = {}
def dump(name, bodies, lessons_):
    items = {f'{name}-{i:05d}': b for i, b in enumerate(bodies)}
    json.dump(items, open(os.path.join(work, 'src', name + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    manifest[name] = {'lessons': lessons_, 'strings': len(items), 'zh_chars': size(bodies),
                      'titles': {l: cat[l]['title'] for l in lessons_ if l in cat}}
dump('common', common, [])
# catalog.json fields and <title> texts that do not already appear as JS strings
extra = []
for c in cat.values():
    for v in [c['title'], c['type'], c['question']] + c['textbook'] + c['steps']:
        if CJK.search(v) and v not in uses and v not in extra: extra.append(v)
for f in sorted(glob.glob(os.path.join(root, 'courses', '*.html'))):
    t = re.search(r'<title>(.*?)</title>', open(f, encoding='utf-8').read()).group(1)
    if CJK.search(t) and t not in uses and t not in extra: extra.append(t)
dump('catalog', extra, [])
for i, sh in enumerate(shards):
    dump(f's{i+1}', [b for s in sh for b in by_lesson[s]], sh)
json.dump(manifest, open(os.path.join(work, 'manifest.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in manifest.items(): print(k, v['strings'], v['zh_chars'], ' '.join(v['lessons']))
