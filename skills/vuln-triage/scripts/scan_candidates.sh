#!/usr/bin/env bash
# scan_candidates.sh: deterministic candidate scanner for the /vuln-triage skill.
# Pass 1 of the grep+judge two-pass. Read-only on the target. No network. No new deps
# (bash, coreutils, grep, find only).
#
# Usage: scan_candidates.sh <repo-path>
# Stdout: one candidate per line as  CLASS<TAB>file:line:matched-text
#         terminated by             SCAN_COMPLETE candidates=<N>
# Exit:   0 scan completed (even with zero candidates)
#         2 bad target (missing, not a directory, bad usage)
#         3 REFUSED (resolved path is outside this workspace)
#
# Defensive-only guarantee: the resolved real path must live under the workspace
# root. Symlinks and ../ tricks are resolved BEFORE the ownership check, so an
# in-workspace path that points outside is refused the same as a direct outside path.
#
# Markdown-aware mode (opt-in, off by default): SCAN_INCLUDE_MD=1 <this script> <repo-path>
# Default behavior excludes *.md/*.markdown, treating them as prose (unchanged, see T-15).
# That assumption is wrong for skill-forge: SKILL.md IS the payload, carrying instructions
# and inline shell/python snippets an agent will run (MAI-136). SCAN_INCLUDE_MD=1 folds
# *.md/*.markdown into the same five-class scan (the patterns are code-shaped, so they match
# fenced/inline code wherever it sits in the file and essentially never match plain prose)
# and adds a sixth, markdown-only PROMPT_INJECTION class for instruction-override language.

set -u
LC_ALL=C
export LC_ALL

# Workspace root the scan is confined to. Overridable only for tests via
# VT_WORKSPACE_ROOT; defaults to the real workspace. Normalized so the prefix
# comparison is against a canonical, slash-free-tail path.
WORKSPACE_ROOT=$(realpath -m -- "${VT_WORKSPACE_ROOT:-/home/apexaipc}")
PER_CLASS_CAP=200
INCLUDE_MD="${SCAN_INCLUDE_MD:-0}"

if [[ $# -ne 1 ]]; then
  echo "ERROR: usage: scan_candidates.sh <repo-path>" >&2
  exit 2
fi

RAW="$1"
# Expand a literal leading tilde (callers often pass it quoted).
case "$RAW" in
  "~") RAW="$HOME" ;;
  "~/"*) RAW="$HOME/${RAW#\~/}" ;;
esac

if ! TARGET=$(realpath -e -- "$RAW" 2>/dev/null); then
  echo "ERROR: target path does not exist: $RAW" >&2
  exit 2
fi
if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: target is not a directory: $TARGET" >&2
  exit 2
