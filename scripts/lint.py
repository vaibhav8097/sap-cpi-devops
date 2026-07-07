import os
import zipfile
from xml.etree import ElementTree as ET

BACKUP_FOLDER = "backup/latest"
REPORT_FOLDER = "reports"

os.makedirs(REPORT_FOLDER, exist_ok=True)

results = []

for file in os.listdir(BACKUP_FOLDER):

    if not file.endswith(".zip"):
        continue

    path = os.path.join(BACKUP_FOLDER, file)

    status = "PASS"
    message = []

    try:

        with zipfile.ZipFile(path, "r") as z:

            names = z.namelist()

            if not any("META-INF" in n for n in names):
                status = "FAIL"
                message.append("META-INF folder missing")

            if not any("integrationflow" in n.lower() for n in names):
                status = "FAIL"
                message.append("Integration Flow artifact missing")

            for name in names:

                if name.endswith(".xml"):

                    try:
                        ET.fromstring(z.read(name))
                    except Exception:
                        status = "FAIL"
                        message.append(f"Invalid XML : {name}")

    except Exception as ex:

        status = "FAIL"
        message.append(str(ex))

    results.append((file, status, ", ".join(message)))

html = """
<html>
<head>
<title>CPI Lint Report</title>
<style>
table{
border-collapse:collapse;
width:100%;
}
th,td{
border:1px solid #ddd;
padding:8px;
}
th{
background:#0d6efd;
color:white;
}
.pass{
color:green;
font-weight:bold;
}
.fail{
color:red;
font-weight:bold;
}
</style>
</head>
<body>

<h2>SAP CPI Lint Report</h2>

<table>

<tr>
<th>Artifact</th>
<th>Status</th>
<th>Remarks</th>
</tr>
"""

for file, status, remarks in results:

    css = "pass" if status == "PASS" else "fail"

    html += f"""
<tr>
<td>{file}</td>
<td class="{css}">{status}</td>
<td>{remarks}</td>
</tr>
"""

html += """
</table>
</body>
</html>
"""

with open("reports/lint-report.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Lint Completed")
print(f"Artifacts Checked : {len(results)}")