---
name: vault-push
description: Push a vault note to Perceptor for cross-tool access and DR. Accepts a path relative to ~/vault/ or "this" for current context. Use when a project brief, decision, or research note should be accessible from Claude Desktop.
---

Push a vault note to Perceptor so it's accessible from Claude Desktop and backed up to GitHub.

## Usage

The user will specify what to push in one of these ways:
- A path relative to ~/vault/ (e.g., `projects/ai-google-ads-loop`)
- "this" or "current" — push whatever vault content was discussed in this session
- A folder — push the README.md or main file in that folder

## Steps

1. **Resolve the target file**
   - If a folder path, look for README.md inside it
   - If "this"/"current", identify which vault files were referenced in this session
   - Read the file content

2. **Format for Perceptor**
   - Extract or infer: title, tags, project name, summary
   - If the file has frontmatter (YAML), use those fields
   - If not, infer from the content

3. **Call perceptor_save** with these parameters:
   - `title`: Use the markdown H1 title, prefixed with "vault:" (e.g., "vault: AI-Powered Google Ads Loop")
   - `tags`: From frontmatter tags, plus "vault-sync"
   - `projects`: From frontmatter or inferred from folder name
   - `summary`: From frontmatter or first paragraph after the title
   - `content`: The full file content
   - `source`: "cc"
   - `autoSync`: true

4. **Report result**
   - Show the Perceptor context ID created
   - Confirm it's now accessible from Claude Desktop

## Naming Convention

All vault-pushed contexts use the prefix `vault:` in the title to distinguish them from regular Perceptor contexts.

## Example

```
User: /vault-push projects/ai-google-ads-loop
→ Reads ~/vault/projects/ai-google-ads-loop/README.md
→ Calls perceptor_save with title "vault: AI-Powered Google Ads Loop"
→ Reports: "Pushed to Perceptor as vault-ai-powered-google-ads-loop-2026-03-15"
```
