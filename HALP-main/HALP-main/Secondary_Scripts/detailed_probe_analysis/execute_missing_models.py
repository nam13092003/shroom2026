#!/usr/bin/env python3
"""Execute analysis for the 2 missing models"""
import sys
import os

# Change to the correct directory
os.chdir('/root/akhil/detailed_probe_analysis')

# Run the analysis script
sys.path.insert(0, '/root/akhil/probe_analysis')
sys.path.insert(0, '/root/akhil/detailed_probe_analysis')

# Import and execute
exec(open('add_missing_models_results.py').read())
