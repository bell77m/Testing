"""
Automated Test Report Generator
Generates beautiful documentation from test results using Obsidian notes and Pandoc
"""
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import xml.etree.ElementTree as ET


class TestReportGenerator:
    """Generate test reports from Allure results and convert to multiple formats"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.docs_dir = self.project_root / "docs"
        self.reports_dir = self.project_root / "reports"
        self.allure_results = self.reports_dir / "allure-results"
        self.output_dir = self.docs_dir / "generated_reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def parse_allure_results(self) -> Dict:
        """Parse Allure test results from JSON files"""
        if not self.allure_results.exists():
            print(f"❌ Allure results not found: {self.allure_results}")
            return {}

        test_results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'tests': []
        }

        # Parse all result JSON files
        for result_file in self.allure_results.glob("*-result.json"):
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    test_results['total'] += 1
                    status = data.get('status', 'unknown')

                    if status == 'passed':
                        test_results['passed'] += 1
                    elif status == 'failed':
                        test_results['failed'] += 1
                    elif status == 'skipped':
                        test_results['skipped'] += 1

                    test_results['tests'].append({
                        'name': data.get('name', 'Unknown'),
                        'status': status,
                        'duration': data.get('stop', 0) - data.get('start', 0),
                        'description': data.get('description', ''),
                        'steps': data.get('steps', []),
                        'attachments': data.get('attachments', [])
                    })
            except Exception as e:
                print(f"⚠️ Failed to parse {result_file.name}: {e}")

        return test_results

    def generate_markdown_report(self, test_results: Dict, template: str = "comprehensive") -> str:
        """Generate markdown report from test results"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if template == "comprehensive":
            return self._generate_comprehensive_report(test_results, timestamp)
        elif template == "executive":
            return self._generate_executive_summary(test_results, timestamp)
        else:
            return self._generate_basic_report(test_results, timestamp)

    def _generate_comprehensive_report(self, results: Dict, timestamp: str) -> str:
        """Generate detailed comprehensive report"""
        total = results['total']
        passed = results['passed']
        failed = results['failed']
        skipped = results['skipped']
        pass_rate = (passed / total * 100) if total > 0 else 0

        md = f"""# 🧪 Test Execution Report

**Generated:** {timestamp}  
**Project:** QA Automation Framework

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| Total Tests | {total} |
| ✅ Passed | {passed} |
| ❌ Failed | {failed} |
| ⏭️ Skipped | {skipped} |
| **Pass Rate** | **{pass_rate:.1f}%** |

### Status Overview

```
Pass Rate: {pass_rate:.1f}%
{'█' * int(pass_rate / 5)}{'░' * (20 - int(pass_rate / 5))}
```

---

## 📋 Test Results by Status

### ✅ Passed Tests ({passed})

"""
        # Add passed tests
        for test in results['tests']:
            if test['status'] == 'passed':
                duration_ms = test['duration'] / 1000000  # Convert to ms
                md += f"- **{test['name']}** ✓\n"
                md += f"  - Duration: {duration_ms:.0f}ms\n"
                if test['description']:
                    md += f"  - Description: {test['description']}\n"
                md += "\n"

        md += f"""
### ❌ Failed Tests ({failed})

"""
        # Add failed tests with details
        for test in results['tests']:
            if test['status'] == 'failed':
                duration_ms = test['duration'] / 1000000
                md += f"- **{test['name']}** ✗\n"
                md += f"  - Duration: {duration_ms:.0f}ms\n"
                if test['description']:
                    md += f"  - Description: {test['description']}\n"

                # Add failure steps
                if test['steps']:
                    md += "  - **Failed Steps:**\n"
                    for step in test['steps']:
                        status_icon = "✓" if step.get('status') == 'passed' else "✗"
                        md += f"    - {status_icon} {step.get('name', 'Unknown step')}\n"
                md += "\n"

        md += f"""
---

## 📈 Test Metrics

### Performance Metrics

| Test Type | Average Duration | Count |
|-----------|------------------|-------|
| Smoke | - | - |
| Regression | - | - |
| Total | {self._calculate_avg_duration(results['tests']):.0f}ms | {total} |

### Coverage Analysis

- **Critical Path Tests:** {passed} / {total}
- **Security Tests:** Pending analysis
- **API Tests:** Pending analysis

---

## 🔍 Detailed Test Breakdown

"""
        # Add all tests with full details
        for i, test in enumerate(results['tests'], 1):
            status_emoji = {
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️'
            }.get(test['status'], '❓')

            md += f"### {i}. {test['name']} {status_emoji}\n\n"
            md += f"**Status:** {test['status'].upper()}  \n"
            md += f"**Duration:** {test['duration'] / 1000000:.0f}ms  \n"

            if test['description']:
                md += f"**Description:** {test['description']}  \n"

            if test['steps']:
                md += "\n**Test Steps:**\n\n"
                for step in test['steps']:
                    step_status = "✓" if step.get('status') == 'passed' else "✗"
                    md += f"- {step_status} {step.get('name', 'Unknown')}\n"

            md += "\n---\n\n"

        md += """
## 📝 Notes

- All tests executed in automated CI/CD pipeline
- Test artifacts stored in Allure report
- Full trace logs available in `logs/` directory

---

*Report generated by QA Automation Framework*
"""
        return md

    def _generate_executive_summary(self, results: Dict, timestamp: str) -> str:
        """Generate executive summary report"""
        total = results['total']
        passed = results['passed']
        failed = results['failed']
        pass_rate = (passed / total * 100) if total > 0 else 0

        return f"""# Executive Test Summary

**Date:** {timestamp}

## Key Metrics

- **Total Tests Executed:** {total}
- **Pass Rate:** {pass_rate:.1f}%
- **Failed Tests:** {failed}

## Status

{'✅ All tests passed!' if failed == 0 else f'⚠️ {failed} test(s) require attention'}

## Recommendation

{'Production deployment approved.' if pass_rate >= 95 else 'Review failures before deployment.'}

---

*Generated automatically from test execution*
"""

    def _generate_basic_report(self, results: Dict, timestamp: str) -> str:
        """Generate basic test report"""
        return f"""# Test Report

Generated: {timestamp}

## Summary
- Total: {results['total']}
- Passed: {results['passed']}
- Failed: {results['failed']}
- Skipped: {results['skipped']}

## Test List
"""

    def _calculate_avg_duration(self, tests: List[Dict]) -> float:
        """Calculate average test duration"""
        if not tests:
            return 0
        total_duration = sum(test['duration'] for test in tests)
        return (total_duration / len(tests)) / 1000000  # Convert to ms

    def save_markdown_report(self, content: str, filename: str = None) -> Path:
        """Save markdown report to docs folder"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.md"

        filepath = self.output_dir / filename
        filepath.write_text(content, encoding='utf-8')
        print(f"✅ Markdown report saved: {filepath}")
        return filepath

    def convert_with_pandoc(self, input_file: Path, output_format: str = "html") -> Path:
        """Convert markdown to other formats using Pandoc"""
        output_file = input_file.with_suffix(f".{output_format}")

        try:
            # Check if pandoc is installed
            subprocess.run(["pandoc", "--version"],
                           capture_output=True, check=True)

            # Pandoc conversion with enhanced styling
            cmd = [
                "pandoc",
                str(input_file),
                "-o", str(output_file),
                "--standalone",
                "--toc",  # Table of contents
                "--toc-depth=3",
                "-V", "geometry:margin=1in"
            ]

            if output_format == "html":
                cmd.extend([
                    "--css=https://cdn.jsdelivr.net/npm/water.css@2/out/water.css",
                    "--metadata", "title=Test Execution Report"
                ])
            elif output_format == "pdf":
                cmd.extend([
                    "--pdf-engine=pdflatex",
                    "-V", "colorlinks=true"
                ])

            subprocess.run(cmd, check=True)
            print(f"✅ Converted to {output_format.upper()}: {output_file}")
            return output_file

        except FileNotFoundError:
            print("❌ Pandoc not installed. Install with: https://pandoc.org/installing.html")
            return None
        except subprocess.CalledProcessError as e:
            print(f"❌ Pandoc conversion failed: {e}")
            return None

    def generate_obsidian_compatible(self, content: str, filename: str = None) -> Path:
        """Save report in Obsidian-compatible format with metadata"""
        timestamp = datetime.now().strftime("%Y-%m-%d")

        # Add Obsidian frontmatter
        frontmatter = f"""---
