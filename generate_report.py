#!/usr/bin/env python3
"""
Password Analysis Report Generator
Integrates with Pipal output to generate obfuscated HTML reports

Usage:
    python generate_report.py [pipal_output.txt]

If no file is provided, it will prompt you to run pipal first or paste content.
"""

import re
import sys
import os
import subprocess
import math
from pathlib import Path

class PasswordReportGenerator:
    def __init__(self):
        self.total_hashes = 0
        self.total_cracked = 0
        self.total_unique = 0
        self.crack_percentage = 0.0
        self.blank_passwords = 0  # Count of blank/empty lines in password file
        self.pipal_count = 0      # Count of passwords pipal actually analyzed

        self.top_passwords = []
        self.top_base_words = []
        self.length_distribution = []
        self.length_compliance = {}
        self.char_composition = {}
        self.predictable_patterns = {}
        self.last_digits = {}
        self.last_2_digits = []
        self.last_4_digits = []
        self.char_sets = []
        self.char_set_ordering = []

    def obfuscate_password(self, password):
        """Fully obfuscate password with asterisks matching length"""
        return '*' * len(password)

    def obfuscate_base_word(self, word):
        """Fully obfuscate base word with asterisks matching length"""
        return '*' * len(word)

    def get_pattern_description(self, password, index):
        """Generate a pattern description for a password"""
        patterns = [
            "[Company/Product Name]",
            "[Temporary] + [Digits]",
            "[Word] + [Year] + [Symbol]",
            "[Company] + [Digits] + [Symbols]",
            "[Temporary] + [Digits]",
            "[Name] + [Digits]",
            "[Symbol] + [Word] + [Year]",
            "[Keyboard Walk Pattern]",
            "[Word] + [Digits] + [Symbol]",
            "[Word] + [Year] + [Symbol]",
        ]
        if index < len(patterns):
            return patterns[index]
        return "[Pattern]"

    def get_baseword_category(self, word, index):
        """Generate a category description for a base word"""
        categories = [
            "[Temporary/Default]",
            "[Company/Product]",
            "[Company Name]",
            "[Season]",
            "[Common Word]",
            "[Personal Name]",
            "[Keyboard Pattern]",
            "[Short Word]",
            "[Personal Name]",
            "[Personal Name]",
        ]
        if index < len(categories):
            return categories[index]
        return "[Word]"

    def parse_pipal_output(self, content):
        """Parse pipal text output"""
        lines = content.split('\n')
        current_section = None

        for i, line in enumerate(lines):
            line = line.strip()

            # Total entries
            if line.startswith('Total entries'):
                match = re.search(r'=\s*(\d+)', line)
                if match:
                    self.total_cracked = int(match.group(1))

            # Total unique entries
            elif line.startswith('Total unique entries'):
                match = re.search(r'=\s*(\d+)', line)
                if match:
                    self.total_unique = int(match.group(1))

            # Section headers
            elif 'Top' in line and 'passwords' in line.lower():
                current_section = 'passwords'
            elif 'Top' in line and 'base words' in line.lower():
                current_section = 'base_words'
            elif 'Password length (count ordered)' in line:
                current_section = 'length_count'
            elif 'Password length (length ordered)' in line:
                current_section = 'length_ordered'
            elif 'One to six characters' in line:
                current_section = None
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.length_compliance['1-6 chars'] = (int(match.group(1)), float(match.group(2)))
            elif 'One to eight characters' in line:
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.length_compliance['1-8 chars'] = (int(match.group(1)), float(match.group(2)))
            elif 'More than eight characters' in line:
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.length_compliance['8+ chars'] = (int(match.group(1)), float(match.group(2)))
            elif 'Only lowercase alpha' in line:
                current_section = 'char_comp'
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.char_composition['Only lowercase'] = (int(match.group(1)), float(match.group(2)))
            elif 'Only uppercase alpha' in line:
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.char_composition['Only uppercase'] = (int(match.group(1)), float(match.group(2)))
            elif 'Only alpha =' in line:
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.char_composition['Only alphabetic'] = (int(match.group(1)), float(match.group(2)))
            elif 'Only numeric' in line:
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.char_composition['Only numeric'] = (int(match.group(1)), float(match.group(2)))
            elif 'First capital last symbol' in line:
                current_section = None
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.predictable_patterns['First capital, last symbol'] = (int(match.group(1)), float(match.group(2)))
            elif 'First capital last number' in line:
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.predictable_patterns['First capital, last number'] = (int(match.group(1)), float(match.group(2)))
            elif 'Single digit on the end' in line:
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.predictable_patterns['Single trailing digit'] = (int(match.group(1)), float(match.group(2)))
            elif 'Two digits on the end' in line:
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.predictable_patterns['Two trailing digits'] = (int(match.group(1)), float(match.group(2)))
            elif 'Three digits on the end' in line:
                match = re.search(r'=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.predictable_patterns['Three trailing digits'] = (int(match.group(1)), float(match.group(2)))
            elif line == 'Last digit':
                current_section = 'last_digit'
            elif 'Last 2 digits' in line:
                current_section = 'last_2'
            elif 'Last 3 digits' in line:
                current_section = 'last_3'
            elif 'Last 4 digits' in line:
                current_section = 'last_4'
            elif 'Last 5 digits' in line:
                current_section = 'last_5'
            elif line == 'Character sets':
                current_section = 'char_sets'
            elif 'Character set ordering' in line:
                current_section = 'char_ordering'
            elif line == 'Last number':
                current_section = 'last_number'

            # Parse data based on current section
            elif current_section and '=' in line and line[0] not in '|0123456789' or (current_section and re.match(r'^[a-zA-Z0-9#@!].*=\s*\d+', line)):
                match = re.match(r'^(.+?)\s*=\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    item = match.group(1).strip()
                    count = int(match.group(2))
                    pct = float(match.group(3))

                    if current_section == 'passwords':
                        self.top_passwords.append((item, count, pct))
                    elif current_section == 'base_words':
                        self.top_base_words.append((item, count, pct))
                    elif current_section in ['length_ordered', 'length_count']:
                        if current_section == 'length_count':
                            self.length_distribution.append((item, count, pct))
                    elif current_section == 'last_2':
                        self.last_2_digits.append((item, count, pct))
                    elif current_section == 'last_4':
                        self.last_4_digits.append((item, count, pct))

            # Character sets parsing (different format)
            elif current_section == 'char_sets' and ':' in line:
                match = re.match(r'^(\w+):\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.char_sets.append((match.group(1), int(match.group(2)), float(match.group(3))))
            elif current_section == 'char_ordering' and ':' in line:
                match = re.match(r'^(\w+):\s*(\d+)\s*\(([0-9.]+)%\)', line)
                if match:
                    self.char_set_ordering.append((match.group(1), int(match.group(2)), float(match.group(3))))

    def calculate_percentages(self):
        """Calculate crack percentage based on total hashes"""
        if self.total_hashes > 0:
            self.crack_percentage = (self.total_cracked / self.total_hashes) * 100

    def generate_html(self, output_file='password_report.html'):
        """Generate a 2-column HTML report with automatic section distribution"""

        # Calculate max for bar scaling
        max_length_count = max([x[1] for x in self.length_distribution]) if self.length_distribution else 1

        # Build sections as (title, content_html, row_count) tuples
        sections = []

        # Section: Top Passwords
        pwd_rows = min(len(self.top_passwords), 10)
        if pwd_rows > 0:
            content = '<table>\n      <tr><th>#</th><th>Password</th><th class="right">Count</th><th class="right">%</th></tr>\n'
            for i, (pwd, count, pct) in enumerate(self.top_passwords[:10], 1):
                obfuscated = self.obfuscate_password(pwd)
                content += f'      <tr><td>{i}</td><td><code>{obfuscated}</code></td><td class="right">{count}</td><td class="right">{pct:.2f}</td></tr>\n'
            content += '    </table>'
            sections.append(('Top 10 Cracked Passwords', content, pwd_rows + 2))

        # Section: Top Base Words
        base_rows = min(len(self.top_base_words), 10)
        if base_rows > 0:
            content = '<table>\n      <tr><th>#</th><th>Base Word</th><th class="right">Count</th><th class="right">%</th></tr>\n'
            for i, (word, count, pct) in enumerate(self.top_base_words[:10], 1):
                obfuscated = self.obfuscate_base_word(word)
                content += f'      <tr><td>{i}</td><td><code>{obfuscated}</code></td><td class="right">{count}</td><td class="right">{pct:.2f}</td></tr>\n'
            content += '    </table>'
            sections.append(('Top 10 Base Words', content, base_rows + 2))

        # Section: Key Findings (merged with predictable patterns summary)
        findings_content = '<table>\n      <tr><th>Finding</th><th>Severity</th></tr>\n'
        findings_rows = 2
        if self.crack_percentage >= 50:
            findings_content += f'      <tr class="critical"><td>{self.crack_percentage:.1f}% of passwords cracked</td><td>Critical</td></tr>\n'
            findings_rows += 1
        elif self.crack_percentage >= 25:
            findings_content += f'      <tr class="high"><td>{self.crack_percentage:.1f}% of passwords cracked</td><td>High</td></tr>\n'
            findings_rows += 1
        else:
            findings_content += f'      <tr class="medium"><td>{self.crack_percentage:.1f}% of passwords cracked</td><td>Medium</td></tr>\n'
            findings_rows += 1

        first_cap_symbol = self.predictable_patterns.get('First capital, last symbol', (0, 0))[1]
        first_cap_num = self.predictable_patterns.get('First capital, last number', (0, 0))[1]
        predictable_pct = first_cap_symbol + first_cap_num
        if predictable_pct > 30:
            findings_content += f'      <tr class="high"><td>{predictable_pct:.1f}% use predictable patterns</td><td>High</td></tr>\n'
            findings_rows += 1

        one_to_eight = self.length_compliance.get('1-8 chars', (0, 0))[1]
        if one_to_eight > 10:
            findings_content += f'      <tr class="critical"><td>{one_to_eight:.1f}% use 8 or fewer chars</td><td>Critical</td></tr>\n'
            findings_rows += 1

        fifteen_or_fewer = sum(count for length, count, pct in self.length_distribution if length.isdigit() and int(length) <= 15)
        fifteen_or_fewer_pct = (fifteen_or_fewer / self.total_cracked * 100) if self.total_cracked > 0 else 0
        if fifteen_or_fewer_pct > 50:
            findings_content += f'      <tr class="medium"><td>{fifteen_or_fewer_pct:.1f}% use 15 or fewer chars</td><td>Medium</td></tr>\n'
            findings_rows += 1
        findings_content += '    </table>'
        sections.append(('Key Findings', findings_content, findings_rows))

        # Section: Password Length (merged with compliance)
        one_to_six = self.length_compliance.get('1-6 chars', (0, 0))
        one_to_eight_data = self.length_compliance.get('1-8 chars', (0, 0))
        over_eight = self.length_compliance.get('8+ chars', (0, 0))
        len_rows = min(len(self.length_distribution), 8)
        if len_rows > 0:
            content = '<table>\n      <tr><th>Length</th><th class="right">Count</th><th class="right">%</th><th></th></tr>\n'
            for length, count, pct in self.length_distribution[:8]:
                bar_width = int((count / max_length_count) * 100) if max_length_count > 0 else 0
                content += f'      <tr><td>{length} chars</td><td class="right">{count}</td><td class="right">{pct:.1f}</td><td><span class="bar" style="width:{bar_width}%"></span></td></tr>\n'
            # Reconciliation row: every password has exactly one length, so the shown
            # distribution must account for 100% of the cracked total. The table displays
            # only the top 8 lengths by count; fold every remaining length into one
            # aggregated row so the visible column never silently sums to less than the
            # whole. The per-length detail stays behind the scenes; the face always ties out.
            shown_count = sum(count for length, count, pct in self.length_distribution[:8])
            all_len_count = sum(count for length, count, pct in self.length_distribution if str(length).isdigit())
            remainder_count = all_len_count - shown_count
            has_remainder = remainder_count > 0
            if has_remainder:
                remainder_pct = (remainder_count / self.total_cracked * 100) if self.total_cracked > 0 else 0
                content += f'      <tr><td>All other lengths</td><td class="right">{remainder_count}</td><td class="right">{remainder_pct:.1f}</td><td></td></tr>\n'
            # Add compliance summary rows
            meets_12_pct = sum(count for length, count, pct in self.length_distribution if length.isdigit() and int(length) >= 12)
            meets_12_pct = (meets_12_pct / self.total_cracked * 100) if self.total_cracked > 0 else 0
            content += f'      <tr class="summary"><td colspan="4"><b>Compliance:</b> {meets_12_pct:.0f}% meet 12+ char minimum</td></tr>\n'
            content += '    </table>'
            sections.append(('Password Length', content, len_rows + 3 + (1 if has_remainder else 0)))

        # Section: Character Analysis (merged composition + sets)
        content = '<table>\n      <tr><th>Category</th><th class="right">Count</th><th class="right">%</th></tr>\n'
        char_rows = 1
        # Add top character sets (most useful data)
        for name, count, pct in self.char_sets[:4]:
            readable_name = name.replace('alpha', ' alpha').replace('special', ' + special').replace('num', ' + num').replace('mixed', 'Mixed').strip()
            content += f'      <tr><td>{readable_name}</td><td class="right">{count}</td><td class="right">{pct:.1f}</td></tr>\n'
            char_rows += 1
        content += '    </table>'
        if char_rows > 1:
            sections.append(('Character Analysis', content, char_rows + 1))

        # Section: Pattern Analysis (merged ordering + trailing digits)
        content = '<table>\n      <tr><th>Pattern Type</th><th class="right">Count</th><th class="right">%</th></tr>\n'
        pattern_rows = 1
        # Top ordering patterns
        for name, count, pct in self.char_set_ordering[:3]:
            readable_name = name.replace('string', 'String+').replace('digit', 'Digit').replace('special', 'Special+').replace('other', 'Other/').replace('mask', 'Complex').replace('all', 'All').rstrip('+')
            content += f'      <tr><td>{readable_name}</td><td class="right">{count}</td><td class="right">{pct:.1f}</td></tr>\n'
            pattern_rows += 1
        # Add trailing digits summary
        if self.last_4_digits:
            top_4 = self.last_4_digits[0]
            content += f'      <tr><td>Top trailing 4: {top_4[0]}</td><td class="right">{top_4[1]}</td><td class="right">{top_4[2]:.1f}</td></tr>\n'
            pattern_rows += 1
        content += '    </table>'
        if pattern_rows > 1:
            sections.append(('Pattern Analysis', content, pattern_rows + 1))

        # Section: Compliance Assessment
        # Validate data completeness - sum of length_distribution should equal total_cracked
        total_from_lengths = sum(count for length, count, pct in self.length_distribution if length.isdigit())
        data_coverage = (total_from_lengths / self.total_cracked * 100) if self.total_cracked > 0 else 0

        # Length thresholds aligned to current (May 2026) framework versions:
        #   NIST SP 800-63B Rev 4 (Aug 2025) - 15 chars SHALL for single-factor (was 8 in Rev 3)
        #   PCI DSS v4.0.1 Req 8.3.6 - 12 chars (8-char legacy fallback only if system cannot support 12)
        #   HIPAA 45 CFR 164.308(a)(5)(ii)(D) - no explicit length; OCR guidance recommends 800-63B alignment
        #   CIS Controls v8.1 Safeguard 5.2 - 14 chars non-MFA / 8 chars MFA
        meets_8 = sum(count for length, count, pct in self.length_distribution if length.isdigit() and int(length) >= 8)
        meets_12 = sum(count for length, count, pct in self.length_distribution if length.isdigit() and int(length) >= 12)
        meets_14 = sum(count for length, count, pct in self.length_distribution if length.isdigit() and int(length) >= 14)
        meets_15 = sum(count for length, count, pct in self.length_distribution if length.isdigit() and int(length) >= 15)
        pct_8 = (meets_8 / self.total_cracked * 100) if self.total_cracked > 0 else 0
        pct_12 = (meets_12 / self.total_cracked * 100) if self.total_cracked > 0 else 0
        pct_14 = (meets_14 / self.total_cracked * 100) if self.total_cracked > 0 else 0
        pct_15 = (meets_15 / self.total_cracked * 100) if self.total_cracked > 0 else 0

        has_complexity = sum(count for name, count, pct in self.char_sets if 'special' in name.lower() and 'num' in name.lower())
        pct_complexity = (has_complexity / self.total_cracked * 100) if self.total_cracked > 0 else 0

        # Use floor() for strict compliance - 99.5% should NOT round to PASS
        pct_8_display = math.floor(pct_8)
        pct_12_display = math.floor(pct_12)
        pct_14_display = math.floor(pct_14)
        pct_15_display = math.floor(pct_15)
        pct_complexity_display = math.floor(pct_complexity)

        # Determine pass/fail based on floored percentage (strict: must be exactly 100%)
        nist_status = "pass" if pct_15_display >= 100 else "fail"
        nist_text = "PASS" if pct_15_display >= 100 else "FAIL"
        pci_status = "pass" if pct_12_display >= 100 else "fail"
        pci_text = "PASS" if pct_12_display >= 100 else "FAIL"
        hipaa_status = "pass" if pct_15_display >= 100 else "fail"
        hipaa_text = "PASS" if pct_15_display >= 100 else "FAIL"
        cis_status = "pass" if pct_14_display >= 100 else "fail"
        cis_text = "PASS" if pct_14_display >= 100 else "FAIL"

        # Option C verdict: passing rows read "PASS"; failing rows show the deficiency
        # (percent NOT meeting the requirement) so the compliant and fail figures on the
        # face always sum to 100. Fail = 100 - floored compliant, keeping the row reconciled.
        nist_verdict = "PASS" if nist_status == "pass" else f"{100 - pct_15_display}% fail"
        pci_verdict = "PASS" if pci_status == "pass" else f"{100 - pct_12_display}% fail"
        hipaa_verdict = "PASS (per NIST)" if hipaa_status == "pass" else f"{100 - pct_15_display}% fail (per NIST)"
        cis_verdict = "PASS" if cis_status == "pass" else f"{100 - pct_14_display}% fail"

        # Compliance Assessment is rendered as a standalone full-width section AFTER the
        # 2-column flow (built later in this method as `compliance_section_html`).
        # See verified citations (May 2026):
        #   NIST SP 800-63B-4 Aug 2025 §3.1.1.2 (15 chars SHALL, composition rules SHALL NOT)
        #   PCI DSS v4.0.1 Req 8.3.6 (12 chars)
        #   HIPAA 45 CFR 164.308(a)(5)(ii)(D) (Addressable, no explicit length)
        #   CIS Controls v8.1 Safeguard 5.2 (14 chars non-MFA / 8 chars MFA)

        # Optional blank-row + data-coverage details, emitted INSIDE the standalone section.
        blank_row = ""
        if self.blank_passwords > 0:
            blank_pct = (self.blank_passwords / self.total_cracked * 100) if self.total_cracked > 0 else 0
            blank_row = (
                f'\n      <tr class="critical">'
                f'<td class="framework-name">Blank / Empty</td>'
                f'<td class="citation">AD UF_PASSWD_NOTREQD flag</td>'
                f'<td>Accounts with empty NT hash ({self.blank_passwords:,} found)</td>'
                f'<td class="status-cell"><span class="status-pct fail">{blank_pct:.1f}%</span>'
                f'<span class="status-verdict fail">of cracked</span></td></tr>'
            )

        coverage_note = ""
        if data_coverage < 99.9:
            coverage_note = (
                f'\n      <tr class="summary"><td colspan="4">'
                f'Note: Compliance % based on {total_from_lengths:,} analyzable passwords '
                f'({data_coverage:.1f}% of total)</td></tr>'
            )

        compliance_section_html = f'''<div class="compliance-section">
  <h2>Compliance Assessment</h2>
  <table class="compliance-table">
    <colgroup>
      <col style="width:18%">
      <col style="width:24%">
      <col style="width:38%">
      <col style="width:20%">
    </colgroup>
    <thead>
      <tr>
        <th>Framework</th>
        <th>Citation</th>
        <th>Requirement</th>
        <th class="right">Compliance</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td class="framework-name">NIST SP 800-63B</td>
        <td class="citation">Rev 4 &sect;3.1.1.2 (Aug 2025)</td>
        <td>Minimum 15 characters required (single-factor logins)</td>
        <td class="status-cell"><span class="status-pct compliant">{pct_15_display}% Compliant</span><span class="status-verdict {nist_status}">{nist_verdict}</span></td>
      </tr>
      <tr>
        <td class="framework-name">PCI DSS</td>
        <td class="citation">v4.0.1 Req 8.3.6</td>
        <td>Min 12 chars</td>
        <td class="status-cell"><span class="status-pct compliant">{pct_12_display}% Compliant</span><span class="status-verdict {pci_status}">{pci_verdict}</span></td>
      </tr>
      <tr>
        <td class="framework-name">HIPAA</td>
        <td class="citation">45 CFR 164.308(a)(5)(ii)(D)</td>
        <td>No explicit length; HHS OCR guidance recommends NIST 800-63B alignment. NPRM pending (90 FR 898)</td>
        <td class="status-cell"><span class="status-pct compliant">{pct_15_display}% Compliant</span><span class="status-verdict {hipaa_status}">{hipaa_verdict}</span></td>
      </tr>
      <tr>
        <td class="framework-name">CIS Controls</td>
        <td class="citation">v8.1 Safeguard 5.2</td>
        <td>Min 14 chars non-MFA / 8 chars with MFA</td>
        <td class="status-cell"><span class="status-pct compliant">{pct_14_display}% Compliant</span><span class="status-verdict {cis_status}">{cis_verdict}</span></td>
      </tr>
      <tr>
        <td class="framework-name">Composition Rules</td>
        <td class="citation">NIST 800-63B-4 &sect;3.1.1.2</td>
        <td>Complexity and composition rules not permitted</td>
        <td class="status-cell"><span class="status-pct fail">{pct_complexity_display}%</span><span class="status-verdict fail">legacy enforced</span></td>
      </tr>{blank_row}{coverage_note}
    </tbody>
  </table>
</div>
'''

        # Section: Recommendations (in-column)
        content = '''<table>
      <tr><td>1. Enforce 15+ char minimum (NIST SP 800-63B-4 &sect;3.1.1.2)</td></tr>
      <tr><td>2. Block common patterns, sequences &amp; breached passwords</td></tr>
      <tr><td>3. Remove legacy complexity rules (not permitted under NIST 800-63B-4)</td></tr>
      <tr><td>4. Audit accounts with UF_PASSWD_NOTREQD flag set</td></tr>
    </table>'''
        sections.append(('Recommendations', content, 5))

        # Distribute sections into two columns based on row count
        col1_sections = []
        col2_sections = []
        col1_weight = 0
        col2_weight = 0

        for title, content, weight in sections:
            if col1_weight <= col2_weight:
                col1_sections.append((title, content))
                col1_weight += weight
            else:
                col2_sections.append((title, content))
                col2_weight += weight

        # Build HTML
        html = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Password Analysis Report</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: Arial, sans-serif;
      font-size: 10pt;
      padding: 6px 12px;
      max-width: 7.7in;
      line-height: 1.2;
      background: #ffffff;
      color: #111111;
    }}
    h1 {{ font-size: 14pt; margin-bottom: 4px; text-align: center; }}
    h2 {{ font-size: 9.5pt; margin: 4px 0 2px 0; background: #333; color: white; padding: 2px 5px; }}
    .container {{ display: flex; gap: 8px; }}
    .col {{ flex: 1 1 0; min-width: 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 2px; }}
    th, td {{ border: 1px solid #ccc; padding: 1px 3px; text-align: left; font-size: 9pt; line-height: 1.15; }}
    th {{ background: #f0f0f0; font-weight: bold; }}
    .right {{ text-align: right; }}
    .center {{ text-align: center; }}
    .critical {{ background: #ffcccc; }}
    .high {{ background: #ffe6cc; }}
    .medium {{ background: #ffffcc; }}
    .compliant {{ color: #0a0; font-weight: bold; }}
    .summary {{ background: #f8f8f8; font-size: 8.5pt; }}
    .summary-box {{ background: #f5f5f5; padding: 4px; margin-bottom: 5px; }}
    .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 4px; text-align: center; }}
    .summary-item {{ padding: 2px; }}
    .summary-value {{ font-size: 13pt; font-weight: bold; line-height: 1.1; }}
    .summary-value.critical {{ color: #c00; }}
    .summary-value.green {{ color: #090; }}
    .summary-label {{ font-size: 8pt; color: #666; }}
    .bar {{ background: #4a90d9; height: 7px; display: inline-block; }}
    code {{ background: #eee; padding: 0 2px; font-size: 8.5pt; font-family: monospace; }}
    .fail {{ color: #c00; font-weight: bold; }}
    .pass {{ color: #090; font-weight: bold; }}
    .compliance-section {{ margin-top: 5px; page-break-inside: avoid; }}
    .compliance-table th, .compliance-table td {{ padding: 4px 8px; vertical-align: middle; font-size: 10pt; line-height: 1.35; }}
    .compliance-table th {{ background: #333; color: white; font-size: 10pt; }}
    .compliance-table tbody tr:nth-child(even) {{ background: #fafafa; }}
    .compliance-table .framework-name {{ font-weight: bold; white-space: nowrap; }}
    .compliance-table .citation {{ font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 8pt; color: #444; }}
    .compliance-table .status-cell {{ text-align: right; white-space: nowrap; }}
    .compliance-table .status-pct {{ font-size: 10pt; font-weight: bold; }}
    .compliance-table .status-verdict {{ font-size: 10pt; font-weight: bold; margin-left: 7px; }}
    @page {{ size: letter; margin: 0.3in; }}
    @media print {{
      body {{ padding: 0; max-width: none; font-size: 9pt; }}
      .container {{ gap: 8px; }}
      h1 {{ font-size: 13pt; margin-bottom: 3px; }}
      h2 {{ margin: 3px 0 1px 0; font-size: 9pt; }}
      table {{ margin-bottom: 1px; }}
      th, td {{ padding: 1px 3px; font-size: 8.5pt; }}
      .summary-box {{ padding: 3px; margin-bottom: 3px; }}
      .summary-value {{ font-size: 12pt; }}
      .summary-label {{ font-size: 7.5pt; }}
      .compliance-section {{ margin-top: 3px; }}
      .compliance-table th, .compliance-table td {{ padding: 3px 6px; font-size: 9.5pt; }}
      .compliance-table .status-pct {{ font-size: 9.5pt; }}
      .compliance-table .status-verdict {{ font-size: 9.5pt; }}
    }}
  </style>
</head>
<body>

<h1>Password Analysis Report</h1>

<div class="summary-box">
  <div class="summary-grid">
    <div class="summary-item">
      <div class="summary-value green">{self.total_hashes:,}</div>
      <div class="summary-label">Total Password Hashes</div>
    </div>
    <div class="summary-item">
      <div class="summary-value">{self.total_cracked:,}</div>
      <div class="summary-label">Hashes Cracked</div>
    </div>
    <div class="summary-item">
      <div class="summary-value">{self.total_unique:,}</div>
      <div class="summary-label">Unique Passwords</div>
    </div>
    <div class="summary-item">
      <div class="summary-value critical">{self.crack_percentage:.2f}%</div>
      <div class="summary-label">Cracked</div>
    </div>
  </div>
</div>

<div class="container">
  <div class="col">
'''
        # Add column 1 sections
        for title, content in col1_sections:
            html += f'    <h2>{title}</h2>\n    {content}\n\n'

        html += '  </div>\n  <div class="col">\n'

        # Add column 2 sections
        for title, content in col2_sections:
            html += f'    <h2>{title}</h2>\n    {content}\n\n'

        html += '  </div>\n</div>\n\n'
        html += compliance_section_html
        html += '''
</body>
</html>
'''

        with open(output_file, 'w') as f:
            f.write(html)

        return output_file


def strip_rtf(content):
    """Strip RTF formatting and return plain text"""
    # Remove RTF header and formatting
    content = re.sub(r'^\{\\rtf1.*?\\f0\\fs\d+\s*\\cf0\s*', '', content, flags=re.DOTALL)
    content = re.sub(r'\}$', '', content)
    # Remove RTF control words
    content = re.sub(r'\\[a-z]+\d*\s?', '', content)
    # Remove braces
    content = re.sub(r'[{}]', '', content)
    # Convert RTF line breaks
    content = content.replace('\\\n', '\n').replace('\\', '\n')
    return content


def run_pipal(password_file, pipal_path):
    """Run pipal on the password file and return output"""
    pipal_script = os.path.join(pipal_path, 'pipal.rb')
    if not os.path.exists(pipal_script):
        print(f"Error: pipal.rb not found at {pipal_script}")
        return None

    try:
        result = subprocess.run(
            ['ruby', pipal_script, password_file],
            capture_output=True,
            text=True,
            cwd=pipal_path
        )
        return result.stdout
    except Exception as e:
        print(f"Error running pipal: {e}")
        return None


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate HTML password analysis report from pipal output or raw passwords.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # One command from raw passwords (runs pipal automatically):
  python3 generate_report.py -p passwords.txt -t 10000 -o report.html

  # From existing pipal output:
  python3 generate_report.py -i pipal_output.txt -t 10000 -o report.html

  # Interactive mode:
  python3 generate_report.py
        '''
    )
    parser.add_argument('-p', '--passwords', help='Raw password file (will run pipal automatically)')
    parser.add_argument('-i', '--input', help='Existing pipal output file')
    parser.add_argument('-t', '--total', type=int, help='Total password hashes before cracking')
    parser.add_argument('-o', '--output', default='password_report.html', help='Output HTML filename (default: password_report.html)')

    args = parser.parse_args()

    # Check if running in command-line mode or interactive mode
    if args.passwords or args.input:
        # Command-line mode
        if not args.total:
            print("Error: --total is required when using command-line mode")
            print("Usage: python3 generate_report.py -p passwords.txt -t 10000 -o report.html")
            sys.exit(1)

        generator = PasswordReportGenerator()
        generator.total_hashes = args.total

        if args.passwords:
            # Run pipal on raw passwords
            if not os.path.exists(args.passwords):
                print(f"Error: File not found: {args.passwords}")
                sys.exit(1)

            # Count total lines in password file (including blank lines)
            # This represents the actual cracked count from the cracking tool
            with open(args.passwords, 'r', errors='ignore') as f:
                password_file_lines = sum(1 for _ in f)

            pipal_path = os.path.dirname(os.path.abspath(__file__))
            print(f"Running pipal on {args.passwords}...")
            content = run_pipal(args.passwords, pipal_path)
            if content is None:
                sys.exit(1)
        else:
            # Use existing pipal output
            if not os.path.exists(args.input):
                print(f"Error: File not found: {args.input}")
                sys.exit(1)

            with open(args.input, 'r', errors='ignore') as f:
                content = f.read()
            if content.startswith('{\\rtf'):
                content = strip_rtf(content)

        # Parse and generate
        print("Parsing pipal output...")
        generator.parse_pipal_output(content)

        # When using -p flag, override total_cracked with actual file line count
        # (includes blank lines, which represent the total output from cracking tool)
        if args.passwords:
            generator.pipal_count = generator.total_cracked  # Store pipal's count
            generator.blank_passwords = password_file_lines - generator.total_cracked
            if generator.blank_passwords > 0:
                print(f"  Note: Using file line count ({password_file_lines:,}) instead of pipal count ({generator.total_cracked:,})")
                print(f"  Blank/empty passwords detected: {generator.blank_passwords:,}")
            generator.total_cracked = password_file_lines

        generator.calculate_percentages()

        output_file = args.output
        if not output_file.endswith('.html'):
            output_file += '.html'

        print(f"Generating report...")
        output_path = generator.generate_html(output_file)

        print(f"\nReport generated: {output_path}")
        print(f"  Total Hashes: {generator.total_hashes:,} | Cracked: {generator.total_cracked:,} ({generator.crack_percentage:.2f}%)")

    else:
        # Interactive mode (original behavior)
        print("=" * 60)
        print("Password Analysis Report Generator")
        print("=" * 60)
        print()
        print("Tip: For one-command usage, run:")
        print("  python3 generate_report.py -p passwords.txt -t TOTAL_HASHES -o report.html")
        print()

        # Get total password hashes
        while True:
            try:
                total_hashes = input("Enter Total Password Hashes (total number of hashes before cracking): ")
                total_hashes = int(total_hashes.strip().replace(',', ''))
                if total_hashes > 0:
                    break
                print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")

        print()

        generator = PasswordReportGenerator()
        generator.total_hashes = total_hashes

        # Check if pipal output file provided as positional argument
        if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
            input_file = sys.argv[1]
            with open(input_file, 'r', errors='ignore') as f:
                content = f.read()
            if content.startswith('{\\rtf'):
                content = strip_rtf(content)
        else:
            print("Options:")
            print("  1. Parse existing pipal output file")
            print("  2. Run pipal on a password file")
            print()
            choice = input("Enter choice (1 or 2): ").strip()

            if choice == '2':
                password_file = input("Enter path to cracked passwords file: ").strip()
                if not os.path.exists(password_file):
                    print(f"Error: File not found: {password_file}")
                    sys.exit(1)

                pipal_path = os.path.dirname(os.path.abspath(__file__))
                print(f"\nRunning pipal on {password_file}...")
                content = run_pipal(password_file, pipal_path)
                if content is None:
                    sys.exit(1)
            else:
                input_file = input("Enter path to pipal output file: ").strip()
                if not os.path.exists(input_file):
                    print(f"Error: File not found: {input_file}")
                    sys.exit(1)

                with open(input_file, 'r', errors='ignore') as f:
                    content = f.read()
                if content.startswith('{\\rtf'):
                    content = strip_rtf(content)

        # Parse the content
        print("\nParsing pipal output...")
        generator.parse_pipal_output(content)
        generator.calculate_percentages()

        # Get output file name
        output_file = input("\nEnter output filename (default: password_report.html): ").strip()
        if not output_file:
            output_file = 'password_report.html'
        if not output_file.endswith('.html'):
            output_file += '.html'

        # Generate report
        print(f"\nGenerating report...")
        output_path = generator.generate_html(output_file)

        print(f"\nReport generated: {output_path}")
        print()
        print("Summary:")
        print(f"  Total Password Hashes: {generator.total_hashes:,}")
        print(f"  Total Hashes Cracked:  {generator.total_cracked:,}")
        print(f"  Total Unique Entries:  {generator.total_unique:,}")
        print(f"  Cracked:               {generator.crack_percentage:.2f}%")
        print()
        print("Open the HTML file in a browser to view the report.")


if __name__ == '__main__':
    main()
