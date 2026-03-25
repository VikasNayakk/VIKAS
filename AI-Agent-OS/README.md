"""
AI-Agent-OS
Autonomous Agent System for Windows

## Quick Start

### 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy config template
cp config/config.example.yaml config/config.yaml

# Edit config and add your OpenAI API key
# Set environment variable: $env:OPENAI_API_KEY = "your-key"
```

### 2. Run

```bash
python main.py
```

### 3. Use

```
Type commands naturally:
> send hello to himanshu
> open chrome
> take screenshot
> search python tutorial
> type hello world
```

## Examples

### Send Message
```
> send hello to himanshu on teams
AI will:
1. Launch Teams
2. Find Himanshu in contacts
3. Type message
4. Send
```

### Open and Search
```
> open chrome and search python tutorials
AI will:
1. Launch browser
2. Click search bar
3. Type query
4. Display results
```

### File Operations
```
> create file test.txt with hello world
AI will:
1. Open text editor
2. Type content
3. Save file
```

## Architecture

See full architecture in: `docs/ARCHITECTURE.md`

Key components:
- **Event Bus**: Central pub/sub (no circular deps)
- **Agents**: Coordinator → Executor, Planner, Monitor (HAT)
- **Memory**: 3-tier (Cache → Context → Vector DB)
- **LLM**: Fallback chain (OpenAI → Local)
- **Vision**: Screenshot with smart caching
- **Security**: Sandboxed execution

## Configuration

Edit `config/config.yaml`:

```yaml
llm:
  provider: "openai"  # or "local"
  openai_model: "gpt-4"

vision:
  cache_ttl: 5
  use_ocr: true

security:
  sandbox_enabled: true
```

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt pytest black flake8

# Run tests
pytest tests/

# Format code
black .

# Lint
flake8 .
```

## Troubleshooting

### Issue: "OpenAI API key not found"
Solution: Set environment variable
```bash
$env:OPENAI_API_KEY = "sk-..."
```

### Issue: Tesseract OCR not found
Solution: Install Tesseract
Windows: Download from https://github.com/UB-Mannheim/tesseract

### Issue: Agent not responding
Solution: Check logs in `data/logs/system.log`

## Performance Tips

1. **Enable caching**: `memory.cache_ttl: 300`
2. **Use local LLM**: Faster than OpenAI for simple tasks
3. **Adjust capture interval**: `vision.capture_interval: 1` for slower systems
4. **Monitor resources**: Check `Monitor` agent metrics

## Security

✅ All code runs in sandbox
✅ Permission checks before actions  
✅ Audit log of all operations
✅ No credentials in code (use env vars)

## License

MIT

## Support

See documentation in `docs/` folder.
"""
