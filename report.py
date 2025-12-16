from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict
import json
import re
import csv

# ================= CONFIG =================

SHIFT_TIMES = {
    "day":   ("8:00 AM",  "2:40 PM"),
    "swing": ("3:00 PM", "11:20 PM"),
}

USERNAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
TIMESTAMP_RE = re.compile(
    r"\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M"
)

# ================= HELPERS =================

def parse_ts(ts):
    return datetime.strptime(ts, "%m/%d/%Y %I:%M:%S %p")

def get_shift(ts):
    t = parse_ts(ts).time()
    for shift, (start, end) in SHIFT_TIMES.items():
        if datetime.strptime(start, "%I:%M %p").time() <= t <= datetime.strptime(end, "%I:%M %p").time():
            return shift
    return None

def is_task_list(text):
    return bool(re.match(r"(MQI-\d+)|(DA-\d+.*MQI-\d+)", text))

def is_timestamp(text):
    return bool(TIMESTAMP_RE.fullmatch(text))

# ================= EXTRACTION =================

def extract(html):
    soup = BeautifulSoup(html, "html.parser")
    report = soup.find("div", id=lambda x: x and "oReportDiv" in x)
    if not report:
        raise RuntimeError("❌ oReportDiv not found")

    rows = []
    state = {
        "task_list": None,
        "employee": None,
    }

    for tr in report.find_all("tr"):
        tds = tr.find_all("td", recursive=False)
        if not tds:
            continue

        texts = [td.get_text(strip=True) for td in tds]

        txn_date = next((t for t in texts if is_timestamp(t)), None)
        if not txn_date:
            continue  # Not a data row

        # ---- Resolve task list + employee (rowspan safe) ----
        seen_pass = False
        for t in texts:
            if t in ("PASS", "FAIL"):
                seen_pass = True
                continue

            if is_task_list(t):
                state["task_list"] = t
                continue

            if (
                not seen_pass
                and USERNAME_RE.fullmatch(t)
            ):
                state["employee"] = t

        # ---- Task item + status are adjacent ----
        task_item = None
        status = None
        for i in range(len(texts) - 1):
            if texts[i + 1] in ("PASS", "FAIL"):
                task_item = texts[i]
                status = texts[i + 1]
                break

        if status != "PASS":
            continue

        if not state["task_list"]:
            print(f"⚠️ Missing task list at {txn_date}")
            continue

        if not state["employee"]:
            print(f"⚠️ Missing employee for {state['task_list']} at {txn_date}")
            continue

        rows.append({
            "task_list": state["task_list"],
            "employee": state["employee"],
            "task_item": task_item,
            "txn_date": txn_date,
        })

    return rows

# ================= ORGANIZATION =================

def organize(rows):
    data = defaultdict(lambda: {
        "day": {
            "employee": "",
            "employees": set(),
            "tasks": set(),
        },
        "swing": {
            "employee": "",
            "employees": set(),
            "tasks": set(),
        }
    })

    for r in rows:
        shift = get_shift(r["txn_date"])
        if not shift:
            continue

        entry = data[r["task_list"]][shift]

        # Lock first employee, but track multiples
        if not entry["employee"]:
            entry["employee"] = r["employee"]
        entry["employees"].add(r["employee"])

        entry["tasks"].add(r["task_item"])

    result = []
    for task_list, shifts in sorted(data.items()):
        out = {task_list: {}}
        for s in ("day", "swing"):
            out[task_list][s] = {
                "employee": shifts[s]["employee"],
                "task_completed": tuple(sorted(shifts[s]["tasks"])),
                "total_passed": len(shifts[s]["tasks"]),
            }

            if len(shifts[s]["employees"]) > 1:
                print(
                    f"⚠️ Multiple employees for {task_list} ({s}): "
                    f"{', '.join(sorted(shifts[s]['employees']))}"
                )

        result.append(out)

    return result

# ================= EXPORT =================

def export_csv(rows, filename="extracted_tasks.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["task_list", "employee", "task_item", "txn_date"]
        )
        writer.writeheader()
        writer.writerows(rows)

# ================= MAIN =================

if __name__ == "__main__":
    with open("report_page.html", encoding="utf-8") as f:
        html = f.read()

    rows = extract(html)
    print(f"Extracted rows: {len(rows)}")

    export_csv(rows)

    result = organize(rows)

    print(json.dumps(result, indent=2))

    with open("extracted_data.json", "w") as f:
        json.dump(result, f, indent=2)
