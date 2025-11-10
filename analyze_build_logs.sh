#!/bin/bash
###############################################################################
# Fetch and analyze GitHub Actions build logs
###############################################################################

set -e

echo "=============================================================================="
echo "  GITHUB ACTIONS BUILD LOG ANALYZER"
echo "=============================================================================="
echo ""

# Get latest workflow run
echo "[1] Fetching latest workflow run..."

if command -v gh &> /dev/null; then
    echo "✓ GitHub CLI found"

    # Get the latest run
    RUN_ID=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId' 2>/dev/null || echo "")

    if [ -n "$RUN_ID" ]; then
        echo "✓ Latest run ID: $RUN_ID"

        # Get the run status
        STATUS=$(gh run view $RUN_ID --json status --jq '.status' 2>/dev/null || echo "unknown")
        CONCLUSION=$(gh run view $RUN_ID --json conclusion --jq '.conclusion' 2>/dev/null || echo "unknown")

        echo "  Status: $STATUS"
        echo "  Conclusion: $CONCLUSION"

        # Download logs
        echo ""
        echo "[2] Downloading build logs..."
        gh run view $RUN_ID --log > github_actions_build.log 2>&1 || true

        if [ -f "github_actions_build.log" ]; then
            echo "✓ Logs saved to: github_actions_build.log"

            # Analyze logs
            echo ""
            echo "[3] Analyzing logs for errors..."
            echo "=============================================================================="

            # Look for common error patterns
            echo ""
            echo "--- ERRORS ---"
            grep -i "error" github_actions_build.log | grep -v "error only" | tail -20 || echo "No errors found in grep"

            echo ""
            echo "--- FAILURES ---"
            grep -i "fail" github_actions_build.log | tail -20 || echo "No failures found"

            echo ""
            echo "--- RECIPE ISSUES ---"
            grep -i "recipe\|xlsxwriter" github_actions_build.log | tail -20 || echo "No recipe mentions found"

            echo ""
            echo "--- P4A TOOLCHAIN ---"
            grep -i "pythonforandroid\|p4a\|toolchain" github_actions_build.log | tail -20 || echo "No p4a mentions found"

            echo ""
            echo "--- BUILD COMMAND ---"
            grep -i "command failed\|buildozer" github_actions_build.log | tail -10 || echo "No command failures found"

            echo ""
            echo "=============================================================================="
            echo "Full log file: github_actions_build.log"
            echo "Lines: $(wc -l < github_actions_build.log)"
            echo "=============================================================================="
        else
            echo "✗ Failed to download logs"
        fi
    else
        echo "✗ No workflow runs found"
    fi
else
    echo "✗ GitHub CLI (gh) not installed"
    echo ""
    echo "To install:"
    echo "  On Debian/Ubuntu: sudo apt install gh"
    echo "  On macOS: brew install gh"
    echo ""
    echo "Or manually view logs at:"
    echo "  https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')/actions"
fi

echo ""
echo "=============================================================================="
echo "  MANUAL LOG ANALYSIS"
echo "=============================================================================="
echo ""
echo "If automated fetch failed, manually check:"
echo "1. Go to GitHub repository"
echo "2. Click 'Actions' tab"
echo "3. Click latest failed run"
echo "4. Click 'build' job"
echo "5. Look for the actual error in the logs"
echo ""
echo "Common error locations:"
echo "  - After 'Build APK' step"
echo "  - Look for 'Command failed'"
echo "  - Look for 'STDERR:'"
echo "  - Look for Python traceback"
echo ""
