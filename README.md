# Linkreader

Linkreader is a tool that takes a list of news article URLs (from a PDF or a text file) and downloads the **clean text** of each article — no ads, no navigation menus, no "follow us on social media" clutter. Just the article itself.

It was built to help researchers who need to build a text corpus from online news sources, particularly for use with tools like [Sketch Engine](https://www.sketchengine.eu/).

---

## What does it do?

1. You give it a **PDF** (or a plain text file) that contains news article URLs
2. It reads all the URLs from that file
3. It visits each URL and extracts **only the article text** (headline, body paragraphs — nothing else)
4. It saves each article as a clean `.txt` file on your computer
5. It organizes the files into folders by **news site**, **year**, and **section** (e.g. politics, lifestyle, etc.)

For example, if your PDF contains URLs from `takvim.com.tr` spanning 2015 to 2025, you'll get a folder structure like this:

```
output/
  takvim.com.tr/
    2015/
      siyaset/
        2015-09-06_neden-kadinlar-karar-veren-olmasin.txt
    2020/
      guncel/
        2020-08-03_istanbul-sozlesmesi-nedir-...txt
      yasam/
        2020-05-26_icisleri-bakanligi-koronavirus-...txt
    2021/
      guncel/
        2021-03-19_istanbul-sozlesmesi-iptal-edildi.txt
        2021-03-20_son-dakika-istanbul-sozlesmesi-...txt
      ...
```

Each `.txt` file looks like this:

```
Baslik: (article title, if available)
Tarih: 2021-03-19
Yazar: (author name, if available)
Kaynak: takvim.com.tr
URL: https://www.takvim.com.tr/guncel/2021/03/19/istanbul-sozlesmesi-iptal-edildi
Bolum: guncel
============================================================

Resmi Gazete'de yayimlanan Cumhurbaskani Karari ile Turkiye, Istanbul
Sozlesmesi'nden ayrildi...
(rest of the article text)
```

---

## Before you start (one-time setup)

You need two things installed on your computer:

### 1. Python (version 3.12 or newer)

Check if you already have it by opening your terminal and typing:

```
python3 --version
```

If it says `Python 3.12.x` or higher, you're good. If not, download it from [python.org](https://www.python.org/downloads/).

### 2. uv (the Python package manager)

Install it by opening your terminal and running:

**On Mac or Linux:**
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installing, close and reopen your terminal.

### 3. Download and set up Linkreader

Open your terminal and run these commands one by one:

```
cd linkreader
uv sync
```

The `uv sync` command will download all the necessary components. This only needs to be done once (or again if something changes in the project).

---

## How to use it

All commands below should be run from inside the `linkreader` folder in your terminal.

### Step 1: Check your PDF (recommended first step)

Before downloading anything, you can check that your PDF was read correctly:

```
uv run linkreader your-file.pdf --dry-run
```

This will show you how many URLs were found and how they are grouped by year, **without actually downloading anything**. Use this to verify everything looks right.

Example output:

```
  takvim-url-2013-2025.pdf: 232 URLs parsed

  Total URLs: 232

                    URLs by Year
  ┏━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
  ┃ Year ┃ Count ┃ Sections              ┃
  ┡━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
  │ 2015 │     1 │ siyaset               │
  │ 2018 │     8 │ galeri, guncel, ...   │
  │ 2020 │    32 │ ekonomi, guncel, ...  │
  │ 2021 │    76 │ galeri, guncel, ...   │
  │ ...  │   ... │ ...                   │
  └──────┴───────┴───────────────────────┘
```

### Step 2: Download the articles

```
uv run linkreader your-file.pdf
```

That's it! The tool will:
- Visit each URL (with a 2-second pause between requests to be polite to the website)
- Extract the clean article text
- Save everything into the `output/` folder

You'll see a progress bar while it works:

```
Fetching articles from takvim.com.tr (232 URLs)
takvim.com.tr ━━━━━━━━━━━━━━━━━━━ 148/232  0:03:24
```

For 232 URLs, expect it to take about **8 minutes**.

### Step 3: Check the results

When it finishes, you'll see a summary table:

```
              Summary
  ┏━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━━┓
  ┃ Year  ┃ Total ┃ Success ┃ Failed ┃
  ┡━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━━┩
  │ 2020  │    32 │      30 │      2 │
  │ 2021  │    76 │      74 │      2 │
  │ ...   │   ... │     ... │    ... │
  ├───────┼───────┼─────────┼────────┤
  │ TOTAL │   232 │     220 │     12 │
  └───────┴───────┴─────────┴────────┘
```

- **Success** means the article was downloaded and saved
- **Failed** means the URL couldn't be reached (maybe the page was deleted, or the website blocked the request)

If there are failures, a `failed_urls.txt` file is created in the output folder listing all the URLs that didn't work and why.

---

## More options

### Process multiple files at once

```
uv run linkreader file1.pdf file2.pdf file3.pdf
```

Or all PDFs in the folder:

```
uv run linkreader *.pdf
```

### Use a plain text file instead of a PDF

If you have URLs in a simple text file (one URL per line), that works too:

```
uv run linkreader urls.txt
```

You can add comments with `#` and year hints:

```
# 2020
https://www.example.com/article1
https://www.example.com/article2

# 2021
https://www.example.com/article3
```

### Mix PDFs and text files

```
uv run linkreader takvim.pdf cumhuriyet-urls.txt hurriyet.pdf
```

### Save to a different folder

By default, articles are saved to `./output/`. To change this:

```
uv run linkreader your-file.pdf -o my-corpus
```

### Resume after interruption

If the download gets interrupted (you close your laptop, lose internet, etc.), you can pick up where you left off:

```
uv run linkreader your-file.pdf --resume
```

This will skip articles that were already downloaded and only fetch the remaining ones.

### Adjust the download speed

By default, the tool waits 2 seconds between each request. If you want to be more cautious (some websites may block fast requests):

```
uv run linkreader your-file.pdf --delay 3
```

Or if you want to go a bit faster (not recommended for large batches):

```
uv run linkreader your-file.pdf --delay 1
```

---

## Preparing your input files

### PDF format

The tool reads URLs that are embedded as **clickable links** in the PDF. This is the most reliable method.

It also understands year headers in the format `2021 – 76 haber` (or `2021 – haber yok` for years with no articles). These headers help group the articles by year.

### Text file format

A simple `.txt` file with one URL per line. Blank lines are ignored. Lines starting with `#` are treated as comments and can include year hints:

```
# 2021 - 76 haber
https://www.takvim.com.tr/guncel/2021/03/19/istanbul-sozlesmesi-iptal-edildi
https://www.takvim.com.tr/guncel/2021/03/20/...
```

---

## Troubleshooting

### "Command not found: uv"

You need to install `uv` first. See the setup instructions above. After installing, close and reopen your terminal.

### "No URLs found in input files"

The PDF might not have clickable links embedded in it. Try opening the PDF and clicking on a URL — if it doesn't open in your browser, the links aren't embedded. You may need to copy the URLs into a text file manually.

### Some articles show "no content extracted"

This can happen when:
- The article is behind a paywall
- The page has been deleted
- The page uses heavy JavaScript (video-only pages, interactive content)

These will be listed in `failed_urls.txt` so you can check them manually.

### The download is very slow

Each request has a 2-second pause to avoid being blocked by the website. For 232 URLs, this means about 8 minutes. This is intentional — going faster risks getting your IP blocked by the news site.

### I got disconnected / my laptop went to sleep

No problem! Run the same command again with `--resume`:

```
uv run linkreader your-file.pdf --resume
```

It will skip everything that was already downloaded.

---

## Quick reference

| Command | What it does |
|---|---|
| `uv run linkreader file.pdf --dry-run` | Check PDF contents without downloading |
| `uv run linkreader file.pdf` | Download all articles |
| `uv run linkreader file.pdf --resume` | Resume a previously interrupted download |
| `uv run linkreader file.pdf -o folder` | Save to a custom folder |
| `uv run linkreader file.pdf --delay 3` | Wait 3 seconds between requests |
| `uv run linkreader *.pdf` | Process all PDFs in the folder |
