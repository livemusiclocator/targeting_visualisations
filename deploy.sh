#!/bin/bash
# This script prepares and deploys the visualizations to GitHub.

# --- Configuration ---
# Your GitHub username and the repository name.
# Please ensure this matches your setup.
GITHUB_USERNAME="livemusiclocator"
REPO_NAME="targeting_visualisations"

# --- Git Operations ---
echo "--- Starting Deployment Process ---"

# Step 1: Ensure we are in a git repository.
# If not, initialize it. If so, this does nothing harmful.
git init

# Step 2: Set the main branch name to 'main' if it isn't already.
# This is the modern standard.
git branch -M main

# Step 3: Remove any lingering staging issues.
echo "--- Resetting staging area... ---"
git reset

# Step 4: Add only the files we want to deploy.
# The .gitignore file will ensure that .py and .csv files are ignored.
echo "--- Staging all permitted files... ---"
git add .

# Step 5: Commit the files.
echo "--- Committing files... ---"
git commit -m "Deploying interactive visualizations" --allow-empty

# Step 6: Connect this local repository to your GitHub repository.
echo "--- Setting up remote repository connection... ---"
# Remove any old remote connection to avoid errors.
git remote remove origin
git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

# Step 7: Push the committed files to GitHub.
# The -u flag sets the upstream branch for future pushes.
# The -f flag forces the push, which is useful for overwriting a
# repository's history, as needed for this initial setup.
echo "--- Pushing files to GitHub... ---"
echo "--- IMPORTANT: Please enter your GitHub credentials if prompted. ---"
git push -u -f origin main

echo "--- Deployment Complete! ---"
echo "Your visualizations should now be available at:"
echo "https://livemusiclocator.github.io/targeting_visualisations/"