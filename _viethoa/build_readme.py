"""Sinh README.md tiếng Việt từ catalog.json, trỏ link tới bản triển khai trên Vercel.

  python -X utf8 build_readme.py
Tham chiếu SGK dạng ngắn lấy từ README.en.md (bản gốc tiếng Anh) rồi đổi sang tiếng Việt.
"""
import json, os, re

SITE = 'https://lab-3d-ashy.vercel.app'
REPO = 'https://github.com/HoDinhDang/lab-3d'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cat = json.load(open(os.path.join(ROOT, 'catalog.json'), encoding='utf-8'))
en = open(os.path.join(ROOT, 'README.en.md'), encoding='utf-8').read()

# slug -> "Elective Vol. 1, Ch. 2, Sec. 3" ; thứ tự bài theo README gốc
ref, order = {}, []
for m in re.finditer(r'^\| \[.*?\]\(https://lab\.tongjiang\.app/c/([\w-]+)/\) \| ([^|]+) \|', en, re.M):
    ref[m.group(1)] = m.group(2).strip()
    order.append(m.group(1))


def vi_ref(s):
    s = re.sub(r'Required Vol\. (\d)', r'Bắt buộc – Tập \1', s)
    s = re.sub(r'Elective Vol\. (\d)', r'Tự chọn bắt buộc \1', s)
    s = re.sub(r'Ch\. (\d+)', r'Chương \1', s)
    s = re.sub(r'Sec\. (\d+)', r'Bài \1', s)
    return s


SUBJECTS = [('phys', 'Vật lý'), ('chem', 'Hoá học'), ('bio', 'Sinh học'), ('geo', 'Địa lý')]
by_slug = {c['slug']: c for c in cat}
rank = {s: i for i, s in enumerate(order)}

out = [f"""# Phòng thí nghiệm 3D — bản Việt hoá Tongjiang Lab

**Bài giảng khoa học 3D tương tác, miễn phí cho THPT: Vật lý, Hoá học, Sinh học và Địa lý.**

👉 Dùng trực tuyến: **{SITE}**

Hiện có {len(cat)} bài. Mỗi bài là **một file HTML độc lập, khoảng 1 MB**: nhấp đúp để mở, chạy được khi không có mạng, trên máy chiếu hoặc bảng tương tác. Mỗi bài là một thế giới 3D có bảng điều khiển trực tiếp, câu hỏi dẫn dắt và lộ trình từng bước để giáo viên dạy từ đầu đến cuối.

Nội dung bám theo chương trình THPT và bộ SGK Nhân dân Giáo dục (PEP) 2019 của Trung Quốc. Toàn bộ giao diện và lời giảng đã được Việt hoá theo thuật ngữ SGK Việt Nam (chương trình GDPT 2018); tên chất hoá học dùng danh pháp IUPAC.

## Cách dùng

- **Trực tuyến**: mở trang mục lục {SITE}, chọn môn học rồi chọn bài, hoặc bấm **▶ Mở bài** trong các bảng dưới đây.
- **Không cần mạng**: tải repo về (**Code → Download ZIP**), giải nén, mở `index.html` hoặc một file trong `courses/` bằng Chrome hoặc Edge.
- **Nhúng vào trang khác**: `<iframe src="{SITE}/courses/<slug>" width="100%" style="aspect-ratio:16/9;border:0" allow="fullscreen"></iframe>`
- **Dữ liệu**: [`catalog.json`](catalog.json) liệt kê mọi bài kèm vị trí trong SGK và các bước.
- **Thao tác trong bài**: kéo chuột để xoay, cuộn để phóng to/thu nhỏ; **F** toàn màn hình, **Q** làm bài kiểm tra, **1–9** nhảy tới bước.

## Danh sách bài giảng
"""]

for key, name in SUBJECTS:
    items = sorted([c for c in cat if c['subject'] == key], key=lambda c: rank.get(c['slug'], 999))
    out.append(f'\n### {name} ({len(items)})\n')
    out.append('| Bài học | SGK PEP 2019 | Số bước | Mở | Mã nguồn |')
    out.append('|---|---|---|---|---|')
    for c in items:
        url = f"{SITE}/courses/{c['slug']}"
        title = c['title'].replace('|', '\\|')
        out.append(f"| [{title}]({url}) | {vi_ref(ref.get(c['slug'], ''))} | {len(c['steps'])} | "
                   f"[▶ Mở bài]({url}) | [HTML](courses/{c['slug']}.html) |")

out.append(f"""
## Cấu trúc thư mục

| Đường dẫn | Nội dung |
|---|---|
| `index.html` | Trang mục lục, phân chia theo môn học |
| `courses/` | 54 bài giảng, mỗi bài một file HTML |
| `covers/` | Ảnh bìa các bài |
| `catalog.json` | Danh mục bài giảng (tiếng Việt) |
| `_viethoa/` | Công cụ Việt hoá: script tách/ghép chuỗi, bảng thuật ngữ `glossary.md`, bản dịch trong `out/` |

## Giấy phép và ghi nguồn

- Đây là **bản Việt hoá có chỉnh sửa** của [Tongjiang Lab](https://lab.tongjiang.app) do Tongjiang (铜匠十点睡觉) xây dựng. Bản gốc tiếng Anh của README xem ở [README.en.md](README.en.md).
- Bài giảng, ảnh bìa và danh mục theo giấy phép **[CC BY-NC 4.0](LICENSE)**: được dùng, chia sẻ và chỉnh sửa cho mục đích **phi thương mại**, phải ghi nguồn “Tongjiang Lab (https://lab.tongjiang.app)”.
- Mã của bên thứ ba đóng gói trong bài (three.js, MIT) giữ giấy phép riêng, xem [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
- Không liên kết với Nhà xuất bản Giáo dục Nhân dân (PEP).

Phát hiện lỗi dịch hoặc lỗi hiển thị? Hãy mở issue tại [{REPO}/issues]({REPO}/issues).
""")

open(os.path.join(ROOT, 'README.md'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
missing = [c['slug'] for c in cat if c['slug'] not in ref]
print('đã ghi README.md;', 'thiếu tham chiếu SGK:', missing)
