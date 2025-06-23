#!/bin/bash
# This script removes previously tracked files that should be ignored.

echo "--- Starting Repository Fix ---"

# Step 1: Remove every file from Git's tracking index.
# The --cached flag means the files will be untracked but not deleted from your local disk.
echo "--- Untracking all files... ---"
git rm -r --cached .

# Step 2: Re-add all files.
# Git will now re-read the .gitignore file and add only the files that are not ignored.
echo "--- Re-staging all permitted files... ---"
git add .

# Step 3: Commit the changes.
# This creates a new commit that reflects the correct state of the repository.
echo "--- Committing the fix... ---"
git commit -m "Fix: Remove previously tracked .py and .csv files"

# Step 4: Force-push the corrected commit to GitHub.
# This will overwrite the previous history on the remote.
echo "--- Pushing the fix to GitHub... ---"
git push -f origin main

echo "--- Repository Fix Complete! ---"
echo "The Python and data files should now be removed from your GitHub repository."