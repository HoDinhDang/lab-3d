"""Liệt kê nhãn ngắn (gốc ≤ N chữ Hán, không có mã) mà bản dịch quá dài so với chỗ trống trên giao diện.

  python -X utf8 long_labels.py [N=6] [ratio=4.5]  -> ghi long_labels.json {id: {zh, vi}}
"""
import glob, json, os, re, sys
from tool import HERE, src, out

N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
RATIO = float(sys.argv[2]) if len(sys.argv) > 2 else 4.5
CJK = re.compile(r'[一-鿿]')
res = {}
for f in sorted(glob.glob(os.path.join(HERE, 'src', '*.json'))):
    sh = os.path.basename(f)[:-5]
    s, o = src(sh), out(sh)
    for k, zh in s.items():
        n = len(CJK.findall(zh))
        if not n or n > N or re.search(r'[<${}\n]', zh) or k not in o:
            continue
        vi = o[k].strip()
        # chiều rộng ước lượng: 1 chữ Hán ≈ 2 ký tự Latin
        if len(vi) > max(12, len(zh.strip()) * RATIO / 2 + 4):
            res[k] = {'zh': zh, 'vi': o[k]}
json.dump(res, open(os.path.join(HERE, 'long_labels.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print(len(res))
for k, v in list(res.items())[:25]:
    print(k, v['zh'], '->', v['vi'])
