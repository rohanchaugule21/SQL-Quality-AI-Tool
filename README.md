# SQL Quality AI Tool

Automated T-SQL code quality analysis using local AI to detect performance issues, security vulnerabilities, and best practice violations before deployment.

## Overview

SQL Quality AI Tool is a production-ready system that analyzes T-SQL stored procedures and scripts to identify code quality issues. It combines rule-based pattern detection with local AI (Ollama) to provide intelligent, context-aware recommendations.

**Built for:** Database engineers, DBAs, and development teams working with SQL Server

**Problem Solved:** Manual SQL code review is time-consuming (20-30 minutes per procedure), inconsistent across reviewers, and creates deployment bottlenecks. This tool automates the review process with 98% time reduction while maintaining quality.


## Key Features

- **Automated Static Analysis** - Detects SELECT *, cursors, non-sargable predicates, NOLOCK hints, and other anti-patterns
- **AI-Powered Explanations** - Uses local LLM (DeepSeek-Coder via Ollama) to explain issues and suggest fixes
- **Multiple Interfaces** - Web dashboard (Streamlit) for interactive use and CLI for automation
- **Zero Cost Operation** - Runs entirely locally with no API fees or cloud services
- **CI/CD Integration** - Compatible with GitHub Actions, Azure DevOps, and Git hooks
- **Production Tested** - Successfully analyzed 600+ line production procedures


## Technologies Used

- **Python 3.11** - Core implementation
- **sqlparse** - SQL syntax parsing
- **Ollama + DeepSeek-Coder** - Local AI for intelligent analysis
- **Streamlit** - Interactive web dashboard
- **YAML** - Configuration management

## Installation

### Prerequisites
- Python 3.11 or higher
- 4GB+ RAM
- Ollama installed ([https://ollama.com/download](https://ollama.com/download))

### Setup Steps

1. Clone the repository
```bash
git clone https://github.com/rohanchaugule21/SQL-Quality-AI-Tool.git
cd SQL-Quality-AI-Tool
```

2. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Download AI model (one-time, ~3.8GB)
```bash
ollama pull deepseek-coder:6.7b
```

5. Verify installation
```bash
python cli/analyze.py test_procedure.sql
```

## Usage

### Web Dashboard

```bash
streamlit run dashboard/app.py
```

Opens browser at http://localhost:8501

- Paste SQL code or upload .sql file
- Click "Analyze Code"
- Review results with AI explanations

### Command Line

```bash
# Analyze a file
python cli/analyze.py path/to/stored_procedure.sql

# Fast mode (without AI)
python cli/analyze.py stored_procedure.sql --no-ai

# JSON output for automation
python cli/analyze.py stored_procedure.sql --output json
```


## Detection Rules

| Rule ID | Description | Severity |
|---------|-------------|----------|
| SQL001 | SELECT * usage | Warning |
| SQL002 | Missing SET NOCOUNT ON | Info |
| SQL003 | Non-sargable predicates (functions in WHERE) | Warning |
| SQL004 | Cursor usage | Warning |
| SQL005 | NOLOCK hint | Warning |

Each detected issue includes:
- Exact line number
- Code context
- AI explanation of the problem
- Suggested fix with code example
- Performance impact estimate


## Project Structure

```
SQL-Quality-AI-Tool/
├── src/
│   ├── static_analyzer/        # Core analysis engine
│   └── llm/                    # AI integration
├── cli/                        # Command-line tool
├── dashboard/                  # Web interface
├── tests/                      # Test suite
├── docs/                       # Documentation
├── config.yaml                 # Configuration
└── requirements.txt            # Dependencies
```

## Configuration

Edit `config.yaml` to customize:

```yaml
analysis:
  use_ai: true
  ai_model: "deepseek-coder:6.7b"

rules:
  select_star:
    enabled: true
    severity: WARNING
  cursor:
    enabled: true
    severity: WARNING
```


## CI/CD Integration

### GitHub Actions

Add `.github/workflows/sql-check.yml`:

```yaml
name: SQL Quality Check

on:
  pull_request:
    paths:
      - '**.sql'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - run: pip install -r requirements.txt
    - run: |
        curl -fsSL https://ollama.com/install.sh | sh
        ollama pull deepseek-coder:6.7b
    - run: python cli/analyze.py **/*.sql
```

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
for file in $(git diff --cached --name-only | grep '\.sql$'); do
  python cli/analyze.py "$file" --no-ai || exit 1
done
```


## Roadmap

**Phase 1 (Completed):**
- Static code analysis with 5 rules
- AI-powered explanations
- Web dashboard and CLI
- Production testing

**Phase 2 (Planned - Q4 2026):**
- Git hooks and CI/CD templates
- VS Code extension
- Batch analysis tool

**Phase 3 (Planned - Q1 2027):**
- Query Store integration (runtime performance)
- Execution plan analysis
- Missing index recommendations

## Contributing

Contributions are welcome. To add a new detection rule:

1. Edit `src/static_analyzer/rules.py`
2. Create a class extending `SQLRule`
3. Implement the `check()` method
4. Add to `ALL_RULES` list
5. Update `config.yaml`
6. Submit pull request