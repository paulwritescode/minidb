# MiniDB Project Makefile
# Usage: make <command>

.PHONY: help setup install start repl clean

# Default target
help:
	@echo "MiniDB Project Commands:"
	@echo "  make setup    - Create virtual environment and install dependencies"
	@echo "  make install  - Install/update dependencies (requires existing venv)"
	@echo "  make start    - Start the web application"
	@echo "  make repl     - Start interactive REPL mode"
	@echo "  make clean    - Remove virtual environment and generated files"
	@echo "  make help     - Show this help message"

# Create virtual environment and install dependencies
setup:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Activating environment and installing dependencies..."
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Setup complete! Use 'make start' to run the application."

# Install/update dependencies (assumes venv exists)
install:
	@echo "Installing dependencies..."
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "Dependencies installed!"

# Start the web application
start:
	@echo "Starting MiniDB web application..."
	@echo "Opening at http://127.0.0.1:8001/"
	. venv/bin/activate && python3 app.py

# Start interactive REPL mode
repl:
	@echo "Starting MiniDB REPL mode..."
	@echo "Type 'exit' to quit, '.help' for commands"
	. venv/bin/activate && python3 minidb.py

# Clean up generated files and virtual environment
clean:
	@echo "Cleaning up..."
	rm -rf venv/
	rm -rf __pycache__/
	rm -f *.json
	rm -f *.log
	@echo "Cleanup complete!"

# Check if virtual environment exists
check-venv:
	@if [ ! -d "venv" ]; then \
		echo "Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi

# Start with environment check
start-safe: check-venv start
repl-safe: check-venv repl