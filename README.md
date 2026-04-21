# ScoutAgent

A Claude Code agent that reads a Scout's advancement record and builds a structured, week-by-week plan toward their next rank — from Scout all the way through Eagle.

The agent produces a Markdown plan file. A companion script converts it to a print-ready HTML report with a Gantt chart, monthly card grid, and weekly card grid.

---

## Example Reports

| Scout | Current Rank | Target Rank | Situation |
|-------|-------------|-------------|-----------|
| [Johnny Scout](Johnny_Scout_Eagle_Plan_20260420.md) | Life | Eagle | 4 merit badges remaining, Eagle project in progress, 6 months until 18th birthday — time-critical plan |
| [Jane Scout](Jane_Scout_FirstClass_Plan_20260420.md) | Tenderfoot | First Class | Halfway through Second Class, plan covers both intermediate ranks |

View the rendered HTML reports:
- [Johnny Scout — Eagle Plan](Johnny_Scout_Eagle_Plan_20260420.html)
- [Jane Scout — First Class Plan](Jane_Scout_FirstClass_Plan_20260420.html)

---

## How to Get a Scout's Advancement Record from Scoutbook

The agent works best with a Scoutbook Individual Advancement Record export.

**Steps:**
1. Log in to [scoutbook.scouting.org](https://scoutbook.scouting.org)
2. Click on the Scout's name
3. Click **Reports** in the left sidebar
4. Click **Individual Advancement Record**
5. Click **Download CSV**

The CSV lists every rank requirement and merit badge with its completion date. Paste the contents into the chat or provide the file path when running the agent.

**Don't have Scoutbook access?** You can also paste typed notes, a screenshot description, or a plain-text summary of what the Scout has completed. The agent will work with any format.

---

## How to Run the Agent

1. Open Claude Code in the `ScoutAgent` directory
2. The agent will ask for:
   - Scout's name
   - Current rank
   - Target rank
   - Advancement data (Scoutbook CSV, pasted text, or file path)
   - Date of birth (required if target rank is Eagle or Scout is 15+)
3. The agent reads the BSA requirements file, performs gap analysis, and produces two files:
   - **`[Name]_[Rank]_Plan_[Date].md`** — the full plan in Markdown for quick reference and editing
   - **`[Name]_[Rank]_Plan_[Date].html`** — a formatted report for the Scout and family to read and print

Open the `.html` file in any browser. To save as PDF: **File → Print → Save as PDF**.

---

## What the HTML Report Includes

| Section | Format |
|---------|--------|
| Scout header with key dates | Banner with metadata grid |
| Rank requirements status | Table with ✅ 🔄 ⬜ ⏱️ indicators |
| Time-sensitive requirements | Gantt chart across the plan timeline |
| Month-by-month plan | Two-column card grid with themes and checklists |
| Week-by-week detail (Weeks 1–8) | Two-column card grid |
| Merit badge detail (Eagle plans) | Requirement-by-requirement tables |
| This week's action items | Highlighted action box |

---

## BSA Requirements Reference

The agent uses `bsa-requirements-2025.txt` — a text version of the official *Scouts BSA Requirements* book effective January 1, 2025 (publication 3321625). All rank and merit badge requirements are sourced from this file.

> Verify current merit badge requirements at [scouting.org/advancement](https://www.scouting.org/advancement/) — some badges are updated annually.

---

## Ranks Supported

Scout → Tenderfoot → Second Class → First Class → Star → Life → Eagle

Multi-rank plans are supported. A Scout targeting First Class from Tenderfoot receives a plan covering both Second Class and First Class in sequence.
