#!/bin/bash

# Script to fix git author configuration and commit history
# This removes "Cursor Agent" from the git history

echo "🔧 Fixing Git Author Configuration..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Get current git config
echo "📋 Current git configuration:"
git config --list | grep -E "(user\.name|user\.email)"

echo ""
echo "🔄 Setting up proper git configuration..."

# Set proper git configuration
# Replace these with your actual name and email
read -p "Enter your name: " USER_NAME
read -p "Enter your email: " USER_EMAIL

git config user.name "$USER_NAME"
git config user.email "$USER_EMAIL"

echo "✅ Git configuration updated:"
git config --list | grep -E "(user\.name|user\.email)"

echo ""
echo "🔄 Rewriting commit history to remove Cursor Agent..."

# Rewrite commit history to change author
git filter-branch --env-filter '
OLD_EMAIL="cursoragent@cursor.com"
OLD_NAME="Cursor Agent"
CORRECT_NAME="'$USER_NAME'"
CORRECT_EMAIL="'$USER_EMAIL'"

if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ] || [ "$GIT_COMMITTER_NAME" = "$OLD_NAME" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi

if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ] || [ "$GIT_AUTHOR_NAME" = "$OLD_NAME" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags

echo ""
echo "✅ Commit history rewritten!"

echo ""
echo "📊 Checking commit history..."
git log --oneline --format="%h %an <%ae> %s" -10

echo ""
echo "🚀 Next steps:"
echo "1. Review the commit history above"
echo "2. If everything looks good, force push to update remote:"
echo "   git push --force-with-lease origin main"
echo ""
echo "⚠️  Warning: This will rewrite git history on the remote repository!"
echo "   Make sure no one else is working on the repository before doing this."

# Clean up backup refs
echo ""
echo "🧹 Cleaning up backup references..."
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

echo ""
echo "✅ Git author fix completed!"