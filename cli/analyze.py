#!/usr/bin/env python3
"""
SQL Guardian CLI - Analyze SQL files from command line
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.static_analyzer.analyzer import StaticAnalyzer


def print_banner():
    """Print fancy banner"""
    print("=" * 80)
    print("                    SQL GUARDIAN - Code Analysis")
    print("=" * 80)


def print_summary(result):
    """Print analysis summary"""
    print("\n" + "=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Source: {result['source']}")
    print(f"Total Issues: {result['total_violations']}")
    print(f"  - Critical: {result['critical']}")
    print(f"  - Warnings: {result['warnings']}")
    print(f"  - Info: {result['info']}")
    print("=" * 80)


def print_violations(violations, show_ai=True):
    """Print detailed violation report"""
    if not violations:
        print("\n✅ No issues found! Your SQL code looks great!\n")
        return
    
    print("\n📋 ISSUES FOUND:\n")
    
    for i, v in enumerate(violations, 1):
        # Severity emoji
        emoji = {
            'CRITICAL': '🔴',
            'WARNING': '⚠️',
            'INFO': 'ℹ️'
        }.get(v['severity'], '•')
        
        print(f"{emoji} Issue #{i}: [{v['severity']}] {v['rule_id']}")
        print(f"   {v['message']}")
        print(f"   Line: {v['line']}")
        print(f"\n   Code Context:")
        print(f"   {'-' * 70}")
        for line in str(v['code_snippet']).split('\n'):
            print(f"   {line}")
        print(f"   {'-' * 70}")
        
        if show_ai and 'ai_explanation' in v:
            print(f"\n   🤖 AI Analysis:")
            print(f"   {'-' * 70}")
            for line in v['ai_explanation'].split('\n'):
                print(f"   {line}")
            print(f"   {'-' * 70}")
        
        print()


def main():
    parser = argparse.ArgumentParser(
        description='SQL Guardian - Static SQL Code Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/analyze.py myfile.sql
  python cli/analyze.py myfile.sql --no-ai
  python cli/analyze.py myfile.sql --quiet
        """
    )
    
    parser.add_argument('file', help='SQL file to analyze')
    parser.add_argument('--no-ai', action='store_true', 
                       help='Skip AI explanations (faster)')
    parser.add_argument('--quiet', action='store_true',
                       help='Only show summary, no details')
    
    args = parser.parse_args()
    
    # Check file exists
    if not Path(args.file).exists():
        print(f"❌ Error: File not found: {args.file}")
        sys.exit(1)
    
    # Print banner
    print_banner()
    
    # Initialize analyzer
    analyzer = StaticAnalyzer(use_ai=not args.no_ai)
    
    # Analyze file
    result = analyzer.analyze_file(args.file)
    
    # Check for errors
    if 'error' in result:
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)
    
    # Print results
    print_summary(result)
    
    if not args.quiet:
        print_violations(result['violations'], show_ai=not args.no_ai)
    
    # Exit code based on severity
    if result['critical'] > 0:
        sys.exit(2)  # Critical issues found
    elif result['warnings'] > 0:
        sys.exit(1)  # Warnings found
    else:
        sys.exit(0)  # All clear


if __name__ == '__main__':
    main()