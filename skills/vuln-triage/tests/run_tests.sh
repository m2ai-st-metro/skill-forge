#!/usr/bin/env bash
# run_tests.sh: executable test contract for the /vuln-triage skill.
# Each assert cites its spec-claim id (C-NN) from the build's spec-claims.md.
# Plain bash + coreutils. Exit 0 only if every assert passes.

set -u
LC_ALL=C
export LC_ALL

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCAN="$SKILL_DIR/scripts/scan_candidates.sh"
PLANTED="$SKILL_DIR/tests/fixtures/planted"
CLEAN="$SKILL_DIR/tests/fixtures/clean"
GREPPY="$HOME/projects/research/greppy"

PASS=0
FAIL=0

ok()   { PASS=$((PASS+1)); echo "PASS $1"; }
bad()  { FAIL=$((FAIL+1)); echo "FAIL $1"; }
check() { # check <label> <condition-exit-status>
  if [[ "$2" -eq 0 ]]; then ok "$1"; else bad "$1"; fi
}

WORK=$(mktemp -d "$HOME/.cache/vuln-triage-test.XXXXXX")
trap 'rm -rf "$WORK"' EXIT

# ---- T-01 (C-01, C-22): skill shape and frontmatter -------------------------
[[ -f "$SKILL_DIR/SKILL.md" && -f "$SCAN" ]]; check "T-01a skill files exist" $?
head -5 "$SKILL_DIR/SKILL.md" | grep -q '^name: vuln-triage'; check "T-01b frontmatter name" $?
head -5 "$SKILL_DIR/SKILL.md" | grep -q '^description: '; check "T-01c frontmatter description" $?
HELPER_COUNT=$(find "$SKILL_DIR/scripts" -type f | wc -l)
[[ "$HELPER_COUNT" -eq 1 ]]; check "T-01d exactly one helper script" $?

# ---- planted scan used by several tests -------------------------------------
PLANTED_OUT=$("$SCAN" "$PLANTED" 2>/dev/null); PLANTED_RC=$?
[[ $PLANTED_RC -eq 0 ]]; check "T-02a planted scan exits 0" $?

# ---- T-02 (C-07, C-27): the 3 planted findings must flag --------------------
echo "$PLANTED_OUT" | grep -q $'^CMD_INJECTION\t.*vulnerable_sample\.py.*os\.system'; check "T-02b planted command injection flagged" $?
echo "$PLANTED_OUT" | grep -q $'^HARDCODED_SECRET\t.*vulnerable_sample\.py.*FAKEKEY_'; check "T-02c planted fake key flagged" $?
echo "$PLANTED_OUT" | grep -q $'^PATH_TRAVERSAL\t.*vulnerable_sample\.py.*os\.path\.join'; check "T-02d planted unsafe path join flagged" $?
N_CLASSES_ONE_FILE=$(echo "$PLANTED_OUT" | grep 'vulnerable_sample\.py' | cut -f1 | sort -u | wc -l)
[[ "$N_CLASSES_ONE_FILE" -ge 3 ]]; check "T-02e multiple classes coexist in one file (C-27)" $?

# ---- T-03 (C-08, C-23, C-24, C-25): clean file zero flags -------------------
CLEAN_OUT=$("$SCAN" "$CLEAN" 2>/dev/null); CLEAN_RC=$?
[[ $CLEAN_RC -eq 0 ]]; check "T-03a clean scan exits 0" $?
CLEAN_HITS=$(echo "$CLEAN_OUT" | grep -c 'clean_sample\.py' || true)
[[ "$CLEAN_HITS" -eq 0 ]]; check "T-03b clean file has zero candidates" $?
echo "$CLEAN_OUT" | grep -q '^SCAN_COMPLETE candidates=0$'; check "T-03c clean scan reports candidates=0" $?

# ---- T-04 (C-09): refusal outside workspace ---------------------------------
"$SCAN" /tmp >/dev/null 2>"$WORK/refuse1.err"; RC=$?
[[ $RC -eq 3 ]] && grep -q '^REFUSED' "$WORK/refuse1.err"; check "T-04 outside path refused (exit 3 + REFUSED)" $?

# ---- T-05 (C-15): symlink and dot-dot escapes refused -----------------------
ln -s /tmp "$WORK/escape-link"
"$SCAN" "$WORK/escape-link" >/dev/null 2>"$WORK/refuse2.err"; RC=$?
[[ $RC -eq 3 ]] && grep -q '^REFUSED' "$WORK/refuse2.err"; check "T-05a symlink escape refused" $?
"$SCAN" "$HOME/../../tmp" >/dev/null 2>"$WORK/refuse3.err"; RC=$?
[[ $RC -eq 3 ]] && grep -q '^REFUSED' "$WORK/refuse3.err"; check "T-05b ../ escape refused" $?

