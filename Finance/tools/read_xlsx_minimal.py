import sys
import zipfile
import xml.etree.ElementTree as ET

NS = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def get_shared_strings(z):
    try:
        data = z.read('xl/sharedStrings.xml')
    except KeyError:
        return []
    root = ET.fromstring(data)
    strings = []
    for si in root.findall('.//main:si', NS):
        text_parts = []
        for t in si.findall('.//main:t', NS):
            text_parts.append(t.text or '')
        strings.append(''.join(text_parts))
    return strings


def find_first_sheet(z):
    names = [n for n in z.namelist() if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')]
    if not names:
        raise FileNotFoundError('No worksheets found in xlsx')
    names.sort()
    return names[0]


def parse_sheet(z, sheet_name, shared_strings, max_rows=20):
    data = z.read(sheet_name)
    root = ET.fromstring(data)
    rows = []
    for r in root.findall('.//main:row', NS):
        row_vals = []
        for c in r.findall('main:c', NS):
            cell_type = c.get('t')
            v = c.find('main:v', NS)
            if v is None:
                is_elem = c.find('main:is', NS)
                if is_elem is not None:
                    t = is_elem.find('.//main:t', NS)
                    row_vals.append(t.text if t is not None else '')
                else:
                    row_vals.append('')
            else:
                if cell_type == 's':
                    try:
                        idx = int(v.text)
                        row_vals.append(shared_strings[idx] if idx < len(shared_strings) else '')
                    except:
                        row_vals.append(v.text)
                else:
                    row_vals.append(v.text)
        rows.append(row_vals)
        if len(rows) >= max_rows:
            break
    return rows


def pretty_print(rows):
    if not rows:
        print('(no rows found)')
        return
    widths = []
    for row in rows:
        for i, val in enumerate(row):
            s = '' if val is None else str(val)
            if len(widths) <= i:
                widths.append(len(s))
            else:
                widths[i] = max(widths[i], len(s))
    for row in rows:
        parts = []
        for i, val in enumerate(row):
            s = '' if val is None else str(val)
            parts.append(s.ljust(widths[i]))
        print(' | '.join(parts))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python read_xlsx_minimal.py <path-to-xlsx> [max_rows]')
        sys.exit(1)
    path = sys.argv[1]
    max_rows = int(sys.argv[2]) if len(sys.argv) >= 3 else 20
    try:
        with zipfile.ZipFile(path, 'r') as z:
            shared = get_shared_strings(z)
            sheet = find_first_sheet(z)
            rows = parse_sheet(z, sheet, shared, max_rows=max_rows)
            pretty_print(rows)
    except Exception as e:
        print('Error reading xlsx:', e)
        sys.exit(2)
