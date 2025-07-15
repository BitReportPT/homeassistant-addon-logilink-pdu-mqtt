# Fixing "Cursor Agent" in Git History

## Problem

The repository shows "cursoragent Cursor Agent" as the contributor instead of your actual name. This happens when Cursor is configured as the git author.

## Quick Fix (Future Commits Only)

### Option 1: Run the Setup Script
```bash
chmod +x setup_git_config.sh
./setup_git_config.sh
```

### Option 2: Manual Configuration
```bash
# Configure git with your details
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Verify the configuration
git config --list | grep -E "(user\.name|user\.email)"
```

## Advanced Fix (Rewrite History)

⚠️ **Warning**: This rewrites git history and requires force push. Only do this if you're the sole contributor.

### Option 1: Run the Fix Script
```bash
chmod +x fix_git_author.sh
./fix_git_author.sh
```

### Option 2: Manual History Rewrite
```bash
# Replace with your actual details
export CORRECT_NAME="Your Name"
export CORRECT_EMAIL="your.email@example.com"

git filter-branch --env-filter '
OLD_EMAIL="cursoragent@cursor.com"
OLD_NAME="Cursor Agent"

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

# Clean up backup refs
git for-each-ref --format="%(refname)" refs/original/ | xargs -n 1 git update-ref -d

# Force push to update remote
git push --force-with-lease origin main
```

## Preventing Future Issues

### Configure Cursor to Use Your Git Config
1. Open Cursor settings
2. Go to Extensions > Git
3. Make sure "Use global git config" is enabled
4. Or set your git config globally:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### Alternative: Use .gitconfig
Create or edit `~/.gitconfig`:
```ini
[user]
    name = Your Name
    email = your.email@example.com
```

## Verification

Check your git log to verify the changes:
```bash
git log --oneline --format="%h %an <%ae> %s" -10
```

## Important Notes

- **Quick fix**: Only affects future commits
- **Advanced fix**: Rewrites entire history (requires force push)
- **Collaboration**: If others are working on the repo, coordinate before rewriting history
- **Backup**: Always backup your repository before rewriting history

## Why This Happens

Cursor sometimes configures git with its own credentials:
- `user.name=Cursor Agent`
- `user.email=cursoragent@cursor.com`

This makes all commits appear as if they were made by "Cursor Agent" instead of you.

## Best Practice

Always configure git with your actual credentials:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

This ensures all repositories use your credentials by default.