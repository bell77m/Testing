#!/usr/bin/env python3
"""
Calculate Test Metrics from Allure Results
Generates metrics for GitLab CI/CD pipeline
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class TestMetricsCalculator:
    """Calculate and display test execution metrics"""

    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path.cwd()
        self.allure_results = self.project_root / "reports" / "allure-results"
        self.junit_results = self.project_root / "reports" / "junit.xml"

    def parse_allure_results(self) -> Dict:
        """Parse Allure test results"""
        if not self.allure_results.exists():
            print(f"⚠️  No Allure results found at: {self.allure_results}")
            return self._get_empty_metrics()

        metrics = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'broken': 0,
            'total_duration': 0,
            'tests': []
        }

        result_files = list(self.allure_results.glob("*-result.json"))

        if not result_files:
            print(f"⚠️  No test result files found in: {self.allure_results}")
            return self._get_empty_metrics()

        print(f"📊 Found {len(result_files)} test result file(s)")

        for result_file in result_files:
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    metrics['total'] += 1
                    status = data.get('status', 'unknown')

                    if status == 'passed':
                        metrics['passed'] += 1
                    elif status == 'failed':
                        metrics['failed'] += 1
                    elif status == 'skipped':
                        metrics['skipped'] += 1
                    elif status == 'broken':
                        metrics['broken'] += 1

                    # Calculate duration
                    start = data.get('start', 0)
                    stop = data.get('stop', 0)
                    duration = (stop - start) / 1000 if stop > start else 0  # Convert to seconds
                    metrics['total_duration'] += duration

                    metrics['tests'].append({
                        'name': data.get('name', 'Unknown'),
                        'status': status,
                        'duration': duration,
                        'fullName': data.get('fullName', '')
                    })

            except Exception as e:
                print(f"⚠️  Failed to parse {result_file.name}: {e}")

        return metrics

    def _get_empty_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'broken': 0,
            'total_duration': 0,
            'tests': []
        }

    def calculate_pass_rate(self, metrics: Dict) -> float:
        """Calculate test pass rate percentage"""
        total = metrics['total']
        if total == 0:
            return 0.0
        return (metrics['passed'] / total) * 100

    def calculate_avg_duration(self, metrics: Dict) -> float:
        """Calculate average test duration"""
        total = metrics['total']
        if total == 0:
            return 0.0
        return metrics['total_duration'] / total

    def get_slowest_tests(self, metrics: Dict, count: int = 5) -> List[Dict]:
        """Get the slowest tests"""
        sorted_tests = sorted(
            metrics['tests'],
            key=lambda x: x['duration'],
            reverse=True
        )
        return sorted_tests[:count]

    def get_failed_tests(self, metrics: Dict) -> List[Dict]:
        """Get all failed tests"""
        return [t for t in metrics['tests'] if t['status'] == 'failed']

    def print_metrics(self, metrics: Dict):
        """Print formatted metrics to console"""
        total = metrics['total']
        passed = metrics['passed']
        failed = metrics['failed']
        skipped = metrics['skipped']
        pass_rate = self.calculate_pass_rate(metrics)
        avg_duration = self.calculate_avg_duration(metrics)

        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION METRICS")
        print("=" * 60)

        print(f"\n📈 Test Results:")
        print(f"   Total Tests:    {total}")
        print(f"   ✅ Passed:      {passed}")
        print(f"   ❌ Failed:      {failed}")
        print(f"   ⏭️  Skipped:     {skipped}")
        if metrics['broken'] > 0:
            print(f"   🔧 Broken:      {metrics['broken']}")

        print(f"\n📊 Success Metrics:")
        print(f"   Pass Rate:      {pass_rate:.2f}%")
        print(f"   Success Bar:    {'█' * int(pass_rate / 5)}{'░' * (20 - int(pass_rate / 5))} {pass_rate:.1f}%")

        print(f"\n⏱️  Performance:")
        print(f"   Total Duration: {metrics['total_duration']:.2f}s")
        print(f"   Average:        {avg_duration:.2f}s per test")

        # Show slowest tests
        slowest = self.get_slowest_tests(metrics, 3)
        if slowest:
            print(f"\n🐌 Slowest Tests:")
            for i, test in enumerate(slowest, 1):
                print(f"   {i}. {test['name']} ({test['duration']:.2f}s)")

        # Show failed tests
        failed_tests = self.get_failed_tests(metrics)
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"   • {test['name']}")

        # Quality assessment
        print(f"\n🎯 Quality Assessment:")
        if pass_rate == 100:
            print("   ✅ EXCELLENT - All tests passed!")
        elif pass_rate >= 95:
            print("   ✅ GOOD - Minor issues detected")
        elif pass_rate >= 80:
            print("   ⚠️  WARNING - Significant failures")
        else:
            print("   ❌ CRITICAL - Major issues detected")

        print("\n" + "=" * 60)

    def save_metrics_file(self, metrics: Dict, filename: str = "metrics.txt"):
        """Save metrics to file for GitLab CI"""
        filepath = self.project_root / filename

        pass_rate = self.calculate_pass_rate(metrics)
        avg_duration = self.calculate_avg_duration(metrics)

        content = f"""test_total {metrics['total']}
