# Makefile

# Python script path
SCRIPT_DIR := scripts
SCRIPT := $(SCRIPT_DIR)/download_and_generate.py

# URLs and file paths
EMOJI_TEST_URL := https://unicode.org/Public/emoji/latest/emoji-test.txt
EMOJI_TEST_FILE := emoji-test.txt
DART_OUTPUT_DIR := lib/src
DART_OUTPUT_FILE := $(DART_OUTPUT_DIR)/emoji_enum.dart

# Python dependencies
PYTHON := python3
PIP := pip
REQUIREMENTS := requirements.txt

# Default target
.PHONY: all
all: setup $(DART_OUTPUT_FILE)
	@echo "Emoji Enum Generator has been successfully executed."

# Setup dependencies
.PHONY: setup
setup:
	@if [ -f $(REQUIREMENTS) ]; then \
		$(PIP) install -r $(REQUIREMENTS); \
	else \
		$(PIP) install requests; \
	fi

# Generate Dart Enum
$(DART_OUTPUT_FILE): $(SCRIPT)
	@echo "Ensuring output directory exists..."
	@mkdir -p $(DART_OUTPUT_DIR)
	@echo "Running the Emoji Enum Generator script..."
	$(PYTHON) $(SCRIPT)

# Clean generated files
.PHONY: clean
clean:
	@echo "Cleaning generated files..."
	@rm -f $(DART_OUTPUT_FILE) $(EMOJI_TEST_FILE)
	@echo "Clean complete."

# Help message
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all      - Run the Emoji Enum Generator (default)"
	@echo "  setup    - Install Python dependencies"
	@echo "  clean    - Remove generated files"
	@echo "  help     - Show this help message"
