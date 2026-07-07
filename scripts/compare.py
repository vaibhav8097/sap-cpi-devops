import os
from pathlib import Path

history = Path("backup/history")

folders = sorted(
    [f for f in history.iterdir() if f.is_dir()]
)

if len(folders) < 2:
    print("Need at least two backups.")
    exit()

old = folders[-2]
new = folders[-1]

old_files = {f.name for f in old.glob("*.zip")}
new_files = {f.name for f in new.glob("*.zip")}

results = []

for f in sorted(old_files | new_files):

    if f not in old_files:
        status = "ADDED"

    elif f not in new_files:
        status = "REMOVED"

    else:
        old_size = (old / f).stat().st_size
        new_size = (new / f).stat().st_size

        if old_size == new_size:
            status = "NO CHANGE"
        else:
            status = "MODIFIED"

    results.append((f, status))

os.makedirs("reports", exist_ok=True)

html = """
<html>
<head>
<title>Compare Report</title>
<style>
body{font-family:Arial;}
table{border-collapse:collapse;width:100%;}
th,td{border:1px solid #ddd;padding:8px;}
th{background:#0070f2;color:white;}
</style>
</head>
<body>

<h2>SAP CPI Compare Report</h2>

<table>

<tr>

<th>Artifact</th>

<th>Status</th>

</tr>
"""

for f, s in results:

    html += f"<tr><td>{f}</td><td>{s}</td></tr>"

html += """

</table>

</body>

</html>
"""

with open(
    "reports/compare-report.html",
    "w",
    encoding="utf-8"
) as report:

    report.write(html)

print("Comparison Complete")