type: test-report
date: {timestamp}
tags: [testing, automation, report]
status: completed
---

"""
        full_content = frontmatter + content

        if filename is None:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d')}.md"

        filepath = self.docs_dir / filename
        filepath.write_text(full_content, encoding='utf-8')
        print(f"✅ Obsidian report saved: {filepath}")
        return filepath

    def generate_all_formats(self, template: str = "comprehensive"):
        """Generate reports in all formats"""
        print("\n🚀 Starting report generation...")

        # Parse test results
        results = self.parse_allure_results()
        if not results or results['total'] == 0:
            print("⚠️ No test results found. Run tests first!")
            return

        # Generate markdown
        print(f"\n📝 Generating {template} markdown report...")
        content = self.generate_markdown_report(results, template)

        # Save to output directory
        md_file = self.save_markdown_report(content)

        # Save to Obsidian
        obsidian_file = self.generate_obsidian_compatible(content)

        # Convert to other formats
        print("\n🔄 Converting to multiple formats...")
        self.convert_with_pandoc(md_file, "html")
        self.convert_with_pandoc(md_file, "docx")

        # Try PDF if LaTeX is available
        pdf_file = self.convert_with_pandoc(md_file, "pdf")

        print("\n✅ Report generation complete!")
        print(f"📁 Output directory: {self.output_dir}")
        print(f"📝 Obsidian vault: {self.docs_dir}")


def main():
    """Main execution function"""
    generator = TestReportGenerator()

    # Generate all report formats
    generator.generate_all_formats(template="comprehensive")

    # Also generate executive summary
    results = generator.parse_allure_results()
    if results:
        exec_content = generator.generate_markdown_report(results, template="executive")
        exec_file = generator.save_markdown_report(exec_content, "executive_summary.md")
        generator.convert_with_pandoc(exec_file, "html")


if __name__ == "__main__":
    main()