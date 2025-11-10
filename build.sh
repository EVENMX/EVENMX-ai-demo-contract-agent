#!/bin/bash
# Vercel build script to copy necessary files into the api directory
# This ensures all required files are available in the serverless function bundle

echo "=== Custom build script: Copying files for Vercel deployment ==="

# Create directories in api/ to mirror project structure
mkdir -p api/app/data
mkdir -p api/templates
mkdir -p api/static

# Copy app module files
echo "Copying app/ module..."
cp -r app/*.py api/app/
cp -r app/data/*.json api/app/data/
cp -r app/data/*.txt api/app/data/

# Copy templates
echo "Copying templates/..."
cp -r templates/*.html api/templates/

# Copy static files
echo "Copying static/..."
cp -r static/*.css api/static/

echo "=== Build complete: Files copied to api/ directory ==="

