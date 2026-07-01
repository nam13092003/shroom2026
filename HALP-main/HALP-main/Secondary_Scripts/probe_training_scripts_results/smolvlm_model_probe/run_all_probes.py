#!/usr/bin/env python3
"""
SmolVLM2-2.2B - Master Probe Training Script (Python Version)
==============================================================
Runs all 11 probe training scripts sequentially with comprehensive logging.
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Configuration
BASE_DIR = Path("/root/akhil/probe_training_scripts/smolvlm_model_probe")
PYTHON_BIN = "python3"

# Probe scripts in execution order
PROBE_SCRIPTS = [
    "01_vision_only_probe.py",
    "02_vision_token_layer0_probe.py",
    "03_vision_token_layer6_probe.py",
    "04_vision_token_layer12_probe.py",
    "05_vision_token_layer18_probe.py",
    "06_vision_token_layer23_probe.py",
    "07_query_token_layer0_probe.py",
    "08_query_token_layer6_probe.py",
    "09_query_token_layer12_probe.py",
    "10_query_token_layer18_probe.py",
    "11_query_token_layer23_probe.py",
]

def print_header(message):
    """Print formatted header."""
    print("\n" + "=" * 80)
    print(f"  {message}")
    print("=" * 80 + "\n")

def print_progress(current, total, probe_name):
    """Print progress indicator."""
    print("\n" + "=" * 80)
    print(f"  [{current}/{total}] Running: {probe_name}")
    print("=" * 80 + "\n")

def format_duration(seconds):
    """Format duration in human-readable format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"

def run_probe(script_path, script_name, probe_num, total_probes):
    """Run a single probe training script."""
    print_progress(probe_num, total_probes, script_name)

    start_time = time.time()

    try:
        # Run the script
        result = subprocess.run(
            [PYTHON_BIN, str(script_path)],
            cwd=BASE_DIR,
            capture_output=False,  # Show output in real-time
            text=True,
            check=True
        )

        end_time = time.time()
        duration = int(end_time - start_time)

        print(f"\n✓ SUCCESS: {script_name} ({format_duration(duration)})")
        return True, duration

    except subprocess.CalledProcessError as e:
        end_time = time.time()
        duration = int(end_time - start_time)

        print(f"\n✗ FAILED: {script_name} ({format_duration(duration)})")
        print(f"Error code: {e.returncode}")
        return False, duration

    except KeyboardInterrupt:
        print(f"\n⚠ INTERRUPTED: {script_name}")
        raise

def main():
    """Main execution function."""
    print_header("SmolVLM2-2.2B Probe Training - Master Execution")

    start_time_overall = datetime.now()
    print(f"Start time: {start_time_overall.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base directory: {BASE_DIR}")
    print(f"Total probes: {len(PROBE_SCRIPTS)}")

    # Track results
    results = []
    success_count = 0
    failed_count = 0

    # Run each probe
    for idx, script_name in enumerate(PROBE_SCRIPTS, 1):
        script_path = BASE_DIR / script_name

        if not script_path.exists():
            print(f"\n✗ ERROR: Script not found: {script_name}")
            failed_count += 1
            results.append({
                'script': script_name,
                'success': False,
                'duration': 0,
                'error': 'Script not found'
            })
            continue

        success, duration = run_probe(script_path, script_name, idx, len(PROBE_SCRIPTS))

        results.append({
            'script': script_name,
            'success': success,
            'duration': duration
        })

        if success:
            success_count += 1
        else:
            failed_count += 1

    # Final summary
    end_time_overall = datetime.now()
    total_duration = int((end_time_overall - start_time_overall).total_seconds())

    print_header("TRAINING SUMMARY")

    print(f"End time: {end_time_overall.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total duration: {format_duration(total_duration)}\n")

    print(f"Total probes: {len(PROBE_SCRIPTS)}")
    print(f"✓ Successful: {success_count}")
    print(f"✗ Failed: {failed_count}\n")

    # Detailed results
    print("Detailed Results:")
    print("-" * 80)
    for result in results:
        status = "✓" if result['success'] else "✗"
        duration_str = format_duration(result['duration'])
        print(f"  {status} {result['script']:<40} {duration_str:>10}")

    print("-" * 80)

    # Failed probes
    if failed_count > 0:
        print("\nFailed Probes:")
        for result in results:
            if not result['success']:
                error_msg = f" ({result.get('error')})" if 'error' in result else ""
                print(f"  - {result['script']}{error_msg}")

    print()

    # Exit status
    if success_count == len(PROBE_SCRIPTS):
        print("✓ ALL PROBES COMPLETED SUCCESSFULLY!")
        return 0
    else:
        print("⚠ Some probes failed. Check the output for details.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Execution interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
