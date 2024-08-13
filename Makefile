# Variables
PYTHON = python3
PIP = pip3
NPM = pnpm
VITE = pnpm run dev

# Backend variables
BE_DIR = ./BE
BE_MAIN = $(BE_DIR)/main.py
BE_REQUIREMENTS = $(BE_DIR)/requirements.txt

# Frontend variables
FE_DIR = ./FE

# Targets
.PHONY: all backend frontend install_be install_fe clean_be clean_fe

# Install dependencies for backend and frontend
all: install_be install_fe

# Install backend dependencies
install_be:
	cd $(BE_DIR) && $(PIP) install -r $(BE_REQUIREMENTS)

# Install frontend dependencies
install_fe:
	cd $(FE_DIR) && $(NPM) install

# Run backend
backend:
	cd $(BE_DIR) && source env/bin/activate && uvicorn main:app --reload

# Run frontend
frontend:
	cd $(FE_DIR) && $(VITE)

# Clean backend (for example, remove __pycache__)
clean_be:
	rm -rf $(BE_DIR)/__pycache__

# Clean frontend (for example, remove node_modules)
clean_fe:
	rm -rf $(FE_DIR)/node_modules

# Clean both backend and frontend
clean: clean_be clean_fe

# Run both backend and frontend concurrently
start: backend frontend
