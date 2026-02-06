from pylint.lint import Run
from pylint.reporters.text import TextReporter #pylint: code analysis tool enforces the PEP 8
import bandit
from bandit.core import manager as bandit_manager #bandit: plication security testing (SAST) tool designed to find common security issues in Python code
from radon.complexity import cc_visit
from radon.metrics import mi_visit # radon: a powerful Python tool used for code analysis and refactoring, calculating metrics 
import tempfile #tempfile: reating temporary files and directories 
import os


class Structure_analyzer():
    def __init__(self):
        pass

    def _pylint_test(self,file_path:str):
        issues = []
        try:
            result = Run([file_path, '--output-format=json'], exit=False)
            for item in result.linter.reporter.messages:
                    issues.append({
                        "type": "style",
                        "severity": "low" if item.symbol.startswith('C') else "medium",
                        "line": item.line,
                        "description": item.msg,
                        "suggestion": "",
                        "tool": "pylint"
                    })
        except:
                pass
        return issues

    def _bandit_test(self,file_path:str):
        issues = []
        b_mgr = bandit_manager.BanditManager(bandit.config.BanditConfig(), 'file')
        b_mgr.discover_files([file_path])
        b_mgr.run_tests()
        
        for issue in b_mgr.results:
            issues.append({
                "type": "security",
                "severity": issue.severity.lower(),
                "line": issue.lineno,
                "description": issue.text,
                "suggestion": "",
                "tool": "bandit"
            })
        return issues
    
    def _check_complexity(self,code:str):
        issues = []
        complexity_results = cc_visit(code)
        for item in complexity_results:
            if item.complexity > 10:  # Threshold
                issues.append({
                    "type": "performance",
                    "severity": "medium" if item.complexity < 20 else "high",
                    "line": item.lineno,
                    "description": f"High complexity ({item.complexity}). Consider refactoring.",
                    "suggestion": "Break down into smaller functions",
                    "tool": "radon"
                })
        return issues
    
    def analyze_python(self, code: str, file_path: str = "temp.py"):
        issues = []
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
            
        try:
            issues.extend(self._pylint_test(temp_path))

            issues.extend(self._bandit_test(temp_path))

            complexity = self._check_complexity(code)
            if complexity:
                issues.extend(complexity)

        finally:
            os.unlink(temp_path)
        
        return issues
    
if __name__ == '__main__':
    pass