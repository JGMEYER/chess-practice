# Python Practice

A Python project for practicing and experimenting with Python code.

## Requirements

- Python 3.12+
- Poetry 2.2+

## Setup

1. Install dependencies and create virtual environment:
   ```bash
   poetry install
   ```

2. The virtual environment is created in `.venv/` within the project directory.

## Running Scripts

Run Python scripts using Poetry:
```bash
poetry run python main.py
```

Or activate the virtual environment shell:
```bash
poetry shell
python main.py
```

## Managing Dependencies

Add a new dependency:
```bash
poetry add <package-name>
```

Add a development dependency:
```bash
poetry add --group dev <package-name>
```

Remove a dependency:
```bash
poetry remove <package-name>
```

Update all dependencies:
```bash
poetry update
```

## Project Structure

```
python-practice/
├── .venv/              # Virtual environment (in-project)
├── main.py             # Main script
├── poetry.lock         # Locked dependency versions
├── pyproject.toml      # Project configuration
└── README.md
```
