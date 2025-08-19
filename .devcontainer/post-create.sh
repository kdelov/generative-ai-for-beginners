#!/bin/bash
set -e

echo "=== Starting post-create setup ==="

# Update pip to the latest version
python3 -m pip install --upgrade pip --disable-pip-version-check

# Install Python dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 --disable-pip-version-check --no-cache-dir install -r requirements.txt
else
    echo "No requirements.txt found, skipping Python dependencies installation."
fi

# Install Rust non-interactively
if ! command -v rustc >/dev/null 2>&1; then
    echo "Installing Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    # Add Rust to current shell session
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "Rust is already installed."
fi

# Optional: any additional setup commands
echo "=== Post-create setup completed! ==="
