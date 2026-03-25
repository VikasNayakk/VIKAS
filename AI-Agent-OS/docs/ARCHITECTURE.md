"""
AI-Agent-OS Architecture Documentation

## System Overview
AI-Agent-OS is an enterprise-grade autonomous agent system that understands natural language,
plans tasks, and executes them on your computer - just like a human would.

## Key Features
✅ Event-driven architecture (no circular dependencies)
✅ Hierarchical Agent System (Coordinator → Executor, Planner, Monitor)
✅ 3-tier memory system (Cache → Context → Vector DB)
✅ AI fallback chain (OpenAI → Local LLM)
✅ Circuit breaker pattern (prevent cascading failures)
✅ Vision system with caching
✅ Sandbox execution environment
✅ Structured logging & observability

## Architecture

```
┌──────────────────────────────────────────────┐
│         User Interface / API                 │
└─────────────────┬──────────────────────────┘
                  │
         ┌────────▼─────────┐
         │   Event Bus      │  (Central pub/sub)
         └────────┬─────────┘
                  │
    ┌─────────────▼─────────────┐
    │  Kernel (Main Event Loop) │
    └─────────────┬─────────────┘
                  │
    ┌─────────────▼──────────────┐
    │  State Manager (Event Log) │
    └────────────────────────────┘

                  │
    ┌─────────────▼──────────────────┐
    │   Agent System (HAT)           │
    │                                │
    │  ┌─────────────────────────┐  │
    │  │  Coordinator (Central)  │  │
    │  └──┬──────────┬──────────┬┘  │
    │     │          │          │   │
    │  ┌──▼──┐  ┌───▼──┐  ┌───▼──┐ │
    │  │Plan │  │Exec  │  │Learn │ │
    │  └─────┘  └──────┘  └──────┘ │
    └────────────────────────────────┘

┌──────────────────────────────────┐
│  Brain System                    │
│  ├── Intent Parser               │
│  ├── LLM (Fallback Chain)        │
│  │   ├── OpenAI                  │
│  │   └── Local LLM               │
│  └── Memory (3-tier)             │
│      ├── Cache                   │
│      ├── Context                 │
│      └── Vector DB               │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│  Perception / Vision             │
│  ├── Screen Capture              │
│  ├── UI Detection                │
│  └── OCR                         │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│  Actions                         │
│  ├── Mouse Control               │
│  ├── Keyboard Control            │
│  └── App Control                 │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│  Security                        │
│  ├── Code Sandbox                │
│  ├── Permission Manager          │
│  └── Audit Log                   │
└──────────────────────────────────┘
```

## Component Details

### Core
- **event_bus.py**: Central pub/sub for all communication
- **state_manager.py**: Event-sourced state with versioning
- **kernel.py**: Main event loop and lifecycle management

### Brain
- **llm/**: AI providers with fallback chain
  - openai_provider.py: GPT-4 via OpenAI API
  - local_provider.py: Ollama/Transformers local models
  - circuit_breaker.py: Prevent cascading failures
  - fallback_chain.py: Try multiple providers
  - response_cache.py: Cache LLM responses
- **parser/**: Parse natural language into intents
  - intent_parser.py: Convert "send hello to himanshu" → structured intent
- **memory/**: 3-tier memory system
  - memory_system.py: Cache, Context, Vector DB

### Agents (HAT Architecture)
- **agent_system.py**: Hierarchical agent coordination
  - Coordinator: Routes messages, manages task queue
  - Executor: Low-level action execution
  - Planner: Break tasks into steps
  - Monitor: Track system health & metrics

### Vision
- **vision_system.py**: Screen analysis
  - Fast capture with MSS
  - Caching to avoid reprocessing
  - OCR for text extraction

### Actions
- **executor.py**: Execute on system
  - Mouse: move, click, drag
  - Keyboard: type, hotkeys
  - Apps: launch, close

### Security
- **sandbox.py**: Safe code execution
  - RestrictedPython for isolation
  - Permission checks
  - Audit logging

### Observability
- **logging.py**: Structured logging
  - Metrics collection
  - Performance tracing
  - System monitoring

## Execution Flow

```
1. User Command
   "send hello to himanshu"
         │
         ▼
2. Event Emitted
   Event(type=USER_COMMAND, data={command: "..."})
         │
         ▼
3. Intent Parsed
   Intent(action=send_message, target=himanshu, parameters={message: "hello"})
         │
         ▼
4. Task Added to Coordinator
   task_id = await coordinator.add_task(task)
         │
         ▼
5. Planner Breaks into Steps
   [open_teams → find_contact → type_message → send]
         │
         ▼
6. Executor Executes Steps
   - Vision: Analyze screen for Teams UI
   - Actions: Launch app, navigate, type, send
   - Monitoring: Track success, retry on failure
         │
         ▼
7. Result
   Task completed, event logged
```

## Key Design Patterns

### 1. Event Sourcing
- All state changes are immutable events
- Complete audit trail
- Easy rollback and recovery

### 2. Circuit Breaker
- API fails → stop calling → recovery period → try again
- Prevents wasting resources on broken services

### 3. Fallback Chain
- OpenAI fails? Try local model
- Always have backup option

### 4. Hierarchical Agents
- Central coordinator
- Specialized agents (executor, planner, monitor)
- Message-based communication (no circular deps)

### 5. Caching Strategy
- L1: In-memory cache (5sec TTL)
- L2: Session context (current task)
- L3: Vector DB (semantic search)

## Configuration

Edit `config/config.yaml`:

```yaml
system:
  version: "1.0.0"
  debug: false
  timeout: 30

llm:
  provider: "openai"  # or "local"
  model: "gpt-4"
  temperature: 0.7

vision:
  cache_ttl: 5
  use_ocr: true

security:
  sandbox_enabled: true
  permission_checks: true
```

## Example Usage

```python
import asyncio
from main import AIAgentOS

async def main():
    system = AIAgentOS()
    await system.initialize()
    
    # Send command
    await system.send_command("send hello to himanshu")
    await asyncio.sleep(2)
    
    # Send another
    await system.send_command("open chrome")
    
    await system.shutdown()

asyncio.run(main())
```

## Extension Points

1. **Custom Workflow**: Add to `workflows/`
2. **Custom Agent**: Inherit from `BaseAgent`
3. **Custom Skill**: Add to `agents/skills/`
4. **Custom Integration**: Add to `integrations/`
5. **Custom Plugin**: Add to `plugins/`

## Performance Notes

- Vision captures every 0.5s (configurable)
- LLM responses cached to avoid duplicate calls
- Agents run concurrently using asyncio
- Long operations don't block event loop

## Security Practices

✅ All user code runs in sandbox
✅ Permission checks before actions
✅ Audit log of all operations
✅ HTTPS for external APIs
✅ No credentials in code (use .env)

## Troubleshooting

See `docs/TROUBLESHOOTING.md` for common issues.
"""
