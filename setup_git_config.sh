#!/bin/bash

# Simple script to configure git properly for future commits

echo "🔧 Configuring Git for Future Commits..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Show current configuration
echo "📋 Current git configuration:"
git config --list | grep -E "(user\.name|user\.email)"

echo ""
echo "🔄 Setting up proper git configuration..."

# Set proper git configuration
read -p "Enter your name: " USER_NAME
read -p "Enter your email: " USER_EMAIL

git config user.name "$USER_NAME"
git config user.email "$USER_EMAIL"

echo ""
echo "✅ Git configuration updated:"
git config --list | grep -E "(user\.name|user\.email)"

echo ""
echo "🚀 Future commits will now use your credentials!"
echo ""
echo "📝 Note: This only affects new commits."
echo "   To fix existing commits, you would need to rewrite git history."
echo "   Use 'fix_git_author.sh' if you want to do that (advanced)."