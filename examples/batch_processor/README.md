# Batch Processor Example

Efficiently process multiple prompts concurrently with error recovery, progress tracking, and results export.

## Features

- Concurrent processing with thread pool
- Progress tracking with tqdm
- Automatic retry on failures
- Rate limiting support
- Results export (JSON, CSV)
- Detailed logging
- Error recovery

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Process JSON input
python processor.py input.json output.json

# Process CSV input with 4 workers
python processor.py input.csv output.csv --workers 4

# With rate limiting (2 requests per second)
python processor.py input.json output.json --rate-limit 0.5

# With retries
python processor.py input.json output.json --retries 3 --retry-delay 2.0
```

## Input Formats

### JSON (List of Strings)
```json
[
  "What is Python?",
  "Explain machine learning",
  "Write a haiku"
]
```

### JSON (List of Objects)
```json
[
  {"prompt": "What is Python?", "max_tokens": 100},
  {"prompt": "Explain ML", "temperature": 0.8},
  {"prompt": "Write code", "max_tokens": 500, "temperature": 0.7}
]
```

### CSV
```csv
prompt,max_tokens,temperature
What is Python?,100,0.7
Explain machine learning,500,0.8
Write a haiku,50,0.9
```

## Output Formats

Results include:
- Original prompt
- Generated response
- Success status
- Error (if failed)
- Duration
- Retry count

## Options

- `--workers`: Number of concurrent workers (default: 3)
- `--retries`: Max retry attempts (default: 2)
- `--retry-delay`: Delay between retries in seconds (default: 1.0)
- `--rate-limit`: Minimum seconds between requests
- `--verbose`: Verbose output
- `--format`: Output format (json or csv)

## License

MIT License - see main package for details.
