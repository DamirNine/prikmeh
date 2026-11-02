# v16 = правленая пользователем v15 (30.10) без рисунка 13 и связанного с ним текста.
import os
from docx import Document
from docx.oxml.ns import qn

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'Расчет_силовой_и_кинематический_тангенсный_механизм_v15_правки_30.10.docx')
DST = os.path.join(HERE, 'Расчет_силовой_и_кинематический_тангенсный_механизм_v16.docx')

doc = Document(SRC)
paras = doc.paragraphs


def text(p):
    return ''.join(t.text or '' for t in p._p.iter(qn('w:t')))


def drop(p):
    p._p.getparent().remove(p._p)


# 1. Абзац «26295» на месте удалённого рисунка и подпись рисунка 13
junk = [p for p in paras if text(p).strip() == '26295']
cap = [p for p in paras if text(p).startswith('Рисунок 13 ')]
assert len(junk) == 1 and len(cap) == 1, (len(junk), len(cap))
assert not list(junk[0]._p.iter(qn('w:drawing')))
drop(junk[0])
drop(cap[0])

# 2. Ссылка на рисунок 13 в п. 12.5
OLD, NEW = ' — в таблице 16 и на рисунке 13.', ' — в таблице 16.'
hits = [p for p in doc.paragraphs if OLD in text(p)]
assert len(hits) == 1
p = hits[0]
runs = list(p._p.iter(qn('w:t')))
full = ''.join(t.text or '' for t in runs)
start = full.index(OLD)
end = start + len(OLD)
# переписываем затронутые w:t, сохраняя форматирование первого из них
pos = 0
first = True
for t in runs:
    s, e = pos, pos + len(t.text or '')
    pos = e
    if e <= start or s >= end:
        continue
    keep_l = (t.text or '')[:max(0, start - s)]
    keep_r = (t.text or '')[max(0, end - s):] if e > end else ''
    t.text = keep_l + (NEW if first else '') + keep_r
    t.set(qn('xml:space'), 'preserve')
    first = False

assert not any('рисунк' in text(q) and '13' in text(q) and 'Рисунок 1' not in text(q)
               for q in doc.paragraphs if 'рисунке 13' in text(q))
doc.save(DST)
print('saved', DST)
