"""Công cụ hỗ trợ dịch các shard.

  python -X utf8 tool.py next  <shard> [n]   in n chuỗi chưa dịch (mặc định 80) dạng JSON
  python -X utf8 tool.py check <shard>       kiểm tra toàn bộ bản dịch của shard
  python -X utf8 tool.py status              tiến độ mọi shard

Bản dịch ghi vào out/<shard>-pNNN.json dạng {"<id>": "<bản dịch>"}.
"""
import json, glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CJK = re.compile(r'[一-鿿]')


def src(shard):
    return json.load(open(os.path.join(HERE, 'src', shard + '.json'), encoding='utf-8'))


def out(shard):
    res = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'out', shard + '-*.json'))):
        try:
            res.update(json.load(open(f, encoding='utf-8')))
        except Exception as e:
            print(f'!! {os.path.basename(f)} không đọc được JSON: {e}')
    return res


def skeleton(s):
    """Phần 'mã' phải giữ nguyên: ${...} (bỏ chuỗi lồng trong), thẻ HTML, thuộc tính class/id/data-."""
    sk = []
    i = 0
    while True:
        j = s.find('${', i)
        if j < 0:
            break
        depth, k = 0, j + 1
        while k < len(s):
            if s[k] == '{': depth += 1
            elif s[k] == '}':
                depth -= 1
                if depth == 0: break
            k += 1
        expr = re.sub(r'"[^"]*"|\'[^\']*\'', '""', s[j:k + 1])
        sk.append(re.sub(r'\s+', '', expr))
        i = k + 1
    sk += re.findall(r'</?[a-zA-Z][\w-]*', s)
    sk += re.findall(r'\b(?:class|id|data-[\w-]+|style)="[^"]*"', s)
    sk.append('NL%d' % s.count('\n'))
    return sorted(sk)


def problems(zh, vi):
    p = []
    if not isinstance(vi, str) or not vi.strip():
        return ['bản dịch rỗng']
    if CJK.search(vi):
        p.append('còn chữ Hán: ' + ''.join(CJK.findall(vi))[:20])
    if skeleton(zh) != skeleton(vi):
        a, b = skeleton(zh), skeleton(vi)
        p.append('lệch phần mã (${...}/thẻ HTML/xuống dòng): thiếu %s thừa %s' % (
            [x for x in a if x not in b][:4], [x for x in b if x not in a][:4]))
    if vi.count('\\') != zh.count('\\'):
        p.append('số dấu \\ khác bản gốc')
    for q in '"\'`':
        if vi.count(q) != zh.count(q):
            p.append(f'số ký tự {q} khác bản gốc (dùng “ ” ‘ ’ thay vì nháy ASCII)')
    return p


def main():
    cmd = sys.argv[1]
    if cmd == 'status':
        for f in sorted(glob.glob(os.path.join(HERE, 'src', '*.json'))):
            sh = os.path.basename(f)[:-5]
            s, o = src(sh), out(sh)
            print(f'{sh}: {len([k for k in s if k in o])}/{len(s)}')
        return
    shard = sys.argv[2]
    s, o = src(shard), out(shard)
    if cmd == 'next':
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 80
        todo = {k: v for k, v in s.items() if k not in o}
        batch = dict(list(todo.items())[:n])
        print(f'# còn {len(todo)} chuỗi; in {len(batch)}')
        print(json.dumps(batch, ensure_ascii=False, indent=0))
    elif cmd == 'check':
        bad = 0
        for k, zh in s.items():
            if k not in o:
                continue
            p = problems(zh, o[k])
            if p:
                bad += 1
                print(k, '|', '; '.join(p))
                print('   gốc :', zh[:200].replace('\n', '⏎'))
                print('   dịch:', str(o[k])[:200].replace('\n', '⏎'))
        extra = [k for k in o if k not in s]
        if extra:
            print('id không tồn tại:', extra[:10])
        print(f'== {shard}: đã dịch {len([k for k in s if k in o])}/{len(s)}, lỗi {bad}')


if __name__ == '__main__':
    main()
