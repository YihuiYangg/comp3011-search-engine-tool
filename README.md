# COMP3011 Coursework 2: Search Engine Tool

A Python command-line search tool for crawling `https://quotes.toscrape.com/`, building an inverted index, saving/loading the index, and searching for pages containing query terms.

This project is structured to match the COMP3011 Coursework 2 brief.

## Features

- Polite same-site crawler with a default 6-second delay between HTTP requests
- HTML parsing with Beautiful Soup
- Case-insensitive tokenisation
- JSON inverted index storing:
  - word frequency per page
  - token positions per page
- Interactive shell commands:
  - `build`
  - `load`
  - `print <word>`
  - `find <query terms>`
- Unit tests for crawler, indexer, search logic, and index persistence

## Repository Structure

```text
repository-name/
├── src/
│   ├── __init__.py
│   ├── crawler.py
│   ├── indexer.py
│   ├── search.py
│   └── main.py
├── tests/
│   ├── test_crawler.py
│   ├── test_indexer.py
│   └── test_search.py
├── data/
│   └── .gitkeep
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows PowerShell
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Search Tool

Start the interactive shell from the repository root:

```bash
python -m src.main
```

You should then see a prompt:

```text
>
```

### Command 1: build

Crawls the target website, builds the inverted index, and saves it to `data/index.json`.

```text
> build
```

The default crawler delay is 6 seconds, so this command is intentionally slow. This is required to respect the coursework politeness window.

### Command 2: load

Loads the saved index from the file system:

```text
> load
```

Run `build` before `load` unless `data/index.json` already exists.

### Command 3: print

Prints the inverted-index posting list for one word:

```text
> print nonsense
```

The output shows each URL containing the word, plus the word frequency and token positions in that page.

### Command 4: find

Finds pages containing all query terms:

```text
> find indifference
> find good friends
```

Multi-word queries use AND semantics. For example, `find good friends` returns pages that contain both `good` and `friends`. Results are ranked by the total frequency of the query words on each page.

### Edge Cases

The shell handles common edge cases:

```text
> find
Usage: find <word or words>

> print
Usage: print <word>

> find wordnotintheindex
No pages found for 'wordnotintheindex'.
```

## Optional Runtime Arguments

The defaults are suitable for coursework submission. For development only, you can reduce the delay:

```bash
python -m src.main --delay 0
```

Do not use a delay below 6 seconds in the assessed `build` demonstration unless your module staff explicitly allow it.

Other options:

```bash
python -m src.main --base-url https://quotes.toscrape.com/ --index-path data/index.json --max-pages 120
```

## Testing

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

The tests use small fake HTML examples and mocked crawling, so they do not make live network requests or wait 6 seconds.

## Design Notes

### Crawler

`src/crawler.py` implements a breadth-first same-site crawler. It normalises URLs, removes fragments, skips external links, and waits between requests. The default delay is 6 seconds to satisfy the politeness requirement.

### Indexer

`src/indexer.py` converts HTML into visible text, tokenises words case-insensitively, and records each word's frequency and positions per page.

The inverted index structure is:

```json
{
  "word": {
    "https://example/page/": {
      "frequency": 2,
      "positions": [3, 19]
    }
  }
}
```

This structure makes `print <word>` efficient because the posting list for a word can be retrieved directly by dictionary lookup.

### Search

`src/search.py` implements:

- `build()` to crawl and index pages
- `save()` and `load()` for JSON persistence
- `print_word()` for single-word posting lists
- `find()` for single-word and multi-word queries

Multi-word search intersects posting-list URL sets, which is appropriate for AND-style search.

## Version Control Workflow

Suggested commit sequence:

```bash
git add README.md requirements.txt .gitignore
git commit -m "Set up project structure"

git add src/indexer.py tests/test_indexer.py
git commit -m "Implement inverted index construction"

git add src/crawler.py tests/test_crawler.py
git commit -m "Implement polite same-site crawler"

git add src/search.py tests/test_search.py
git commit -m "Implement search and index persistence"

git add src/main.py README.md
git commit -m "Add command-line search shell"
```

## GenAI Declaration and Critical Evaluation Notes

Replace this section with your own accurate reflection before submission.

Example points to discuss in the video:

- Which GenAI tool was used and for what purpose.
- Which generated suggestions were useful, such as project structuring, test ideas, or explaining Beautiful Soup usage.
- Which suggestions required correction, such as ensuring the 6-second politeness window was actually enforced or making tests avoid real network requests.
- How you verified the code yourself by reading it, running tests, and checking edge cases.
- How using GenAI affected your learning and development process.

Do not claim understanding of code you cannot explain. You should be able to justify every file, function, and data structure in the final submission.

## Submission Reminder

Submit via Minerva:

1. A working video demonstration link.
2. Your public GitHub repository URL.
3. The compiled index file generated by running `build`, usually `data/index.json`.
