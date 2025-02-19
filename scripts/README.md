# Test Scripts

This directory contains test scripts for different browser automation approaches used in research.

## Available Scripts

- `test_browser_use.py`: Test Browser-use-based research
- `test_nodriver.py`: Test NoDriver-based research
- `test_patchright.py`: Test Patchright-based research

## Usage

All test scripts support the same command-line arguments:

```bash
python -m scripts.test_patchright --query "your query" --site perplexity --headless true
```

### Arguments

- `--query` (required): The research query to execute
- `--site` (optional): Research site to use (default: gemini)
  - Available sites: gemini, perplexity
- `--headless` (optional): Whether to run in headless mode (default: true)

### Examples

1. Using Patchright with Perplexity:
```bash
python -m scripts.test_patchright \
  --query "Compare GPT-4 vs Gemini in summarizing climate change data" \
  --site perplexity \
  --headless true
```

2. Using NoDriver with Gemini:
```bash
python -m scripts.test_nodriver \
  --query "Analyze recent Gemini updates" \
  --site gemini \
  --headless false
```

3. Using Browser-use with Perplexity:
```bash
python -m scripts.test_browser_use \
  --query "Research quantum computing advancements" \
  --site perplexity \
  --headless true
```

## Environment Variables

Required for Gemini research:
- `GOOGLE_EMAIL`: Google account email
- `GOOGLE_PASSWORD`: Google account password
- `GOOGLE_2FA_SECRET` (optional): If 2FA is enabled

No authentication required for Perplexity research.

## Output

Each script will output:
1. Progress messages during execution
2. Research results formatted with separators
3. Any errors that occur during execution

## Error Handling

Scripts will:
1. Validate the site selection
2. Check for required environment variables (for Gemini)
3. Handle browser automation errors
4. Clean up resources on completion or error

## Adding New Sites

When adding support for new research sites:
1. Add the site to `ResearchSite` enum in `config.py`
2. Add site configuration to `SITE_CONFIGS`
3. Implement the site-specific scraper
4. Test using these scripts with the new site option 