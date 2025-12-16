#!/usr/bin/env python3
"""
Generate Test Reports Script
Orchestrates report generation from test results
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.test_report_generator import TestReportGenerator


def main():
    """Main script execution"""
    print("=" * 60)
    print("🚀 QA Automation Report Generator")
    print("=" * 60)

    # Get configuration from environment
    report_template = os.getenv('REPORT_TEMPLATE', 'comprehensive')

    # Initialize generator
    generator = TestReportGenerator()

    # Check if test results exist
    if not generator.allure_results.exists():
        print("\n⚠️  No test results found!")
        print("Please run tests first: pytest tests/")
        sys.exit(1)

    # Count result files
    result_files = list(generator.allure_results.glob("*-result.json"))
    print(f"\n📊 Found {len(result_files)} test result(s)")

    if len(result_files) == 0:
        print("⚠️  No test results to process")
        sys.exit(1)

    # Generate all formats
    print(f"\n📝 Generating reports with template: {report_template}")
    generator.generate_all_formats(template=report_template)

    # Generate additional formats
    print("\n📄 Generating additional report variants...")

    # Executive summary
    results = generator.parse_allure_results()
    if results:
        exec_content = generator.generate_markdown_report(results, template="executive")
        exec_file = generator.save_markdown_report(exec_content, "executive_summary.md")
        generator.convert_with_pandoc(exec_file, "html")
        generator.convert_with_pandoc(exec_file, "docx")

    # Print summary
    print("\n" + "=" * 60)
    print("✅ Report Generation Complete!")
    print("=" * 60)
    print(f"\n📁 Output locations:")
    print(f"  • Markdown reports: {generator.output_dir}")
    print(f"  • Obsidian vault: {generator.docs_dir}")
    print(f"\n📊 Test Summary:")
    print(f"  • Total tests: {results['total']}")
    print(f"  • Passed: {results['passed']} ✅")
    print(f"  • Failed: {results['failed']} ❌")
    print(f"  • Skipped: {results['skipped']} ⏭️")

    if results['total'] > 0:
        pass_rate = (results['passed'] / results['total']) * 100
        print(f"  • Pass rate: {pass_rate:.1f}%")

        if pass_rate >= 95:
            print("\n🎉 Excellent! All tests passed!")
        elif pass_rate >= 80:
            print("\n✅ Good! Most tests passed.")
        else:
            print("\n⚠️  Warning: Low pass rate detected.")

    print("\n" + "=" * 60)

    # Exit with appropriate code
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()