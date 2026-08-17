# Pipal, Password Analyser

Copyright(c) 2022, Robin Wood <robin@digi.ninja>

On most internal pen-tests I do, I generally manage to get a password dump from
the DC. To do some basic analysis on this I wrote Counter and since I originally
released it I've made quite a few mods to it to generate extra stats that are
useful when doing reports to management.

Recently a good friend, n00bz, asked on Twitter if anyone had a tool that he
could use to analyse some passwords he had. I pointed him to Counter and said if
he had any suggestions for additions to let me know. He did just that and over
the last month between us we have come up with a load of new features which we
both think will help anyone with a large dump of cracked passwords to analyse.
We also got some input from well known password analysts
[Matt Weir](http://reusablesec.blogspot.com/) and Martin Bos who I'd like to give
a big thanks to.

I have to point out before going on, all this tool does is to give you the stats
and the information to help you analyse the passwords. The real work is done by
you in interpreting the results, I give you the numbers, you tell the story.

Seeing as there have been so many changes to the underlying code I also decided
to change the name (see below) and do a full new release.

So, what does this new version do? The best way to describe it is to see some
examples so go to the [Pipal project page](http://digi.ninja/projects/pipal.php)
for a full walk through of a sample analysis.

## Quick Start

### One Command (Recommended)
```bash
python3 generate_report.py -p passwords.txt -t 10000 -o report.html
```

| Option | Description |
|--------|-------------|
| `-p` | Raw password file (one password per line) |
| `-t` | Total password hashes before cracking (used to calculate crack percentage) |
| `-o` | Output HTML filename |

This runs pipal automatically and generates the HTML report in one step.

**Example:**
```bash
$ python3 generate_report.py -p cracked_passwords.txt -t 444019 -o audit_report.html
Running pipal on cracked_passwords.txt...
Parsing pipal output...
Generating report...

Report generated: audit_report.html
  Total Hashes: 444,019 | Cracked: 242,897 (54.70%)
```

### Alternative: Two-Step Process
```bash
# Step 1: Run Pipal
ruby pipal.rb passwords.txt > pipal_output.txt

# Step 2: Generate report from pipal output
python3 generate_report.py -i pipal_output.txt -t 10000 -o report.html
```

### Interactive Mode
```bash
python3 generate_report.py
```
Prompts for all inputs interactively.

## Install / Usage

The app will only work with `Ruby 1.9.x` and newer, if you try to run it in any previous
versions you will get a warning and the app will close.

Pipal is completely self contained and requires no gems installing so should
work on any vanilla Ruby install.

Usage is fairly simple, `-?` will give you full instructions:

```ruby
$ ./pipal.rb -?
pipal 2.0 Robin Wood (robin@digi.ninja) (http://digi.ninja)

Usage: pipal [OPTION] ... FILENAME
        --help, -h: show help
        --top, -t X: show the top X results (default 10)
        --output, -o : output to file
        --external, -e : external file to compare words against
		--gkey <Google Maps API key>: to allow zip code lookups (optional)

        FILENAME: The file to count
```

When you run the app you'll get a nice progress bar which gives you a rough idea
of how long the app will take to run. If you want to stop it at any point
hitting Ctrl-c will stop the parsing and will dump out the stats generated so
far.

The progress bar is based on a line count from the file which it gets this using
the wc command. If it can't find wc it will make a guess at the number of lines
based on the file size and an average line length of 8 bytes so the progress bar
may not be fully accurate but should still give you an idea.

[The Google Maps API](https://developers.google.com/maps/) key is supposed to be
used by Google to only allow access to their API to registered users.
I assumed this was true and registered for a key
but in putting together this release I found that it will take any value and
still do the look up. This may be a bug at the Google end or deliberate and may
change any any time so I'd suggest grabbing a key just in case. To use it you
can either edit the script and put the key into the constant on line 35 or you
can pass it on the command line every time. If you are going to hope that you
don't need a valid key then just put X in as the value as without something
Pipal won't try to perform a look up.

## Enabling Checkers

Checkers are the scripts that do the actual work, to understand how these work, see the [README_modular.md](README_modular.md) file.

## HTML Report Generator

The `generate_report.py` script transforms Pipal's text output into a professional, print-ready HTML report suitable for management and compliance documentation.

### Features

- **One-command workflow** - runs pipal and generates HTML report automatically
- **Two-column layout** optimized for 8.5" x 11" paper
- **Automatic section distribution** based on content size for balanced columns
- **Obfuscated passwords** (shown as asterisks for security in reports)
- **Color-coded severity** indicators (Critical/High/Medium)
- **Compliance assessment** against major security standards

### Report Sections

| Section | Description |
|---------|-------------|
| **Summary Box** | Total hashes, cracked count, unique passwords, crack percentage |
| **Top 10 Passwords** | Most common passwords (obfuscated) |
| **Top 10 Base Words** | Common root words used in passwords |
| **Key Findings** | Critical issues with severity ratings |
| **Password Length** | Distribution with visual bar chart + compliance summary |
| **Character Analysis** | Character set composition breakdown |
| **Pattern Analysis** | Common patterns and trailing digit sequences |
| **Compliance Assessment** | Per-framework compliance: % Compliant (green) and % fail (red) for NIST, PCI, HIPAA, CIS |
| **Recommendations** | Actionable security improvements |

### Usage Options

**One Command (from raw passwords):**
```bash
python3 generate_report.py -p passwords.txt -t 10000 -o report.html
```

**From existing pipal output:**
```bash
python3 generate_report.py -i pipal_output.txt -t 10000 -o report.html
```

**Interactive Mode:**
```bash
python3 generate_report.py
```

**Command-Line Options:**
| Option | Long | Description |
|--------|------|-------------|
| `-p` | `--passwords` | Raw password file (runs pipal automatically) |
| `-i` | `--input` | Existing pipal output file |
| `-t` | `--total` | Total password hashes before cracking |
| `-o` | `--output` | Output HTML filename (default: password_report.html) |

### Compliance Assessment

The report evaluates password compliance against major security standards. Citations
verified against primary sources (NIST CSRC, PCI SSC, HHS OCR, CIS) as of May 2026.
See `README_report_generator.md` for the full citation table.

| Framework | Citation | Threshold |
|-----------|----------|-----------|
| **NIST SP 800-63B** | Rev 4 §3.1.1.2 (Aug 2025) | 15 chars (single-factor) |
| **PCI DSS** | v4.0.1 Req 8.3.6 | 12 chars |
| **HIPAA** | 45 CFR 164.308(a)(5)(ii)(D) | No explicit length; OCR -> NIST 800-63B |
| **CIS Controls** | v8.1 Safeguard 5.2 | 14 chars non-MFA / 8 chars MFA |
| **Composition Rules** | NIST 800-63B-4 §3.1.1.2 | Complexity and composition rules not permitted |

**Display and Pass/Fail Logic:**
- Each row shows two figures: **`N% Compliant`** (green, the share meeting the requirement) and **`M% fail`** (red, the share below it). The two always sum to 100.
- **PASS** only when 100% of cracked passwords meet the minimum length; otherwise **FAIL**, shown as the fail percentage.
- Compliant % uses `floor()` for strict compliance (99.5% displays as 99%, never rounded up to 100%); fail % is the exact complement (`100 - floored compliant`), so the two never disagree.
- Requirement wording is plain English, no RFC-2119 "SHALL"/"SHALL NOT" (e.g. "Minimum 15 characters required (single-factor logins)").
- The **Composition Rules** row is an inverted indicator (NIST prohibits composition rules), so a high "legacy enforced" % is a negative finding and is shown in red. It is a proxy (passwords containing mixed character types), not a hard pass/fail control.

**Calculation Method:**
- All compliance percentages are calculated from pipal's complete password length distribution
- Formula: `(count of passwords >= N chars) / total_cracked * 100`
- The tool captures ALL password lengths from pipal output (no truncation)
- The Password Length table shows the top 8 lengths by count plus an **"All other lengths"** row, so the displayed distribution always reconciles to 100% of the cracked total
- Data coverage validation ensures all passwords are accounted for in calculations

**Example Output:**
```
Framework         Citation                       Requirement                                             Compliance
NIST SP 800-63B   Rev 4 §3.1.1.2 (Aug 2025)      Minimum 15 characters required (single-factor logins)    7% Compliant   93% fail
PCI DSS           v4.0.1 Req 8.3.6               Min 12 chars                                            35% Compliant   65% fail
HIPAA             45 CFR 164.308(a)(5)(ii)(D)    No explicit length; OCR -> NIST 800-63B                  7% Compliant   93% fail (per NIST)
CIS Controls      v8.1 Safeguard 5.2             Min 14 chars non-MFA / 8 chars MFA                      12% Compliant   88% fail
Composition Rules NIST 800-63B-4 §3.1.1.2        Complexity and composition rules not permitted          51% legacy enforced
```
In the rendered HTML report, `N% Compliant` is green and `M% fail` is red (the Composition Rules "legacy enforced" figure is red as a negative indicator), on a white background.

**Data Coverage Warning:**
If the sum of password lengths doesn't equal the total cracked count (e.g., due to parsing issues), the report displays a warning showing the percentage of passwords analyzed.

### Requirements

- Python 3.x (3.6+ recommended)
- Ruby 1.9.x or newer (for pipal.rb)
- No external Python dependencies (uses only standard library)

### Sample Output

The generated HTML report includes:
- Executive summary with key metrics (total hashes, cracked, unique, crack rate)
- Visual distribution charts with bar graphs
- Color-coded compliance pass/fail indicators
- Prioritized security recommendations

## Version History

### Report Generator Updates (August 2026): Client-Facing Clarity Pass

Compliance section reworked for accuracy-on-the-face and readability. All five
citations re-verified against primary sources (NIST 800-63B-4, PCI SSC, CIS,
HHS/eCFR):

1. **Plain-language requirements** - Removed RFC-2119 "SHALL"/"SHALL NOT" jargon from the client face (e.g. "Minimum 15 characters required (single-factor logins)", "Complexity and composition rules not permitted").
2. **Dual compliance/fail display** - Each row now shows `N% Compliant` (green) and `M% fail` (red); the two always sum to 100. Fail % is the exact complement of the floored compliant %.
3. **Composition Rules colored red** - Inverted-polarity indicator (NIST prohibits composition rules), so a high "legacy enforced" % renders red as a negative finding.
4. **Length table reconciles to 100%** - Added an "All other lengths" row so the displayed distribution always accounts for every cracked password (top-8 lengths no longer silently sum to under 100%).
5. **Explicit white background** - `body` now sets a white background so the report renders correctly in dark-mode browsers and PDF exporters.
6. **Layout evened up** - Two-column sections fill the full width, aligning their right edge with the full-width Compliance table.

### Report Generator Updates (May 2026): Framework Citation Audit

All compliance citations verified against primary sources (NIST CSRC, PCI SSC,
HHS OCR/eCFR, CIS) on 2026-05-19. Key corrections:

1. **NIST SP 800-63B threshold raised to 15 chars** - SP 800-63B-4 (Aug 1, 2025) made 15 characters a normative SHALL for single-factor passwords. NIST and HIPAA rows now score against the 15-char floor, not 8.
2. **Compliance table refactored to 4 columns** - Framework / Citation / Requirement / Status, rendered as a standalone full-width section after the 2-column body. Citations reference the exact section/requirement.
3. **HIPAA framing corrected** - Removed "Defers to NIST 800-63B." HIPAA Security Rule has no explicit length requirement; HHS OCR guidance recommends NIST 800-63B alignment. NPRM (90 FR 898, Jan 2025) noted as pending finalization.
4. **CIS Controls value pair surfaced** - "14 chars non-MFA / 8 chars MFA" per v8.1 Safeguard 5.2.
5. **Composition rules reframed** - Cited the SHALL NOT in NIST 800-63B-4 §3.1.1.2.
6. **CSS tightened** - Body 10pt, headers/tables compacted, @page margin 0.3in. Targets single-letter-page rendering.

### Report Generator Updates (December 2025)

**Compliance Calculation Accuracy Fixes:**

1. **Removed 15-entry truncation limit** - Previously only stored the first 15 password lengths from pipal output, causing data loss for datasets with many distinct lengths. Now captures ALL password lengths.

2. **Fixed NIST/HIPAA percentage calculation** - Correctly calculates passwords >= 8 characters by summing from the complete length distribution. Note: Pipal's "More than eight characters" stat means strictly >8 (9+ chars), not >=8, so direct use of that stat would give incorrect NIST compliance numbers.

3. **Added data completeness validation** - Verifies that the sum of password length counts equals the total cracked count. Displays a warning if data coverage is below 100%.

4. **Strict compliance percentages** - Changed from `round()` to `floor()` for compliance calculations. This ensures 99.5% displays as 99% (FAIL), not rounded to 100% (PASS).

5. **Fixed cracked count calculation** - When using `-p` flag with a raw password file, the cracked count is now based on the total file line count (including blank lines), not pipal's parsed count. This ensures the crack percentage matches the actual output from cracking tools like hashcat or john the ripper, where blank lines may represent empty passwords or hash entries.

**Impact:**
- Large datasets (>15 distinct password lengths) now report accurate compliance percentages
- NIST/HIPAA compliance is correctly calculated as passwords >= 8 chars (not >8)
- Crack percentage now reflects actual cracking tool output (including blank lines)
- Edge cases where rounding could incorrectly show PASS are now handled strictly

---

Version 2 - Two big changes, the first a massive speed increase. This patch was
submitted by Stefan Venken who said a small mention would be good enough, I want
to give him a big mention. Running through the LinkedIn lists would have taken
many many hours on version 1, version 2 went through 3.5 million records in
about 15 minutes. Thank you.

Second change is the addition of US area and zip code lookups. This little
feature gives some interesting geographical data when ran across password lists
originating in the US. The best example I've seen of this is the dump from the
Military Singles site where some passwords could be obviously seen to be grouped
around US military bases. People in the UK don't have the same relationship with
phone numbers so I know this won't work here but if anyone can suggest any other
areas where this might be useful then I'll look at building in some kind of
location awareness feature so you can specify the source of the list and get
results customized to the correct area or just run every area and see if a
pattern emerges.

A non-code-base change is for version 2 is the move from hosting the code myself
to github. This is my first github hosted project so I may get things wrong, if
I do, sorry. A number of people asked how they could submit patches so this
seems like the best way to do it, lets hope it works out.

Version 1 - Was a proof of concept, written fairly in a fairly verbose way so not
very optimised. Took off way more than I expected it would and gathered a lot of
community support.

## Feedback/Todo

If you have a read through the source for Pipal you'll notice that it isn't very
efficient at the moment. The way I built it was to try to keep each chunk of
stats together as a distinct group so that if I wanted to add a new, similar,
group then it was easy to just copy and paste the group. Now I've got a working
app and I know roughly what I need in the different group types I've got an idea
on how to rewrite the main parser to make it much more efficient and hopefully
multi-threaded which should speed up the processing by a lot for large lists.

I could have made these changes before releasing version 1.0 but I figured
before I do I want to get as much feedback as possible from users about the
features already implemented and about any new features they would like to see
so that I can bundle all these together into version 2. So, please get in touch
if there is a set of stats that you'd like to see included.

One other thing I know needs fixing, Pipal doesn't handle certain character
encodings very well. If anyone knows how to correctly deal with different
encoding types, especially with regards to regular expressions, please let me
know.

## Licence

This project released under the
[Creative Commons Attribution-Share Alike 2.0 UK: England & Wales](http://creativecommons.org/licenses/by-sa/2.0/uk/)
