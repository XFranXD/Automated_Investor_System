#!/bin/bash

# Target backup directory and archive name setup
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="automated_investor_bot_backup_${TIMESTAMP}.zip"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Print execution message
echo "Starting backup of Automated Investor Bot..."
echo "Excluding 'venv', '.env', '.git', and the 'backups' directory."

# Create backups directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Run zip to compress the project directory recursively (-r) and quietly (-q)
# -x specifies patterns/directories to exclude
zip -q -r "$BACKUP_PATH" . \
    -x "venv/*" \
    -x ".git/*" \
    -x "backups/*" \
    -x ".env" \
    -x "backup.sh"

# Check if zip exited successfully
if [ $? -eq 0 ]; then
    echo "----------------------------------------"
    echo "Backup completed successfully!"
    echo "Saved to: $BACKUP_PATH"
    echo "Size: $(du -sh "$BACKUP_PATH" | cut -f1)"
    echo "----------------------------------------"
else
    echo "Error: Backup failed." >&2
    exit 1
fi
