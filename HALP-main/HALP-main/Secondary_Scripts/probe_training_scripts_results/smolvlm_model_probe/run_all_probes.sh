#!/bin/bash

################################################################################
# SmolVLM2-2.2B - Master Probe Training Script
################################################################################
# This script runs all 11 probe training scripts sequentially:
# - 1 vision_only probe
# - 5 vision_token probes (layers 0, 6, 12, 18, 23)
# - 5 query_token probes (layers 0, 6, 12, 18, 23)
################################################################################

set -e  # Exit on error

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base directory
BASE_DIR="/root/akhil/probe_training_scripts/smolvlm_model_probe"
cd "$BASE_DIR"

# Log file
MASTER_LOG="$BASE_DIR/master_training_$(date +%Y%m%d_%H%M%S).log"

echo "================================================================================" | tee -a "$MASTER_LOG"
echo "  SmolVLM2-2.2B Probe Training - Master Execution Script" | tee -a "$MASTER_LOG"
echo "================================================================================" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"
echo "Start time: $(date)" | tee -a "$MASTER_LOG"
echo "Master log: $MASTER_LOG" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

# Array of probe scripts
PROBE_SCRIPTS=(
    "01_vision_only_probe.py"
    "02_vision_token_layer0_probe.py"
    "03_vision_token_layer6_probe.py"
    "04_vision_token_layer12_probe.py"
    "05_vision_token_layer18_probe.py"
    "06_vision_token_layer23_probe.py"
    "07_query_token_layer0_probe.py"
    "08_query_token_layer6_probe.py"
    "09_query_token_layer12_probe.py"
    "10_query_token_layer18_probe.py"
    "11_query_token_layer23_probe.py"
)

TOTAL_PROBES=${#PROBE_SCRIPTS[@]}
SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_PROBES=()

# Function to display progress
display_progress() {
    local current=$1
    local total=$2
    local probe_name=$3

    echo "" | tee -a "$MASTER_LOG"
    echo "================================================================================" | tee -a "$MASTER_LOG"
    echo -e "${BLUE}[${current}/${total}] Running: ${probe_name}${NC}" | tee -a "$MASTER_LOG"
    echo "================================================================================" | tee -a "$MASTER_LOG"
    echo "" | tee -a "$MASTER_LOG"
}

# Run each probe script
for i in "${!PROBE_SCRIPTS[@]}"; do
    probe_script="${PROBE_SCRIPTS[$i]}"
    probe_num=$((i + 1))

    display_progress "$probe_num" "$TOTAL_PROBES" "$probe_script"

    start_time=$(date +%s)

    # Run probe training
    if python3 "$BASE_DIR/$probe_script" 2>&1 | tee -a "$MASTER_LOG"; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        minutes=$((duration / 60))
        seconds=$((duration % 60))

        echo "" | tee -a "$MASTER_LOG"
        echo -e "${GREEN}✓ SUCCESS: $probe_script (${minutes}m ${seconds}s)${NC}" | tee -a "$MASTER_LOG"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        minutes=$((duration / 60))
        seconds=$((duration % 60))

        echo "" | tee -a "$MASTER_LOG"
        echo -e "${RED}✗ FAILED: $probe_script (${minutes}m ${seconds}s)${NC}" | tee -a "$MASTER_LOG"
        FAILED_COUNT=$((FAILED_COUNT + 1))
        FAILED_PROBES+=("$probe_script")

        # Ask if user wants to continue
        echo "" | tee -a "$MASTER_LOG"
        echo -e "${YELLOW}Probe training failed. Continue with remaining probes? (y/n)${NC}"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "Aborting remaining probes..." | tee -a "$MASTER_LOG"
            break
        fi
    fi
done

# Final summary
echo "" | tee -a "$MASTER_LOG"
echo "================================================================================" | tee -a "$MASTER_LOG"
echo "  TRAINING SUMMARY" | tee -a "$MASTER_LOG"
echo "================================================================================" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"
echo "End time: $(date)" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"
echo "Total probes attempted: $TOTAL_PROBES" | tee -a "$MASTER_LOG"
echo -e "${GREEN}Successful: $SUCCESS_COUNT${NC}" | tee -a "$MASTER_LOG"
echo -e "${RED}Failed: $FAILED_COUNT${NC}" | tee -a "$MASTER_LOG"
echo "" | tee -a "$MASTER_LOG"

if [ $FAILED_COUNT -gt 0 ]; then
    echo "Failed probes:" | tee -a "$MASTER_LOG"
    for failed_probe in "${FAILED_PROBES[@]}"; do
        echo "  - $failed_probe" | tee -a "$MASTER_LOG"
    done
    echo "" | tee -a "$MASTER_LOG"
fi

if [ $SUCCESS_COUNT -eq $TOTAL_PROBES ]; then
    echo -e "${GREEN}✓ ALL PROBES COMPLETED SUCCESSFULLY!${NC}" | tee -a "$MASTER_LOG"
    exit 0
else
    echo -e "${YELLOW}⚠ Some probes failed. Check the log for details.${NC}" | tee -a "$MASTER_LOG"
    exit 1
fi
