# Mouser

A minimal Python script to periodically move the mouse and click, useful for preventing idle/lock-screen in automation scenarios.

## Features

- Configurable delay between actions (`--delay`)
- Configurable movement offset in pixels (`--movement`)
- Keyboard interrupt (Ctrl+C) to stop gracefully
## Requirements

- Python 3.8+
- `pyautogui` (install using pip)
## Setup

1. Clone or download this repository.
2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .\\.venv\\Scripts\\activate     # Windows PowerShell
   ```


3. Install dependencies:

    ```bash
    pip install pyautogui
    ```

## Usage

```bash
python mouser.py [OPTIONS]
```

### Arguments

- `--delay SECONDS` - Delay between actions in seconds (default: 60)
- `--movement PIXELS` - Random movement offset in pixels (default: 50)
- `--help` - Display help message

### Examples

```bash
# Run with default settings (60s delay, 50px movement)
python mouser.py

# Custom delay of 30 seconds
python mouser.py --delay 30

# Custom movement of 100 pixels
python mouser.py --movement 100

# Combine options
python mouser.py --delay 45 --movement 75
```

## How It Works

The script:
1. Moves the mouse by a random offset within the specified range
2. Performs a click action
3. Waits for the specified delay
4. Repeats until interrupted with Ctrl+C

## License

MIT
