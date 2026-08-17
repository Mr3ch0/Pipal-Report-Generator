# Password Analysis Report Generator

A Python script that transforms [Pipal](https://github.com/digininja/pipal) password analysis output into professional, print-ready HTML reports with compliance assessments.

## Features

- **One-command workflow** - Runs pipal and generates HTML report automatically
- **Two-column layout** - Optimized for 8.5" x 11" paper printing
- **Obfuscated passwords** - Passwords shown as asterisks for secure reporting
- **Compliance assessment** - Pass/fail status for NIST, PCI-DSS, HIPAA, and CIS standards
- **Color-coded severity** - Critical/High/Medium indicators for findings
- **Data validation** - Verifies calculation accuracy and warns of data coverage issues

## Requirements

- Python 3.6+ (no external dependencies)
- Ruby 1.9.x+ (for pipal.rb)
- Pipal password analyzer (in same directory)

## Installation

Place `generate_report.py` in the Pipal directory:

```
pipal/
├── generate_report.py    <-- Report generator
├── pipal.rb              <-- Main Pipal script
├── checkers_available/
├── checkers_enabled/
└── ...
```

## Usage

### One Command (Recommended)

```bash
python3 generate_report.py -p passwords.txt -t 10000 -o report.html
```

| Option | Description |
|--------|-------------|
| `-p, --passwords` | Raw password file (one password per line) |
| `-t, --total` | Total password hashes before cracking |
| `-o, --output` | Output HTML filename (default: password_report.html) |

### From Existing Pipal Output

```bash
python3 generate_report.py -i pipal_output.txt -t 10000 -o report.html
```

| Option | Description |
|--------|-------------|
| `-i, --input` | Existing pipal output file |
| `-t, --total` | Total password hashes before cracking |
| `-o, --output` | Output HTML filename |

### Interactive Mode

```bash
python3 generate_report.py
```

Prompts for all inputs interactively.

## Example

```bash
$ python3 generate_report.py -p cracked_passwords.txt -t 444018 -o audit_report.html
Running pipal on cracked_passwords.txt...
Parsing pipal output...
  Note: Using file line count (277,513) instead of pipal count (242,897)
Generating report...

Report generated: audit_report.html
  Total Hashes: 444,018 | Cracked: 277,513 (62.50%)
```

## Report Sections

| Section | Description |
|---------|-------------|
| **Summary Box** | Total hashes, cracked count, unique passwords, crack percentage |
| **Top 10 Passwords** | Most common passwords (obfuscated with asterisks) |
| **Top 10 Base Words** | Common root words used in passwords |
| **Key Findings** | Critical issues with severity ratings |
| **Password Length** | Distribution with visual bar chart |
| **Character Analysis** | Character set composition breakdown |
| **Pattern Analysis** | Common patterns and trailing digit sequences |
| **Compliance Assessment** | Per-framework % Compliant (green) + % fail (red) for NIST, PCI, HIPAA, CIS |
| **Recommendations** | Actionable security improvements |

## Compliance Assessment

The report evaluates passwords against major security standards. Citations verified
against primary sources (NIST CSRC, PCI SSC, HHS OCR, CIS); most recently re-verified August 2026.

| Framework | Citation | Threshold | Notes |
|-----------|----------|-----------|-------|
| **NIST SP 800-63B** | Rev 4 §3.1.1.2 (Aug 2025) | 15 chars (single-factor) | SP 800-63B-4 (Aug 1, 2025). 15-char minimum is normative SHALL, not a recommendation. 8-char floor applies ONLY to passwords used inside an MFA bundle. |
| **PCI DSS** | v4.0.1 Req 8.3.6 | 12 chars | v4.0.1 (June 2024) is current. 12-char minimum became mandatory 2025-03-31. 8-char legacy fallback permitted only if the system physically cannot support 12. |
| **HIPAA** | 45 CFR 164.308(a)(5)(ii)(D) | No explicit length | Password Management is Addressable; the rule has no numeric standard. HHS OCR guidance recommends NIST 800-63B alignment. NPRM (90 FR 898, Jan 2025) proposing stricter controls is pending finalization. Generator scores HIPAA against the same 15-char threshold as NIST. |
| **CIS Controls** | v8.1 Safeguard 5.2 | 14 chars non-MFA / 8 chars MFA | v8.1 (June 2024) is current. Generator scores against 14-char non-MFA value. |
| **Composition Rules** | NIST 800-63B-4 §3.1.1.2 | Prohibited | Rev 4 strengthens "SHOULD NOT" to "SHALL NOT impose other composition rules." Generator reports the legacy alpha+num+special compliance percentage but frames it as legacy enforcement, not a positive control. |
| **Blank / Empty** | AD `ADS_UF_PASSWD_NOTREQD` (0x20 / 32) | Must be 0 | userAccountControl bit permitting empty passwords. High-risk misconfiguration on normal user accounts. |

### Display and Pass/Fail Logic

- Each row shows **`N% Compliant`** (green) and **`M% fail`** (red); the two always sum to 100.
- **PASS** only at 100% compliant; otherwise **FAIL**, shown as the fail percentage.
- Compliant % uses `floor()` for strict compliance (99.5% displays as 99%, never rounded up to 100%); fail % is the exact complement (`100 - floored compliant`).
- Requirement text is plain English on the client face, no "SHALL"/"SHALL NOT" ("Minimum 15 characters required (single-factor logins)", "Complexity and composition rules not permitted").
- The Composition Rules figure is an inverted proxy indicator and renders red (a high legacy-enforced % is the negative outcome, not a positive control).

### Calculation Method

```
Compliance % = floor((passwords >= N chars) / total_cracked * 100)
```

- NIST and HIPAA both scored against >= 15-char threshold (HIPAA defers via OCR guidance)
- PCI DSS scored against >= 12-char threshold
- CIS Controls scored against >= 14-char threshold (non-MFA accounts)
- All compliance percentages calculated from complete password length distribution
- No truncation - captures ALL password lengths from pipal output
- Data coverage validation ensures all passwords are accounted for

## Crack Percentage Calculation

When using the `-p` flag with a raw password file:

- **Cracked count** = Total lines in file (including blank lines)
- **Crack percentage** = Cracked count / Total hashes * 100

This ensures the crack percentage matches actual cracking tool output (hashcat, john the ripper), where blank lines may represent empty passwords or hash entries.

## Blank/Empty Password Detection

The report automatically detects and reports blank lines in the password file:

- **Blank/Empty row** - Displays count and percentage of blank passwords (highlighted in red)
- **Data coverage note** - Explains that compliance percentages are based on analyzable (non-blank) passwords

Example output:
```
Blank/Empty        Empty passwords    34,616 (12.5%)
Note: Compliance % based on 242,897 analyzable passwords (87.5% of total)
```

Console output when blank passwords are detected:
```
  Note: Using file line count (277,513) instead of pipal count (242,897)
  Blank/empty passwords detected: 34,616
```

**Why this matters:**
- Crack percentage reflects total cracking tool output (including blanks)
- Compliance percentages are calculated only from passwords pipal can analyze
- Blank passwords represent a critical security finding (accounts with no password)

## Obfuscation

All sensitive data is obfuscated in the report:

| Original | Obfuscated |
|----------|------------|
| `Password1$` | `**********` |
| `Temp1234` | `********` |
| `summer` | `******` |

The asterisk count matches the original password length, providing insight into password length patterns without exposing actual credentials.

## Severity Color Coding

| Color | Severity | Example |
|-------|----------|---------|
| Red | Critical | >50% cracked, 8 or fewer characters |
| Orange | High | 25-50% cracked, predictable patterns |
| Yellow | Medium | <25% cracked, 15 or fewer characters |

## Workflow Example

### Step 1: Extract Password Hashes
```bash
# Example: Extract NTLM hashes from secretsdump output
grep -E ':[a-f0-9]{32}:' secretsdump.txt > hashes.txt
wc -l hashes.txt  # Note total count for -t flag
```

### Step 2: Crack Passwords
```bash
hashcat -m 1000 hashes.txt wordlist.txt -o cracked.txt
```

### Step 3: Generate Report (One Command)
```bash
python3 generate_report.py -p cracked.txt -t 10000 -o password_report.html
```

### Step 4: Include in Deliverables
Open `password_report.html` in a browser and:
- Print to PDF for inclusion in deliverables
- Screenshot for embedding in Word/PowerPoint
- Copy tables directly into report documents

## Sample Output

```
Compliance Assessment
---------------------
Framework         Citation                       Requirement                                             Compliance
NIST SP 800-63B   Rev 4 §3.1.1.2 (Aug 2025)      Minimum 15 characters required (single-factor logins)    7% Compliant   93% fail
PCI DSS           v4.0.1 Req 8.3.6               Min 12 chars                                            35% Compliant   65% fail
HIPAA             45 CFR 164.308(a)(5)(ii)(D)    No explicit length; OCR -> NIST 800-63B                  7% Compliant   93% fail (per NIST)
CIS Controls      v8.1 Safeguard 5.2             Min 14 chars non-MFA / 8 chars MFA                      12% Compliant   88% fail
Composition Rules NIST 800-63B-4 §3.1.1.2        Complexity and composition rules not permitted          51% legacy enforced
Blank / Empty     AD UF_PASSWD_NOTREQD flag      Accounts with empty NT hash                              0.1% of cracked
```

## Troubleshooting

### RTF Parsing Issues
If RTF files aren't parsing correctly, convert to plain text first:
```bash
textutil -convert txt pipal_output.rtf
```

### Ruby Version Errors
Pipal requires Ruby 1.9+:
```bash
ruby --version
```

### Data Coverage Warning
If the report shows a data coverage warning, it means the sum of password lengths doesn't match the total cracked count. This could indicate parsing issues with unusual characters in the password file.

## Version History

### v1.2.0 (May 2026)

**Framework Citation Audit (verified May 2026):**

1. **NIST SP 800-63B threshold raised to 15 chars** - SP 800-63B-4 (Aug 1, 2025) made 15 characters a normative SHALL for single-factor passwords. Generator now scores NIST and HIPAA against the 15-char floor, not 8.

2. **Compliance table refactored to 4 columns** - Framework / Citation / Requirement / Status, rendered as a standalone full-width section after the 2-column body. Citations now reference the exact section/requirement (Rev 4 §3.1.1.2, Req 8.3.6, 45 CFR 164.308(a)(5)(ii)(D), Safeguard 5.2).

3. **HIPAA framing corrected** - Removed "Defers to NIST 800-63B" wording. HIPAA Security Rule has no explicit length requirement; HHS OCR guidance recommends NIST 800-63B alignment. NPRM (90 FR 898, Jan 6, 2025) noted as pending finalization.

4. **CIS Controls value pair surfaced** - Now shows "14 chars non-MFA / 8 chars MFA" per v8.1 Safeguard 5.2.

5. **Composition rules reframed** - Moved from "% compliant" to legacy-enforced framing, citing the SHALL NOT in NIST 800-63B-4 §3.1.1.2.

6. **Recommendations updated** - Refer to specific NIST 800-63B-4 sections and call out UF_PASSWD_NOTREQD audit.

7. **CSS tightened** - Body 10pt, headers/tables compacted, @page margin 0.3in. Targets single-letter-page rendering.

### v1.1.0 (December 2025)

**Accuracy Fixes:**

1. **Removed 15-entry truncation limit** - Now captures ALL password lengths from pipal output, fixing data loss for datasets with many distinct lengths.

2. **Fixed NIST/HIPAA calculation** - Correctly calculates passwords >= 8 characters. Pipal's "More than eight characters" means >8 (9+ chars), not >=8, so we sum from the complete length distribution.

3. **Added data completeness validation** - Verifies sum of password lengths equals total cracked. Displays warning if data coverage is below 100%.

4. **Strict compliance percentages** - Changed from `round()` to `floor()`. Ensures 99.5% displays as 99% (FAIL), not rounded to 100% (PASS).

5. **Fixed cracked count** - When using `-p` flag, cracked count is based on total file lines (including blank lines), matching actual cracking tool output.

6. **Blank password detection** - Reports blank/empty passwords as a separate line item in Compliance Assessment, with count and percentage highlighted as critical finding.

### v1.0.0 (December 2024)

- Initial release
- Basic HTML report generation from pipal output
- Compliance assessment for NIST, PCI, HIPAA, CIS
- Obfuscated password display
- Two-column layout for printing

## Credits

- **Pipal**: Robin Wood (robin@digi.ninja) - https://github.com/digininja/pipal
- **Report Generator**: Scott Sailors (Mr3ch0) - https://github.com/Mr3ch0

## License

This report generator is provided as-is for security assessment purposes. Use responsibly and only on systems you have authorization to test.

## Related

- [Pipal](https://github.com/digininja/pipal) - Password Analyzer by Robin Wood
- [NIST SP 800-63B-4 (Aug 2025)](https://pages.nist.gov/800-63-4/sp800-63b.html) - Digital Identity Guidelines, current revision
- [PCI DSS v4.0.1](https://www.pcisecuritystandards.org/) - Payment Card Industry Data Security Standard
- [CIS Controls v8.1](https://www.cisecurity.org/controls/) - Center for Internet Security
- [HIPAA Security Rule (45 CFR Part 164)](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164) - eCFR
- [HIPAA Security Rule NPRM (90 FR 898)](https://www.federalregister.gov/documents/2025/01/06/2024-30983/) - Pending