# ---- T-06 (C-13): nonexistent target is a clear hard error ------------------
"$SCAN" "$HOME/no-such-dir-vt-$$" >/dev/null 2>"$WORK/missing.err"; RC=$?
[[ $RC -eq 2 ]] && grep -q 'does not exist' "$WORK/missing.err"; check "T-06 missing target errors (exit 2)" $?

# ---- T-07 (C-05, C-06): greppy live scan under 30s --------------------------
if [[ -d "$GREPPY" ]]; then
  GREPPY_OUT=$(timeout 30 "$SCAN" "$GREPPY" 2>/dev/null); RC=$?
  [[ $RC -eq 0 ]]; check "T-07a greppy scan exit 0 within 30s" $?
  echo "$GREPPY_OUT" | grep -q '^SCAN_COMPLETE candidates='; check "T-07b greppy scan completes with marker" $?
else
  bad "T-07 greppy repo missing at $GREPPY"
fi

# ---- T-08 (C-12): determinism -----------------------------------------------
"$SCAN" "$PLANTED" > "$WORK/run1.out" 2>/dev/null
"$SCAN" "$PLANTED" > "$WORK/run2.out" 2>/dev/null
cmp -s "$WORK/run1.out" "$WORK/run2.out"; check "T-08 byte-identical across runs" $?

# ---- T-09 (C-10, C-19): scan is read-only on the target ---------------------
BEFORE=$(find "$PLANTED" -type f -print0 | sort -z | xargs -0 md5sum)
BEFORE_LIST=$(find "$PLANTED" | sort)
"$SCAN" "$PLANTED" >/dev/null 2>&1
AFTER=$(find "$PLANTED" -type f -print0 | sort -z | xargs -0 md5sum)
AFTER_LIST=$(find "$PLANTED" | sort)
[[ "$BEFORE" == "$AFTER" ]]; check "T-09a target files unmodified by scan" $?
[[ "$BEFORE_LIST" == "$AFTER_LIST" ]]; check "T-09b scan creates/removes no files in target" $?

# ---- T-10 (C-14): empty dir is an explicit clean result ---------------------
mkdir -p "$WORK/empty"
EMPTY_OUT=$("$SCAN" "$WORK/empty" 2>/dev/null); RC=$?
[[ $RC -eq 0 ]] && echo "$EMPTY_OUT" | grep -q '^SCAN_COMPLETE candidates=0$'; check "T-10 empty dir: exit 0, candidates=0" $?

# ---- T-11 (C-20): no em-dashes ----------------------------------------------
EMD=$(grep -rlP '\x{2014}' "$SKILL_DIR/SKILL.md" "$SCAN" "$SKILL_DIR/tests/run_tests.sh" 2>/dev/null | wc -l)
[[ "$EMD" -eq 0 ]]; check "T-11 no U+2014 em-dashes in skill files" $?

# ---- T-12 (C-21): 14-day gate note ------------------------------------------
grep -q '2026-08-02' "$SKILL_DIR/SKILL.md" && grep -q 'Ravage' "$SKILL_DIR/SKILL.md"; check "T-12 gate note (2026-08-02, Ravage)" $?

# ---- T-13 (C-02, C-26): register-shift probes per class ---------------------
echo "$PLANTED_OUT" | grep -q $'^CMD_INJECTION\t.*register_shift\.js.*execSync'; check "T-13a JS template execSync flagged" $?
echo "$PLANTED_OUT" | grep -q $'^CMD_INJECTION\t.*register_shift\.sh.*eval'; check "T-13b bash eval \$var flagged" $?
echo "$PLANTED_OUT" | grep -q $'^CMD_INJECTION\t.*register_shift\.rs.*format!'; check "T-13c Rust format! arg flagged" $?
echo "$PLANTED_OUT" | grep -q $'^CMD_INJECTION\t.*register_shift\.py.*shell=True'; check "T-13d Python shell=True flagged" $?
echo "$PLANTED_OUT" | grep -q $'^SSRF\t.*register_shift\.js.*fetch'; check "T-13e interpolated fetch flagged as SSRF" $?
echo "$PLANTED_OUT" | grep -q $'^SSRF\t.*register_shift\.js.*fetch(req\.url)'; check "T-13h property-access SSRF arg flagged (round-1 FN fix)" $?
echo "$PLANTED_OUT" | grep -q $'^UNSAFE_DESERIALIZATION\t.*register_shift\.py.*yaml\.load'; check "T-13f yaml.load flagged" $?
echo "$PLANTED_OUT" | grep -q $'^UNSAFE_DESERIALIZATION\t.*register_shift\.py.*pickle\.loads'; check "T-13g pickle.loads flagged" $?