fi
case "$TARGET" in
  "$WORKSPACE_ROOT" | "$WORKSPACE_ROOT"/*) ;;
  *)
    echo "REFUSED: target outside workspace ($TARGET). Defensive-only: this skill scans repos owned by this workspace." >&2
    exit 3
    ;;
esac

TMP_LIST=$(mktemp)
TMP_LIST_MD=$(mktemp)
TMP_HITS=$(mktemp)
trap 'rm -f "$TMP_LIST" "$TMP_LIST_MD" "$TMP_HITS"' EXIT

# Source file inventory: prune build/vendor dirs, skip big files, skip docs and
# generated noise. Sorted for byte-identical output across runs.
find "$TARGET" \
  \( -name .git -o -name target -o -name node_modules -o -name dist -o -name build \
     -o -name .venv -o -name venv -o -name __pycache__ -o -name vendor \) -prune \
  -o -type f -size -1048576c \
  ! -name '*.md' ! -name '*.markdown' ! -name '*.rst' ! -name '*.txt' \
  ! -name '*.lock' ! -name '*.min.js' ! -name '*.svg' ! -name '*.map' \
  -print0 | LC_ALL=C sort -z > "$TMP_LIST"

# Markdown inventory, populated only in SCAN_INCLUDE_MD=1 mode. Kept separate
# from TMP_LIST so PROMPT_INJECTION (markdown-only) can scan just these files,
# then merged into TMP_LIST so the five code-pattern classes see them too.
if [[ "$INCLUDE_MD" == "1" ]]; then
  find "$TARGET" \
    \( -name .git -o -name target -o -name node_modules -o -name dist -o -name build \
       -o -name .venv -o -name venv -o -name __pycache__ -o -name vendor \) -prune \
    -o -type f -size -1048576c \( -name '*.md' -o -name '*.markdown' \) \
    -print0 | LC_ALL=C sort -z > "$TMP_LIST_MD"
  if [[ -s "$TMP_LIST_MD" ]]; then
    cat "$TMP_LIST_MD" >> "$TMP_LIST"
    LC_ALL=C sort -z -o "$TMP_LIST" "$TMP_LIST"
  fi
fi

# scan_class CLASS PATTERN [POST_FILTER] [ci] [LISTFILE]
# Greps the inventory (LISTFILE, default TMP_LIST) for PATTERN, optionally
# removes POST_FILTER lines, sorts, caps at PER_CLASS_CAP with a deterministic
# TRUNCATED marker.
scan_class() {
  local class="$1" pattern="$2" filter="${3:-}" ciflag="${4:-}" listfile="${5:-$TMP_LIST}"
  local -a gopts=(-nHE -I)
  [[ "$ciflag" == "ci" ]] && gopts+=(-i)
  [[ -s "$listfile" ]] || return 0
  local out
  out=$(xargs -a "$listfile" -0 grep "${gopts[@]}" -e "$pattern" -- 2>/dev/null || true)
  if [[ -n "$filter" && -n "$out" ]]; then
    out=$(printf '%s\n' "$out" | grep -vE "$filter" || true)
  fi
  out=$(printf '%s\n' "$out" | sed '/^$/d' | sort)
  [[ -n "$out" ]] || return 0
  local n
  n=$(printf '%s\n' "$out" | wc -l)
  printf '%s\n' "$out" | head -n "$PER_CLASS_CAP" | sed "s/^/${class}\t/" >> "$TMP_HITS"
  if (( n > PER_CLASS_CAP )); then
    printf '%s\tTRUNCATED (%s candidates, showing %s)\n' "$class" "$n" "$PER_CLASS_CAP" >> "$TMP_HITS"
  fi
  return 0
}

# CMD_INJECTION: interpolated or shell-evaluated command construction.
# Deliberately does NOT match list-argv subprocess.run([...]) or literal-only calls.
P_CMD="exec(Sync)?[[:space:]]*\([[:space:]]*\`[^\`]*\\\$\{"
P_CMD+="|exec(Sync)?[[:space:]]*\([[:space:]]*[\"'][^\"']*[\"'][[:space:]]*\+"
P_CMD+="|os\.(system|popen)[[:space:]]*\([[:space:]]*(f[\"']|[A-Za-z_])"
P_CMD+="|os\.(system|popen)[[:space:]]*\([[:space:]]*[\"'][^\"']*[\"'][[:space:]]*\+"
P_CMD+="|subprocess\.(run|call|Popen|check_output|check_call)\([^)]*shell[[:space:]]*=[[:space:]]*True"
P_CMD+="|(^|[^A-Za-z0-9_.])eval[[:space:]]+\"?\\\$"
P_CMD+="|(^|[^A-Za-z0-9_.])eval[[:space:]]*\([[:space:]]*(\`|f[\"']|[A-Za-z_]|[\"'][^\"']*[\"'][[:space:]]*\+)"
P_CMD+="|Command::new\([[:space:]]*format!"
P_CMD+="|\.arg\([[:space:]]*format!"

# PATH_TRAVERSAL: path construction fed by request/user-shaped identifiers.
P_PATH="(os\.path\.join|path\.join)\([^)]*(request|req\.|params|query|body|argv|input\(|user)"
P_PATH+="|(open|readFile|readFileSync|sendFile|createReadStream)\([^)]*(\+[[:space:]]*[A-Za-z_]|req\.|params\[|query\[|argv\[|user_)"
P_PATH+="|open\([[:space:]]*f[\"'][^\"']*\{"

# HARDCODED_SECRET: quoted 16+ char literal assigned to a secret-shaped name.
# Post-filter drops env lookups and obvious placeholders. Case-insensitive.
P_SECRET="(api[_-]?key|apikey|secret|token|passwd|password|private[_-]?key)[\"']?[[:space:]]*[:=][[:space:]]*[\"'][A-Za-z0-9+/_-]{16,}[\"']"
F_SECRET="environ|process\.env|getenv|changeme|placeholder|YOUR_|xxxx"

# SSRF: outbound request whose URL is interpolated, concatenated, or a bare
# variable. Constant string URLs deliberately do not match.
# A bare-variable or property-access argument (req.url, args[0], cfg.host) counts
# as untrusted; a quoted constant URL does not.
P_SSRF="(fetch|axios(\.get|\.post)?|urlopen|https?\.get)[[:space:]]*\([[:space:]]*(\`|f[\"']|[A-Za-z_][A-Za-z0-9_.]*(\[[^]]*\])?[[:space:]]*[,)]|[\"'][^\"']*[\"'][[:space:]]*\+)"
P_SSRF+="|requests\.(get|post|put|delete)[[:space:]]*\([[:space:]]*(f[\"']|[A-Za-z_][A-Za-z0-9_.]*(\[[^]]*\])?[[:space:]]*[,)]|[\"'][^\"']*[\"'][[:space:]]*\+)"
P_SSRF+="|(cu[r]l|wg[e]t)[[:space:]][^|;]*\\\$"

# UNSAFE_DESERIALIZATION: yaml.load without a safe loader, pickle, marshal.
# yaml.safe_load never matches; Loader=SafeLoader lines are post-filtered.
P_DESER="yaml\.load[[:space:]]*\(|YAML\.load[^_]|pickle\.loads?[[:space:]]*\(|marshal\.loads?[[:space:]]*\("
F_DESER="SafeLoader|safe_load"

# PROMPT_INJECTION: markdown-only class, SCAN_INCLUDE_MD=1 mode only. Catches
# instruction-override language a malicious SKILL.md could carry for an agent
# to follow verbatim (natural-language, so scoped to *.md/*.markdown rather
# than run against code, where these phrases would just be noise).
P_PROMPT_INJ="ignore[[:space:]]+(all|any)?[[:space:]]*(previous|prior|the[[:space:]]+above)[[:space:]]+instructions"
P_PROMPT_INJ+="|disregard[[:space:]]+(all|any|your|the)?[[:space:]]*(previous|prior|system)?[[:space:]]*instructions"
P_PROMPT_INJ+="|(reveal|print|show)[[:space:]]+(your|the)[[:space:]]+(system[[:space:]]+prompt|instructions)"
P_PROMPT_INJ+="|you[[:space:]]+are[[:space:]]+now[[:space:]]+(DAN|in[[:space:]]+developer[[:space:]]+mode|unrestricted)"
P_PROMPT_INJ+="|do[[:space:]]+anything[[:space:]]+now"
P_PROMPT_INJ+="|(bypass|override)[[:space:]]+(safety|your)[[:space:]]+(guardrails|restrictions|instructions)"
P_PROMPT_INJ+="|new[[:space:]]+system[[:space:]]+prompt[[:space:]]*:"

scan_class "CMD_INJECTION"          "$P_CMD"
scan_class "PATH_TRAVERSAL"         "$P_PATH"
scan_class "HARDCODED_SECRET"       "$P_SECRET" "$F_SECRET" ci
scan_class "SSRF"                   "$P_SSRF"
scan_class "UNSAFE_DESERIALIZATION" "$P_DESER"  "$F_DESER"
if [[ "$INCLUDE_MD" == "1" ]]; then
  scan_class "PROMPT_INJECTION" "$P_PROMPT_INJ" "" ci "$TMP_LIST_MD"
fi

N=0
if [[ -s "$TMP_HITS" ]]; then
  N=$(grep -cv $'\tTRUNCATED (' "$TMP_HITS" || true)
  cat "$TMP_HITS"
fi
echo "SCAN_COMPLETE candidates=${N}"
exit 0
