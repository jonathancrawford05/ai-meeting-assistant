# Installation Guide

## macOS Setup (Using Homebrew)

### Install ffmpeg
Instead of using `apt` (Linux), on macOS with Homebrew installed, use:

```bash
# Update Homebrew (equivalent to sudo apt update)
brew update

# Install ffmpeg (equivalent to sudo apt install ffmpeg -y)
brew install ffmpeg
```

### Verify Installation
```bash
ffmpeg -version
```

You should see output showing the ffmpeg version and configuration.

### Alternative Installation Methods

#### Using MacPorts
```bash
sudo port install ffmpeg
```

#### Using Conda
```bash
conda install -c conda-forge ffmpeg
```

## Python Environment Setup

### 1. Ensure pyenv is working
```bash
pyenv versions
pyenv install 3.11.0  # or your preferred version
pyenv local 3.11.0
```

### 2. Install Poetry (if not already installed)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Initialize the project
```bash
cd ai-meeting-assistant
poetry install
poetry shell
```

### 4. Run setup script
```bash
python setup.py
```

## Troubleshooting

### ffmpeg not found
- Make sure Homebrew is installed: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Add Homebrew to PATH: `echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc`

### Poetry not found
- Add Poetry to PATH: `echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc`
- Restart terminal or run: `source ~/.zshrc`
