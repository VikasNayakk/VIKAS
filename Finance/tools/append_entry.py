import sys
from datetime import date
try:
    from openpyxl import load_workbook
except ImportError:
    print('MISSING_OPENPYXL')
    raise

if len(sys.argv) < 5:
    print('Usage: python append_entry.py <xlsx-path> <name> <item> <amount>')
    sys.exit(1)

path, name, item, amount = sys.argv[1:5]
try:
    wb = load_workbook(path)
    ws = wb.active
    ws.append([date.today().isoformat(), name, item, amount])
    wb.save(path)
    print('Appended row:', [date.today().isoformat(), name, item, amount])
except Exception as e:
    print('ERROR:', e)
    sys.exit(2)
