# CV Generator – Setup & Usage

## Prerequisites

- Python 3.8 or higher
- pip

---

## First-time setup

### 1. Create and activate a virtual environment (recommended)

```bash
# Create
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on macOS / Linux
source venv/bin/activate
```

### 2. Upgrade pip

```bash
python.exe -m pip install --upgrade pip
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Chromium (one-time, ~300 MB)

```bash
python -m playwright install chromium
```

> **Important:** Always use `python -m playwright` instead of just `playwright`.
> This ensures the version installed inside your virtual environment is used,
> not a system-level installation (which may not exist).

### 5. Verify the installation

```bash
python -m playwright --version
```

You should see something like:

```
Version 1.49.0
```

---

## File structure

```
cv/
├── requirements.txt           ← Python dependencies
├── SETUP.md                   ← this file
├── generate_cv.py             ← generator script
├── cv_data.json               ← your CV content
├── cv.css                     ← styling
├── morten_johnsen_cv.html     ← generated (for browser preview)
└── morten_johnsen_cv.pdf      ← generated (final output)
```

---

## Daily usage

### Generate HTML + PDF (default)

```bash
python generate_cv.py
```

### Generate HTML only (fast preview, no PDF)

```bash
python generate_cv.py --html-only
```

Open the generated `.html` file in your browser to preview before
committing to a PDF render.

### Custom file paths

```bash
python generate_cv.py \
    --json  cv_data.json \
    --css   cv.css \
    --output morten_johnsen_cv.pdf
```

### Tailored version for a specific job application

```bash
# 1. Copy the data file
copy cv_data.json cv_data_ai_role.json        # Windows
# cp cv_data.json cv_data_ai_role.json        # macOS / Linux

# 2. Edit cv_data_ai_role.json
#    - Adjust summary bullets to match the role
#    - Reorder skill groups to prioritise what is relevant
#    - Tweak bullet points in recent experience entries

# 3. Generate the tailored CV
python generate_cv.py \
    --json   cv_data_ai_role.json \
    --output cv_ai_role.pdf
```

The CSS and generator script stay untouched between versions.

---

## Updating dependencies

### Update Playwright to latest

```bash
pip install --upgrade playwright
python -m playwright install chromium
```

> Always run `python -m playwright install chromium` after upgrading
> Playwright, as the required Chromium version may have changed.

### Freeze current working versions

After a successful install or upgrade, lock your exact versions:

```bash
pip freeze > requirements.txt
```

This ensures anyone else (or your future self) can reproduce the
exact same environment.

---

## Troubleshooting

### `greenlet` build fails during `pip install`

**Symptom:**
```
error: Microsoft Visual C++ 14.0 or greater is required.
```

**Cause:** The pinned `greenlet` version has no pre-built wheel for
your Python version and needs a C++ compiler to build from source.

**Fix:** Make sure `requirements.txt` specifies Playwright 1.49.0 or
higher, which ships with a compatible pre-built `greenlet` wheel:

```text
playwright==1.49.0
```

Then re-run:
```bash
pip install -r requirements.txt
```

---

### `playwright` command not recognised

**Symptom:**
```
'playwright' is not recognized as an internal or external command
```

**Cause:** The bare `playwright` command looks in the system PATH,
not inside your virtual environment.

**Fix:** Always use:
```bash
python -m playwright install chromium
```

---

### PDF background colors are missing

The script passes `print_background=True` to Playwright automatically.
If colors are still missing, make sure you are opening the HTML via
the script (which loads it as a `file://` URI) and not passing raw
HTML strings directly.

---

### HTML preview looks unstyled in browser

**Cause:** The generated HTML links to `cv.css` by relative filename.
If you move the HTML file to a different folder without the CSS file,
it will appear unstyled.

**Fix:** Always keep `cv.css` in the same folder as the generated
`.html` file, or open the HTML from the project folder directly.

---

### Pages are cut off in the PDF

Adjust the margin settings in `generate_cv.py` inside the
`html_to_pdf` function:

```python
page.pdf(
    path=str(pdf_path),
    format="A4",
    print_background=True,
    margin={
        "top":    "10mm",
        "bottom": "10mm",
        "left":   "0mm",
        "right":  "0mm"
    }
)
```

Increase `top` and `bottom` values if content is being clipped.

---

## Quick reference card

```
# Activate environment (do this first, every session)
venv\Scripts\activate

# Generate HTML + PDF
python generate_cv.py

# Generate HTML only (browser preview)
python generate_cv.py --html-only

# Tailored version
python generate_cv.py --json cv_data_ai_role.json --output cv_ai_role.pdf

# Update Playwright
pip install --upgrade playwright
python -m playwright install chromium
pip freeze > requirements.txt
```
