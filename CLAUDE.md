# Chess Practice

## Running the project
```bash
cd /c/Users/Justian/Documents/Scripts/chess-practice && ./.venv/Scripts/python.exe chess_game.py
```

## Running tests
```bash
cd /c/Users/Justian/Documents/Scripts/chess-practice && .venv/Scripts/python.exe -m pytest -v
```

## Package manager
This project uses Poetry. Always use `poetry add <package>` for new dependencies and `poetry add --group dev <package>` for dev dependencies.

## Project structure
- `chess/` - Core chess logic (pure Python, no UI dependencies)
- `graphics/` - Pygame rendering and UI components
- `assets/sprites/` - Chess piece SVG sprites
- `tests/` - Pytest test suite

## Workflow
Be sure at the end of building every feature that:
- All previous tests are passing
- There are unit tests covering the new behaviors
- The README.md is up-to-date
- The ROADMAP.md is up-to-date (check off any features we completed)