# Model Context Protocol (MCP) Integration — BhagvadMood Journal

> **Document Version:** 1.0.0  
> **Project:** BhagvadMood Journal  

---

## 1. Overview & Purpose

The **Model Context Protocol (MCP)** integration enables AI agents (e.g., in Antigravity IDE, Claude Desktop, or Cursor) to securely query the BhagvadMood journaling engine as a structured toolset without exposing raw sensitive databases.

---

## 2. MCP Server Configuration

`mcp_config.json`:
```json
{
  "mcpServers": {
    "bhagvadmood-journal": {
      "command": "python",
      "args": ["-m", "services.mcp_server"],
      "env": {
        "DB_PATH": "bhagvadmood.db",
        "APP_ENV": "development"
      }
    }
  }
}
```

---

## 3. Exposed MCP Tools

1. **`analyze_journal_sentiment`**: Analyzes text payload and returns polarity, subjectivity, and emotional vector.
2. **`fetch_vedic_counsel`**: Retrieves Gita shloka and philosophical reframe for an identified emotional state.
3. **`check_crisis_indicators`**: Evaluates crisis keywords and returns harm prevention alerts.
4. **`summarize_mood_trends`**: Provides aggregate anonymized mood distribution over a specified time window.