# ---- T-14 (C-16, C-28): path shapes -----------------------------------------
"$SCAN" "$PLANTED/" >/dev/null 2>&1; check "T-14a trailing slash accepted" $?
(cd "$HOME" && "$SCAN" ".claude/skills/vuln-triage/tests/fixtures/planted" >/dev/null 2>&1); check "T-14b relative path accepted" $?
"$SCAN" '~/.claude/skills/vuln-triage/tests/fixtures/planted' >/dev/null 2>&1; check "T-14c literal tilde path accepted" $?

# ---- T-15 (C-29): markdown docs never become candidates ---------------------
MD_HITS=$(echo "$PLANTED_OUT" | grep -c 'notes\.md' || true)
[[ "$MD_HITS" -eq 0 ]]; check "T-15 notes.md excluded from candidates" $?

# ---- T-16 (C-03, C-04, C-10, C-18): SKILL.md contract text ------------------
grep -q 'ONLY the flagged spans' "$SKILL_DIR/SKILL.md"; check "T-16a judge-only-flagged-spans stated" $?
grep -q 'vault/reports/vuln-triage/' "$SKILL_DIR/SKILL.md"; check "T-16b report path stated" $?
grep -qi 'never auto-fix' "$SKILL_DIR/SKILL.md"; check "T-16c never-auto-fix stated" $?
grep -qi 'not attacker simulation' "$SKILL_DIR/SKILL.md"; check "T-16d attacker-simulation out of scope" $?

# ---- T-17 (C-11): helper has no network/install commands --------------------
NET=$(grep -cE '\b(curl|wget|pip3? install|npm install|apt(-get)? install|nc |ssh )' "$SCAN" || true)
[[ "$NET" -eq 0 ]]; check "T-17 helper free of network/install commands" $?

# ---- T-21 (C-02): os.system string-concat injection flagged (round-2 FN) ----
echo "$PLANTED_OUT" | grep -q $'^CMD_INJECTION\t.*register_shift\.py.*os\.system("ls " '; check "T-21 os.system concat flagged" $?

# ---- T-22 (C-02): JS and Python eval on untrusted input flagged (round-2 FN)-
echo "$PLANTED_OUT" | grep -q $'^CMD_INJECTION\t.*register_shift\.js.*eval(userExpr)'; check "T-22a JS eval flagged" $?
echo "$PLANTED_OUT" | grep -q $'^CMD_INJECTION\t.*register_shift\.py.*eval(expr)'; check "T-22b Python eval flagged" $?

# ---- T-23 (C-27): dangerous call embedded mid-line flagged ------------------
echo "$PLANTED_OUT" | grep -q $'^CMD_INJECTION\t.*register_shift\.js.*execSync(`echo'; check "T-23 embedded mid-line execSync flagged" $?

# ---- T-24 (C-27): clean.js safe eval-lookalikes not flagged -----------------
# guard against eval regex over-matching words like retrieval/medieval
echo "retrieval(x)" > "$WORK/eb.py"; echo "medieval_ok(y)" >> "$WORK/eb.py"
mkdir -p "$WORK/inroot"; cp "$WORK/eb.py" "$WORK/inroot/"
EB_OUT=$(VT_WORKSPACE_ROOT="$WORK" "$SCAN" "$WORK/inroot" 2>/dev/null)
[[ $(echo "$EB_OUT" | grep -c 'eb\.py') -eq 0 ]]; check "T-24 eval word-boundary: retrieval/medieval not flagged" $?

# ---- T-18 (C-08, C-24): safe-variant clean.js has zero candidates -----------
CLEANJS_OUT=$("$SCAN" "$CLEAN" 2>/dev/null)
CJS_HITS=$(echo "$CLEANJS_OUT" | grep -c 'clean_sample\.js' || true)
[[ "$CJS_HITS" -eq 0 ]]; check "T-18 execFile array + constant fetch not flagged" $?

# ---- T-19 (C-09, C-15): sibling prefix does NOT over-match -------------------
# Uses the VT_WORKSPACE_ROOT test seam: a sibling dir sharing a name prefix
# with the root must be refused, while the root itself is accepted.
mkdir -p "$WORK/root/pkg" "$WORK/root-evil"
: > "$WORK/root/pkg/x.py"
: > "$WORK/root-evil/y.py"
VT_WORKSPACE_ROOT="$WORK/root" "$SCAN" "$WORK/root" >/dev/null 2>&1; RC_IN=$?
VT_WORKSPACE_ROOT="$WORK/root" "$SCAN" "$WORK/root-evil" >/dev/null 2>"$WORK/sibling.err"; RC_OUT=$?
[[ $RC_IN -eq 0 ]]; check "T-19a workspace root itself accepted" $?
[[ $RC_OUT -eq 3 ]] && grep -q '^REFUSED' "$WORK/sibling.err"; check "T-19b sibling prefix dir refused (no over-match)" $?

