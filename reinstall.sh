#!/bin/bash

# Script to properly reinstall cursor-agent-tools with fixed metadata

echo "Uninstalling cursor-agent-tools..."
pip3 uninstall -y cursor-agent-tools

echo "Cleaning up any build artifacts..."
rm -rf build/ dist/ *.egg-info

echo "Reinstalling package in development mode..."
pip3 install -e .

echo "Verifying installation..."
pip3 show cursor-agent-tools

echo "Done!" 