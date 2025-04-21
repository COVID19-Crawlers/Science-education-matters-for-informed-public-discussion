# COVID19-Crawlers

Crawlers dedicated to gathering information about jargon changes in Israeli media from the COVID‑19 outbreak until today.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
  - [Running Spiders](#running-spiders)
  - [Resuming Crawls](#resuming-crawls)
- [Data Output](#data-output)
- [Phrase Extraction](#phrase-extraction)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Multi-site crawling**: Extract articles and comments from Kikar and Ynet.
- **Persistent queues**: Store and resume crawl jobs via Scrapy's JOBDIR.
- **Phrase analysis**: Organize extracted phrases from comments for downstream NLP analysis.

## Prerequisites
- Python 3.8+
- [Scrapy](https://scrapy.org/) 2.x

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/COVID19-Crawlers.git
   ```
2. Install dependencies:
   ```bash
   cd COVID19-Crawlers/crawlers
   pip install -r requirements.txt
   ```

## Project Structure
```
.
├── .vscode/                  # VSCode workspace settings
├── crawlers/                 # Scrapy project
│   ├── crawlers/             # Project module
│   │   ├── spiders/          # Spider definitions
│   │   └── settings.py       # Scrapy settings
│   └── crawls/               # JOBDIR folders per spider run
│       ├── kikar_spider_urls_2024_0/
│       │   └── requests.queue
│       ├── ...
│       └── ynet_spider_words_test_0/
│           └── requests.queue
└── phrases_in_comments/      # Extracted phrase data outputs
    ├── kikar/
    └── ynet/
```

## Usage

### Running Spiders
Navigate to the `crawlers` directory and run:
```bash
scrapy crawl kikar_spider -o output/kikar_data.json
scrapy crawl ynet_spider -o output/ynet_data.json
```

### Resuming Crawls (Advanced)
Scrapy’s built-in JOBDIR feature allows pausing and resuming crawls, **but you must enable it at the start of your crawl**. You cannot resume a crawl that was not initially started with the `-s JOBDIR=...` flag.

1. **Start a crawl with JOBDIR**:
   ```bash
   scrapy crawl kikar_spider \
     -s JOBDIR=crawls/kikar_spider_urls_2024_0 \
     -o output/kikar_data.json
   ```
2. **Pause** the crawl at any time (e.g., `CTRL+C`).
3. **Resume** the paused crawl:
   ```bash
   scrapy crawl kikar_spider \
     -s JOBDIR=crawls/kikar_spider_urls_2024_0
   ```

By storing the request queue and state in `crawls/kikar_spider_urls_2024_0`, you can stop and restart without losing progress.
## Data Output
- Raw scraped items will be stored as JSON files in the `output/` directory (create it if missing).
- Adjust the `-o` flag for different formats (CSV, XML).

## Phrase Extraction
After crawling, extracted phrases from comments are aggregated and stored in:
```
phrases_in_comments/
├── kikar/       # Phrase counts for Kikar comments
└── ynet/        # Phrase counts for Ynet comments
```

## Configuration
- Edit `crawlers/crawlers/settings.py` to tweak settings like download delays, concurrent requests, pipelines, and middlewares.
