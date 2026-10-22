"""
Static SQL Code Analyzer - Main analysis engine
"""
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.static_analyzer.rules import ALL_RULES
from src.llm.ollama_client import OllamaClient


class StaticAnalyzer:
    """Main static analysis engine"""
    
    def __init__(self, use_ai: bool = True):
        self.rules = ALL_RULES
        self.use_ai = use_ai
        if use_ai:
            print("Initializing AI engine...")
            self.llm = OllamaClient(model="deepseek-coder:6.7b")
    
    def analyze_file(self, file_path: str) -> Dict:
        """Analyze a SQL file"""
        print(f"\nReading file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_code = f.read()
        except Exception as e:
            return {
                'error': f"Could not read file: {str(e)}",
                'source': file_path
            }
        
        return self.analyze_code(sql_code, file_path)
    
    def analyze_code(self, sql_code: str, source: str = "inline") -> Dict:
        """Analyze SQL code"""
        
        print(f"Running {len(self.rules)} rules...")
        
        # Run all rules
        violations = []
        for rule in self.rules:
            rule_violations = rule.check(sql_code)
            violations.extend(rule_violations)
        
        print(f"Found {len(violations)} issues")
        
        # Add AI explanations if enabled
        if self.use_ai and violations:
            print(f"Generating AI explanations...")
            
            for i, violation in enumerate(violations, 1):
                if violation['severity'] in ['CRITICAL', 'WARNING']:
                    print(f"   Analyzing issue {i}/{len(violations)}...", end='')
                    try:
                        violation['ai_explanation'] = self.llm.explain_violation(
                            code=violation['code_snippet'],
                            violation=violation
                        )
                        print(" Done")
                    except Exception as e:
                        violation['ai_explanation'] = f"AI explanation unavailable: {str(e)}"
                        print(f" Error: {str(e)}")
        
        # Calculate summary
        result = {
            'source': source,
            'total_violations': len(violations),
            'critical': len([v for v in violations if v['severity'] == 'CRITICAL']),
            'warnings': len([v for v in violations if v['severity'] == 'WARNING']),
            'info': len([v for v in violations if v['severity'] == 'INFO']),
            'violations': violations
        }
        
        return result


# Test if run directly
if __name__ == "__main__":
    print("="*80)
    print("SQL GUARDIAN - Static Analyzer Test")
    print("="*80)
    
    # Create test SQL with issues
    test_sql = """
    CREATE PROCEDURE usp_GetCustomerOrders
    AS
    BEGIN
        SELECT * 
        FROM Orders o WITH (NOLOCK)
        WHERE YEAR(OrderDate) = 2026
            AND CustomerID = @CustomerID
    END
    """
    
    print("\nTest SQL Code:")
    print(test_sql)
    
    # Analyze
    analyzer = StaticAnalyzer(use_ai=True)
    result = analyzer.analyze_code(test_sql, "test_code")
    
    # Print results
    print("\n" + "="*80)
    print("ANALYSIS RESULTS")
    print("="*80)
    print(f"Total Issues: {result['total_violations']}")
    print(f"  - Critical: {result['critical']}")
    print(f"  - Warnings: {result['warnings']}")
    print(f"  - Info: {result['info']}")
    
    if result['violations']:
        for i, v in enumerate(result['violations'], 1):
            print(f"\n{i}. [{v['severity']}] {v['rule_id']}: {v['message']}")
            print(f"   Line: {v['line']}")
            print(f"\n   Code:")
            print(v['code_snippet'])
            
            if 'ai_explanation' in v:
                print(f"\n   AI Explanation:")
                print(f"   {v['ai_explanation']}")
            print()