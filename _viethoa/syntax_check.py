"""Tách <script type="module"> của từng bài và chạy `node --check` để bắt lỗi cú pháp sau khi ghép bản dịch."""
import glob, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmp = tempfile.mkdtemp()
bad = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'courses', '*.html'))):
    s = open(f, encoding='utf-8').read()
    m = re.search(r'<script type="module">([\s\S]*)</script>', s)
    p = os.path.join(tmp, os.path.basename(f) + '.mjs')
    open(p, 'w', encoding='utf-8').write(m.group(1))
    r = subprocess.run(['node', '--check', p], capture_output=True, text=True, encoding='utf-8')
    if r.returncode:
        bad += 1
        print(os.path.basename(f), r.stderr[:500])
print(f'lỗi cú pháp: {bad}')
sys.exit(1 if bad else 0)
