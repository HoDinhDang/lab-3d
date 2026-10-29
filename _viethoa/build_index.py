"""Nhúng catalog.json vào index.html (để trang mục lục chạy được cả khi mở trực tiếp file://)."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cat = json.load(open(os.path.join(ROOT, 'catalog.json'), encoding='utf-8'))
data = json.dumps(cat, ensure_ascii=False).replace('</', '<\\/')
p = os.path.join(ROOT, 'index.html')
html = open(p, encoding='utf-8').read()
html = re.sub(r'(<script id="catalog" type="application/json">)[\s\S]*?(</script>)',
              lambda m: m.group(1) + data + m.group(2), html, count=1)
open(p, 'w', encoding='utf-8', newline='').write(html)
print(f'đã nhúng {len(cat)} bài vào index.html')
