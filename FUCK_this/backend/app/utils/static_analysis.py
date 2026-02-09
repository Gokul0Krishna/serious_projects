import tempfile
import os
import subprocess
import json
from typing import List, Dict


class Static_analyzer():

    def __init__(self):
        pass

    def analyze_python(self, code: str, file_path: str = "temp.py"):
        issues = []
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.py', 
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            issues.extend(self._run_pylint(temp_path))
            
            issues.extend(self._run_bandit(temp_path))
            
            issues.extend(self._check_complexity(code))
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return issues
    
    def _run_pylint(self, file_path: str) -> List[Dict]:
        issues = []
        
        try:
            result = subprocess.run(
                ['pylint', file_path, '--output-format=json', 
                 '--disable=all', '--enable=E,W,C0103,C0114,C0115,C0116'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                pylint_issues = json.loads(result.stdout)
                
                for item in pylint_issues:
                    severity = "low"
                    if item['type'] == 'error':
                        severity = "high"
                    elif item['type'] == 'warning':
                        severity = "medium"
                    
                    issues.append({
                        "type": "bug" if item['type'] == 'error' else "style",
                        "severity": severity,
                        "line": item['line'],
                        "description": item['message'],
                        "suggestion": f"Fix: {item['symbol']}",
                        "tool": "pylint"
                    })
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return issues
    
    def _run_bandit(self, file_path: str) -> List[Dict]:
        issues = []
        
        try:
            result = subprocess.run(
                ['bandit', '-f', 'json', file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                bandit_data = json.loads(result.stdout)
                
                for item in bandit_data.get('results', []):
                    issues.append({
                        "type": "security",
                        "severity": item['issue_severity'].lower(),
                        "line": item['line_number'],
                        "description": item['issue_text'],
                        "suggestion": "Review security implications",
                        "tool": "bandit"
                    })
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        
        return issues
    
    def _check_complexity(self, code: str) -> List[Dict]:
        issues = []
        
        try:
            from radon.complexity import cc_visit
            
            complexity_results = cc_visit(code)
            
            for item in complexity_results:
                if item.complexity > 10:
                    severity = "medium" if item.complexity < 20 else "high"
                    
                    issues.append({
                        "type": "performance",
                        "severity": severity,
                        "line": item.lineno,
                        "description": f"High complexity ({item.complexity}). "
                                     f"Function '{item.name}' is too complex.",
                        "suggestion": "Break down into smaller functions",
                        "tool": "radon"
                    })
        except ImportError:
            pass
        
        return issues
    
    def analyze_javascript(self, code: str) -> List[Dict]:
        issues = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            if 'console.log' in line:
                issues.append({
                    "type": "style",
                    "severity": "low",
                    "line": i,
                    "description": "console.log() found - remove before production",
                    "suggestion": "Use proper logging library",
                    "tool": "basic-check"
                })
            
            if ' == ' in line and ' === ' not in line:
                issues.append({
                    "type": "bug",
                    "severity": "medium",
                    "line": i,
                    "description": "Use === instead of == for comparison",
                    "suggestion": "Replace == with ===",
                    "tool": "basic-check"
                })
        
        return issues