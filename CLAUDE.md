# Chess Practice

## Running the project
```bash
./.venv/Scripts/python.exe chess_game.py
```

## Running tests
```bash
./.venv/Scripts/python.exe -m pytest
```

## Package manager
This project uses Poetry. Always use `poetry add <package>` for new dependencies and `poetry add --group dev <package>` for dev dependencies.

## Project structure
- `chess/` - Core chess logic (pure Python, no UI dependencies)
- `graphics/` - Pygame rendering and UI components
- `assets/sprites/` - Chess piece SVG sprites
- `tests/` - Pytest test suite