# ---- T-20 (C-12): TRUNCATED marker fires deterministically over the cap ------
mkdir -p "$WORK/root/many"
python3 - "$WORK/root/many/big.py" <<'PY'
import sys
with open(sys.argv[1], "w") as f:
    for i in range(300):
        f.write('os.system(f"do {x%d}")\n' % i)
PY
TRUNC_OUT=$(VT_WORKSPACE_ROOT="$WORK/root" "$SCAN" "$WORK/root/many" 2>/dev/null)
echo "$TRUNC_OUT" | grep -q $'^CMD_INJECTION\tTRUNCATED'; check "T-20a over-cap class emits TRUNCATED marker" $?
TRUNC_OUT2=$(VT_WORKSPACE_ROOT="$WORK/root" "$SCAN" "$WORK/root/many" 2>/dev/null)
[[ "$TRUNC_OUT" == "$TRUNC_OUT2" ]]; check "T-20b truncated output is deterministic" $?

# ---- T-25 (MAI-136): SCAN_INCLUDE_MD=1 folds notes.md into the scan --------
# notes.md is the known-bad fixture: default mode proves exclusion (T-15),
# include-md mode proves the same file is caught end-to-end across all six
# classes once markdown is opted in (SKILL.md-as-payload, not prose).
MD_OUT=$(SCAN_INCLUDE_MD=1 "$SCAN" "$PLANTED" 2>/dev/null); MD_RC=$?
[[ $MD_RC -eq 0 ]]; check "T-25a include-md scan exits 0" $?
echo "$MD_OUT" | grep -q $'^CMD_INJECTION\t.*notes\.md.*os\.system'; check "T-25b notes.md os.system flagged with SCAN_INCLUDE_MD=1" $?
echo "$MD_OUT" | grep -q $'^HARDCODED_SECRET\t.*notes\.md.*FAKEKEY_'; check "T-25c notes.md hardcoded secret flagged with SCAN_INCLUDE_MD=1" $?
echo "$MD_OUT" | grep -q $'^UNSAFE_DESERIALIZATION\t.*notes\.md.*yaml\.load'; check "T-25d notes.md yaml.load flagged with SCAN_INCLUDE_MD=1" $?
echo "$MD_OUT" | grep -q $'^PROMPT_INJECTION\t.*notes\.md.*[Ii]gnore all previous instructions'; check "T-25e notes.md prompt-injection marker flagged with SCAN_INCLUDE_MD=1" $?

# ---- T-26 (MAI-136): SCAN_INCLUDE_MD=0 (explicit off) matches default ------
MD_OFF_OUT=$(SCAN_INCLUDE_MD=0 "$SCAN" "$PLANTED" 2>/dev/null)
[[ $(echo "$MD_OFF_OUT" | grep -c 'notes\.md' || true) -eq 0 ]]; check "T-26 SCAN_INCLUDE_MD=0 excludes notes.md same as unset" $?

# ---- T-27 (MAI-136): include-md mode is still deterministic ----------------
"$SCAN" "$PLANTED" >/dev/null 2>&1  # unrelated call to keep TMP_LIST fixture untouched
SCAN_INCLUDE_MD=1 "$SCAN" "$PLANTED" > "$WORK/mdrun1.out" 2>/dev/null
SCAN_INCLUDE_MD=1 "$SCAN" "$PLANTED" > "$WORK/mdrun2.out" 2>/dev/null
cmp -s "$WORK/mdrun1.out" "$WORK/mdrun2.out"; check "T-27 include-md output byte-identical across runs" $?

# ---- T-28 (MAI-136): PROMPT_INJECTION never fires in default mode ---------
DEFAULT_OUT=$("$SCAN" "$PLANTED" 2>/dev/null)
echo "$DEFAULT_OUT" | grep -q '^PROMPT_INJECTION'
[[ $? -ne 0 ]]; check "T-28 PROMPT_INJECTION absent by default" $?

# ---- T-29 (MAI-136): SKILL.md documents the opt-in flag --------------------
grep -q 'SCAN_INCLUDE_MD' "$SKILL_DIR/SKILL.md"; check "T-29 SKILL.md documents SCAN_INCLUDE_MD" $?

echo
echo "RESULT: $PASS passed, $FAIL failed"
[[ $FAIL -eq 0 ]]
