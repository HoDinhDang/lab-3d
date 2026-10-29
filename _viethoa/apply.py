"""Ghép bản dịch vào bài giảng.

  python -X utf8 apply.py            đọc goc_tieng_trung/, ghi đè ../courses/*.html và ../catalog.json
  python -X utf8 apply.py --identity  kiểm tra vòng lặp: dùng chính bản gốc làm "bản dịch"
"""
import glob, json, os, re, sys
from tool import HERE, src, out, problems

ROOT = os.path.dirname(HERE)
ORIG = os.path.join(HERE, 'goc_tieng_trung')
ESC = re.compile(r'\\u([0-9A-Fa-f]{4})|\\x([0-9A-Fa-f]{2})')
LIT = re.compile(r'"(?:[^"\\\n]|\\.)*"|\'(?:[^\'\\\n]|\\.)*\'|`(?:[^`\\]|\\.)*`')
CJK = re.compile(r'[一-鿿]')
COMMENT = re.compile(r'/\*[\s\S]*?\*/|//[^\n]*|(?<=content:")[^"]*(?=")')


def decode(body):
    def rep(m):
        cp = int(m.group(1) or m.group(2), 16)
        return chr(cp) if cp >= 0x80 else m.group(0)
    return ESC.sub(rep, body)


identity = '--identity' in sys.argv
tr, rejected = {}, 0
for f in glob.glob(os.path.join(HERE, 'src', '*.json')):
    sh = os.path.basename(f)[:-5]
    s, o = src(sh), out(sh)
    for k, zh in s.items():
        if identity:
            tr[zh] = zh
        elif k in o:
            if problems(zh, o[k]):
                rejected += 1  # bản dịch lỗi định dạng → giữ nguyên gốc cho an toàn
            else:
                # giữ khoảng trắng đầu/cuối như bản gốc để các mảnh câu ghép lại không dính chữ
                lead = zh[:len(zh) - len(zh.lstrip(' '))]
                trail = zh[len(zh.rstrip(' ')):]
                tr[zh] = lead + o[k].strip(' ') + trail
codelits = set(json.load(open(os.path.join(HERE, 'codelits.json'), encoding='utf-8')))

missing = set()
for f in sorted(glob.glob(os.path.join(ORIG, 'courses', '*.html'))):
    s = open(f, encoding='utf-8').read()
    start = s.find('<script')
    parts, last = [s[:start]], start
    for m in LIT.finditer(s, start):
        raw = m.group(0)
        body = decode(raw[1:-1])
        if not CJK.search(body):
            continue
        if body in codelits:
            new = COMMENT.sub(lambda c: tr.get(c.group(0), c.group(0)), body)
        elif body in tr:
            new = tr[body]
        else:
            missing.add(body)
            continue
        if identity:
            new = raw[1:-1]  # identity: giữ nguyên chuỗi thô để so byte
        parts += [s[last:m.start()], raw[0] + new + raw[0]]
        last = m.end()
    parts.append(s[last:])
    res = ''.join(parts)
    if not identity:
        head = res[:start]
        head = head.replace('<html lang="zh-CN">', '<html lang="vi">')
        head = re.sub(r'<title>(.*?)</title>', lambda t: '<title>%s</title>' % tr.get(t.group(1), t.group(1)), head)
        res = head + res[start:]
        open(os.path.join(ROOT, 'courses', os.path.basename(f)), 'w', encoding='utf-8', newline='').write(res)
    elif res != s:
        print('!! vòng lặp không khớp:', os.path.basename(f))

if not identity:
    cat = json.load(open(os.path.join(ORIG, 'catalog.json'), encoding='utf-8'))
    t = lambda v: tr.get(v, v)
    for c in cat:
        for key in ('title', 'type', 'question'):
            c[key] = t(c[key])
        c['textbook'] = [t(v) for v in c['textbook']]
        c['steps'] = [t(v) for v in c['steps']]
    json.dump(cat, open(os.path.join(ROOT, 'catalog.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'đã áp dụng {len(tr)} bản dịch; bị loại vì lỗi định dạng {rejected}; chuỗi chưa có bản dịch {len(missing)}')
