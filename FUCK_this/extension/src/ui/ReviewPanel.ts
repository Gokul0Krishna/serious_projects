import * as vscode from 'vscode';
import { Issue } from '../api';

export class ReviewPanel {
    private static currentPanel: ReviewPanel | undefined;
    private readonly panel: vscode.WebviewPanel;
    private disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this.panel = panel;
        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);
        this.update();
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (ReviewPanel.currentPanel) {
            ReviewPanel.currentPanel.panel.reveal(column);
            return ReviewPanel.currentPanel;
        }

        const panel = vscode.window.createWebviewPanel(
            'codeReviewResults',
            'Code Review Results',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                localResourceRoots: [extensionUri],
            }
        );

        ReviewPanel.currentPanel = new ReviewPanel(panel, extensionUri);
        return ReviewPanel.currentPanel;
    }

    public displayResults(issues: Issue[], score: number) {
        this.panel.webview.html = this.getWebviewContent(issues, score);
    }

    private update() {
        this.panel.webview.html = this.getLoadingContent();
    }

    private getLoadingContent(): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Code Review</title>
        </head>
        <body>
            <h2>Code Review Results</h2>
            <p>Run a code review to see results here...</p>
        </body>
        </html>`;
    }

    private getWebviewContent(issues: Issue[], score: number): string {
        const issuesByType = this.groupIssuesByType(issues);
        const scoreColor = score >= 8 ? 'green' : score >= 5 ? 'orange' : 'red';

        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Code Review Results</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                }
                .score {
                    font-size: 48px;
                    font-weight: bold;
                    color: ${scoreColor};
                    margin: 20px 0;
                }
                .issue-group {
                    margin: 20px 0;
                }
                .issue {
                    padding: 10px;
                    margin: 10px 0;
                    border-left: 4px solid;
                    background: var(--vscode-editor-background);
                }
                .high { border-color: #f44336; }
                .medium { border-color: #ff9800; }
                .low { border-color: #2196f3; }
                .issue-header {
                    font-weight: bold;
                    margin-bottom: 5px;
                }
                .issue-description {
                    margin: 5px 0;
                }
                .issue-suggestion {
                    color: var(--vscode-textLink-foreground);
                    font-style: italic;
                    margin-top: 5px;
                }
            </style>
        </head>
        <body>
            <h1>Code Review Results</h1>
            <div class="score">Score: ${score.toFixed(1)}/10</div>
            <p><strong>Total Issues:</strong> ${issues.length}</p>
            
            ${Object.entries(issuesByType).map(([type, typeIssues]) => `
                <div class="issue-group">
                    <h2>${this.capitalizeFirst(type)} (${typeIssues.length})</h2>
                    ${typeIssues.map(issue => `
                        <div class="issue ${issue.severity}">
                            <div class="issue-header">
                                Line ${issue.line} - ${this.capitalizeFirst(issue.severity)} Severity
                            </div>
                            <div class="issue-description">${issue.description}</div>
                            <div class="issue-suggestion">💡 ${issue.suggestion}</div>
                        </div>
                    `).join('')}
                </div>
            `).join('')}
            
            ${issues.length === 0 ? '<p style="color: green; font-size: 18px;">✓ No issues found! Great code!</p>' : ''}
        </body>
        </html>`;
    }

    private groupIssuesByType(issues: Issue[]): Record<string, Issue[]> {
        return issues.reduce((acc, issue) => {
            if (!acc[issue.type]) {
                acc[issue.type] = [];
            }
            acc[issue.type].push(issue);
            return acc;
        }, {} as Record<string, Issue[]>);
    }

    private capitalizeFirst(str: string): string {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    public dispose() {
        ReviewPanel.currentPanel = undefined;
        this.panel.dispose();
        while (this.disposables.length) {
            const disposable = this.disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}