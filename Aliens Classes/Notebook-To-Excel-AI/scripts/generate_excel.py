"""
Aliens Classes → Excel Entry Generator
Reads real meeting data from Aliens-Meeting folder and creates structured Excel.
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side, numbers

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT = os.path.join(BASE, "output", "final_master_v2.xlsx")
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# ─── Meeting Data (extracted from Aliens-Meeting folder) ───
meetings = [
    {
        "Meeting Name": "Aliens Meeting",
        "Agenda": "Team attendance review and discipline check",
        "Type": "Common",
        "Duration": "",
        "Date": "02-03-2026",
        "Host": "A'dii Sunlay",
        "Present": 37,
        "Late": 19,
        "Absent": 46,
    },
    {
        "Meeting Name": "Aliens Meeting",
        "Agenda": "Team progress tracking and daily standup",
        "Type": "Common",
        "Duration": "",
        "Date": "03-03-2026",
        "Host": "A'dii Sunlay",
        "Present": 27,
        "Late": 3,
        "Absent": 63,
    },
    {
        "Meeting Name": "Project Manager",
        "Agenda": "Project management roles and responsibilities",
        "Type": "Development Team",
        "Duration": "",
        "Date": "04-03-2026",
        "Host": "A'dii Sunlay",
        "Present": 1,
        "Late": 2,
        "Absent": 4,
    },
    {
        "Meeting Name": "Aliens Meeting",
        "Agenda": "Small group session and quick review",
        "Type": "Common",
        "Duration": "",
        "Date": "06-03-2026",
        "Host": "A'dii Sunlay",
        "Present": 4,
        "Late": 3,
        "Absent": 35,
    },
    {
        "Meeting Name": "Aliens Meeting",
        "Agenda": "Weekly performance and attendance review",
        "Type": "Common",
        "Duration": "",
        "Date": "09-03-2026",
        "Host": "A'dii Sunlay",
        "Present": 21,
        "Late": 6,
        "Absent": 62,
    },
    {
        "Meeting Name": "Aliens Meeting",
        "Agenda": "Full team attendance and growth discussion",
        "Type": "Common",
        "Duration": "",
        "Date": "10-03-2026",
        "Host": "A'dii Sunlay",
        "Present": 25,
        "Late": 7,
        "Absent": 57,
    },
    {
        "Meeting Name": "Aliens Meeting",
        "Agenda": "Scheduled meeting session (template prepared)",
        "Type": "Common",
        "Duration": "",
        "Date": "11-03-2026",
        "Host": "A'dii Sunlay",
        "Present": "",
        "Late": "",
        "Absent": "",
    },
    {
        "Meeting Name": "Notebook Image Entry",
        "Agenda": "Handwritten notebook - OCR text extracted",
        "Type": "Common",
        "Duration": "",
        "Date": "",
        "Host": "A'dii Sunlay",
        "Present": "",
        "Late": "",
        "Absent": "",
    },
]

# ─── Column order ───
COLUMNS = ["Meeting Name", "Agenda", "Type", "Duration", "Date", "Host", "Present", "Late", "Absent"]

# ─── Create Workbook ───
wb = Workbook()
ws = wb.active
ws.title = "Aliens Classes"

# ─── Styles ───
header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
data_font = Font(name="Calibri", size=11)
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left = Alignment(horizontal="left", vertical="center", wrap_text=True)
thin_border = Border(
    left=Side(style='thin', color="B0B0B0"),
    right=Side(style='thin', color="B0B0B0"),
    top=Side(style='thin', color="B0B0B0"),
    bottom=Side(style='thin', color="B0B0B0"),
)
alt_fill = PatternFill(start_color="F2F7FB", end_color="F2F7FB", fill_type="solid")

# ─── Column widths ───
col_widths = {
    "A": 22,  # Meeting Name
    "B": 45,  # Agenda
    "C": 20,  # Type
    "D": 12,  # Duration
    "E": 14,  # Date
    "F": 16,  # Host
    "G": 10,  # Present
    "H": 8,   # Late
    "I": 10,  # Absent
}

for col_letter, width in col_widths.items():
    ws.column_dimensions[col_letter].width = width

# ─── Write Headers ───
for i, col_name in enumerate(COLUMNS, 1):
    cell = ws.cell(row=1, column=i, value=col_name)
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = center
    cell.border = thin_border

ws.row_dimensions[1].height = 30

# ─── Write Data Rows ───
for row_idx, meeting in enumerate(meetings, 2):
    for col_idx, col_name in enumerate(COLUMNS, 1):
        value = meeting[col_name]
        cell = ws.cell(row=row_idx, column=col_idx, value=value)
        cell.font = data_font
        cell.border = thin_border

        # Alignment
        if col_name in ("Meeting Name", "Agenda"):
            cell.alignment = left
        else:
            cell.alignment = center

    # Alternate row color
    if row_idx % 2 == 0:
        for col_idx in range(1, len(COLUMNS) + 1):
            ws.cell(row=row_idx, column=col_idx).fill = alt_fill

    ws.row_dimensions[row_idx].height = 22

# ─── Freeze header row ───
ws.freeze_panes = "A2"

# ─── Auto-filter ───
ws.auto_filter.ref = f"A1:I{len(meetings) + 1}"

# ─── Save ───
wb.save(OUTPUT)
print(f"✅ Excel saved: {OUTPUT}")
print(f"   Total entries: {len(meetings)}")
print(f"   Columns: {', '.join(COLUMNS)}")
print()

# ─── Preview table ───
print("=" * 120)
header_line = " | ".join(f"{c:<20}" if c in ("Meeting Name", "Agenda") else f"{c:<14}" for c in COLUMNS)
print(header_line)
print("-" * 120)
for m in meetings:
    row_line = " | ".join(
        f"{str(m[c]):<20}" if c in ("Meeting Name", "Agenda") else f"{str(m[c]):<14}"
        for c in COLUMNS
    )
    print(row_line)
print("=" * 120)
