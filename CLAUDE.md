# Chess Practice

## Running the project
```bash
poetry run python chess_game.py
```

## Running tests
```bash
poetry run pytest
```

## Package manager
This project uses Poetry. Always use `poetry add <package>` for new dependencies and `poetry add --group dev <package>` for dev dependencies.

## Project structure
- `chess/` - Core chess logic (pure Python, no UI dependencies)
- `graphics/` - Pygame rendering and UI components
- `assets/sprites/` - Chess piece SVG sprites
- `tests/` - Pytest test suite
