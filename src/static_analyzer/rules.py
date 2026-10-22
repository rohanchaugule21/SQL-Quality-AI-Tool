"""
SQL Analysis Rules - Detects common T-SQL issues
"""
import re
from typing import List, Dict


class SQLRule:
    """Base class for SQL rules"""
    
    def __init__(self, rule_id: str, severity: str, message: str):
        self.rule_id = rule_id
        self.severity = severity  # CRITICAL, WARNING, INFO
        self.message = message
    
    def check(self, sql_code: str) -> List[Dict]:
        """Check if rule is violated. Return list of violations."""
        raise NotImplementedError
    
    def _find_line_number(self, sql_code: str, pattern: str) -> int:
        """Find line number of pattern match"""
        lines = sql_code.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                return i
        return 0
    
    def _extract_snippet(self, sql_code: str, pattern: str, context_lines: int = 2) -> str:
        """Extract code snippet around the violation"""
        lines = sql_code.split('\n')
        for i, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                snippet_lines = lines[start:end]
                # Add line numbers
                numbered = [f"{start+j+1:4d} | {l}" for j, l in enumerate(snippet_lines)]
                return '\n'.join(numbered)
        return ""


class SelectStarRule(SQLRule):
    """Detect SELECT * usage"""
    
    def __init__(self):
        super().__init__(
            rule_id="SQL001",
            severity="WARNING",
            message="Avoid SELECT * - specify columns explicitly"
        )
    
    def check(self, sql_code: str) -> List[Dict]:
        violations = []
        pattern = r'\bSELECT\s+\*'
        
        if re.search(pattern, sql_code, re.IGNORECASE):
            violations.append({
                'rule_id': self.rule_id,
                'severity': self.severity,
                'message': self.message,
                'line': self._find_line_number(sql_code, pattern),
                'code_snippet': self._extract_snippet(sql_code, pattern)
            })
        
        return violations


class NoCountRule(SQLRule):
    """Detect missing SET NOCOUNT ON in stored procedures"""
    
    def __init__(self):
        super().__init__(
            rule_id="SQL002",
            severity="INFO",
            message="Add SET NOCOUNT ON at the start of stored procedures"
        )
    
    def check(self, sql_code: str) -> List[Dict]:
        violations = []
        
        # Check if it's a stored procedure
        if re.search(r'\bCREATE\s+PROCEDURE\b', sql_code, re.IGNORECASE):
            # Check if SET NOCOUNT ON is missing
            if not re.search(r'\bSET\s+NOCOUNT\s+ON\b', sql_code, re.IGNORECASE):
                violations.append({
                    'rule_id': self.rule_id,
                    'severity': self.severity,
                    'message': self.message,
                    'line': 1,
                    'code_snippet': sql_code.split('\n')[0:5]  # First 5 lines
                })
        
        return violations


class NonSargableRule(SQLRule):
    """Detect non-sargable predicates (functions in WHERE clause)"""
    
    def __init__(self):
        super().__init__(
            rule_id="SQL003",
            severity="WARNING",
            message="Non-sargable predicate prevents index usage"
        )
    
    def check(self, sql_code: str) -> List[Dict]:
        violations = []
        
        # Common non-sargable patterns
        patterns = [
            (r'\bWHERE\s+YEAR\s*\(', 'YEAR() function in WHERE'),
            (r'\bWHERE\s+MONTH\s*\(', 'MONTH() function in WHERE'),
            (r'\bWHERE\s+DATEPART\s*\(', 'DATEPART() function in WHERE'),
            (r'\bWHERE\s+LEFT\s*\(', 'LEFT() function in WHERE'),
            (r'\bWHERE\s+SUBSTRING\s*\(', 'SUBSTRING() function in WHERE'),
            (r'\bWHERE\s+UPPER\s*\(', 'UPPER() function in WHERE'),
            (r'\bWHERE\s+LOWER\s*\(', 'LOWER() function in WHERE'),
        ]
        
        for pattern, description in patterns:
            if re.search(pattern, sql_code, re.IGNORECASE):
                violations.append({
                    'rule_id': self.rule_id,
                    'severity': self.severity,
                    'message': f"{self.message}: {description}",
                    'line': self._find_line_number(sql_code, pattern),
                    'code_snippet': self._extract_snippet(sql_code, pattern)
                })
        
        return violations


class CursorRule(SQLRule):
    """Detect cursor usage"""
    
    def __init__(self):
        super().__init__(
            rule_id="SQL004",
            severity="WARNING",
            message="Cursor detected - consider set-based alternative"
        )
    
    def check(self, sql_code: str) -> List[Dict]:
        violations = []
        pattern = r'\bDECLARE\s+\w+\s+CURSOR\b'
        
        if re.search(pattern, sql_code, re.IGNORECASE):
            violations.append({
                'rule_id': self.rule_id,
                'severity': self.severity,
                'message': self.message,
                'line': self._find_line_number(sql_code, pattern),
                'code_snippet': self._extract_snippet(sql_code, pattern, context_lines=3)
            })
        
        return violations


class NOLOCKRule(SQLRule):
    """Detect NOLOCK hint usage"""
    
    def __init__(self):
        super().__init__(
            rule_id="SQL005",
            severity="WARNING",
            message="NOLOCK can cause dirty reads - ensure this is acceptable"
        )
    
    def check(self, sql_code: str) -> List[Dict]:
        violations = []
        pattern = r'\bWITH\s*\(\s*NOLOCK\s*\)'
        
        if re.search(pattern, sql_code, re.IGNORECASE):
            violations.append({
                'rule_id': self.rule_id,
                'severity': self.severity,
                'message': self.message,
                'line': self._find_line_number(sql_code, pattern),
                'code_snippet': self._extract_snippet(sql_code, pattern)
            })
        
        return violations


# Rule Registry - Add all rules here
ALL_RULES = [
    SelectStarRule(),
    NoCountRule(),
    NonSargableRule(),
    CursorRule(),
    NOLOCKRule(),
]