test_passed {metrics['passed']}
test_failed {metrics['failed']}
test_skipped {metrics['skipped']}
test_pass_rate {pass_rate:.2f}
test_avg_duration {avg_duration:.2f}
test_total_duration {metrics['total_duration']:.2f}
"""

        filepath.write_text(content, encoding='utf-8')
        print(f"\n💾 Metrics saved to: {filepath}")

    def create_gitlab_badge_data(self, metrics: Dict) -> Dict:
        """Create data for GitLab badges"""
        pass_rate = self.calculate_pass_rate(metrics)

        # Determine badge color based on pass rate
        if pass_rate >= 95:
            color = "success"
        elif pass_rate >= 80:
            color = "warning"
        else:
            color = "critical"

        return {
            "schemaVersion": 1,
            "label": "tests",
            "message": f"{metrics['passed']}/{metrics['total']} passed",
            "color": color
        }

    def generate_summary_json(self, metrics: Dict, filename: str = "test-summary.json"):
        """Generate JSON summary for CI/CD integrations"""
        filepath = self.project_root / filename

        summary = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total": metrics['total'],
                "passed": metrics['passed'],
                "failed": metrics['failed'],
                "skipped": metrics['skipped'],
                "pass_rate": self.calculate_pass_rate(metrics),
                "total_duration": metrics['total_duration'],
                "avg_duration": self.calculate_avg_duration(metrics)
            },
            "failed_tests": [t['name'] for t in self.get_failed_tests(metrics)],
            "slowest_tests": [
                {"name": t['name'], "duration": t['duration']}
                for t in self.get_slowest_tests(metrics, 5)
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        print(f"💾 Summary JSON saved to: {filepath}")

    def generate_markdown_summary(self, metrics: Dict, filename: str = "test-summary.md"):
        """Generate markdown summary for merge requests"""
        filepath = self.project_root / filename

        pass_rate = self.calculate_pass_rate(metrics)
        avg_duration = self.calculate_avg_duration(metrics)

        # Status emoji
        if pass_rate == 100:
            status_emoji = "✅"
            status_text = "All tests passed"
        elif pass_rate >= 95:
            status_emoji = "✅"
            status_text = "Tests mostly passed"
        elif pass_rate >= 80:
            status_emoji = "⚠️"
            status_text = "Some tests failed"
        else:
            status_emoji = "❌"
            status_text = "Many tests failed"

        content = f"""## {status_emoji} Test Results Summary

**Status:** {status_text}

| Metric | Value |
|--------|-------|
| Total Tests | {metrics['total']} |
| ✅ Passed | {metrics['passed']} |
| ❌ Failed | {metrics['failed']} |
| ⏭️ Skipped | {metrics['skipped']} |
| **Pass Rate** | **{pass_rate:.1f}%** |
| Total Duration | {metrics['total_duration']:.1f}s |
| Avg Duration | {avg_duration:.2f}s |

### Pass Rate Visualization
```
{pass_rate:.1f}% {'█' * int(pass_rate / 5)}{'░' * (20 - int(pass_rate / 5))}
```
"""

        # Add failed tests section
        failed_tests = self.get_failed_tests(metrics)
        if failed_tests:
            content += "\n### ❌ Failed Tests\n\n"
            for test in failed_tests:
                content += f"- `{test['name']}`\n"

        # Add slowest tests
        slowest = self.get_slowest_tests(metrics, 5)
        if slowest:
            content += "\n### 🐌 Slowest Tests\n\n"
            for test in slowest:
                content += f"- `{test['name']}` - {test['duration']:.2f}s\n"

        filepath.write_text(content, encoding='utf-8')
        print(f"💾 Markdown summary saved to: {filepath}")


def main():
    """Main execution"""
    print("\n🚀 Starting Test Metrics Calculation...")

    calculator = TestMetricsCalculator()

    # Parse test results
    metrics = calculator.parse_allure_results()

    if metrics['total'] == 0:
        print("\n⚠️  No tests were executed!")
        print("This might be expected if this stage runs before tests.")

        # Create empty metrics file
        calculator.save_metrics_file(metrics)
        sys.exit(0)

    # Display metrics
    calculator.print_metrics(metrics)

    # Save outputs
    calculator.save_metrics_file(metrics)
    calculator.generate_summary_json(metrics)
    calculator.generate_markdown_summary(metrics)

    # Exit with appropriate code
    if metrics['failed'] > 0:
        print("\n⚠️  Some tests failed - check the report above")
        sys.exit(0)  # Don't fail the metrics job, just report
    else:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()