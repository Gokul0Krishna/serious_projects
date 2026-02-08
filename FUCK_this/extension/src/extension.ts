import * as vscode from 'vscode';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function displayReviewResults(data: any, editor: vscode.TextEditor) {
    const diagnostics: vscode.Diagnostic[] = [];

    for (const issue of data.issues) {
        const line = issue.line - 1;
        const range = editor.document.lineAt(line).range;

        const severity = issue.severity === 'high' 
            ? vscode.DiagnosticSeverity.Error
            : issue.severity === 'medium'
            ? vscode.DiagnosticSeverity.Warning
            : vscode.DiagnosticSeverity.Information;

        const diagnostic = new vscode.Diagnostic(
            range,
            `${issue.description}\nSuggestion: ${issue.suggestion}`,
            severity
        );
        diagnostic.source = 'AI Code Review';
        diagnostics.push(diagnostic);
    }
    const collection = vscode.languages.createDiagnosticCollection('aiReview');
    collection.set(editor.document.uri, diagnostics);
}

function formatAnswer(data: any): string {
    let content = `# Answer\n\n${data.answer}\n\n`;
    
    if (data.references && data.references.length > 0) {
        content += `## References\n\n`;
        for (const ref of data.references) {
            content += `- ${ref.file}:${ref.line} (relevance: ${(ref.relevance * 100).toFixed(0)}%)\n`;
        }
    }
    
    return content;
}

export function deactivate() {}

export function activate(context: vscode.ExtensionContext) {
    console.log('Code Review AI extension activated');

    const reviewCommand = vscode.commands.registerCommand(
        'codeReviewAI.reviewCode',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }

            const selection = editor.selection;

            const code = selection.isEmpty
                ? editor.document.getText()
                : editor.document.getText(selection);

            const language = editor.document.languageId;

            await vscode.window.withProgress(
                {
                    location: vscode.ProgressLocation.Notification,
                    title: 'Reviewing code...',
                    cancellable: false
                },
                async () => {
                    try {
                        const response = await axios.post(`${API_BASE}/review`, {
                            code,
                            language
                        });

                        displayReviewResults(response.data, editor);

                    } catch (error) {
                        vscode.window.showErrorMessage(
                            'Failed to review code. Is backend running?'
                        );
                    }
                }
            );
        }
    );
    const askCommand = vscode.commands.registerCommand(
        'codeReviewAI.askQuestion',
        async () => {
            const question = await vscode.window.showInputBox({
                prompt: 'Ask a question about your codebase',
                placeHolder: 'e.g., How does authentication work?'
            });

            if (!question) return;

            try {
                const response = await axios.post(`${API_BASE}/ask`, {
                    question
                });

                const doc = await vscode.workspace.openTextDocument({
                    content: response.data.answer || JSON.stringify(response.data, null, 2),
                    language: 'markdown'
                });

                await vscode.window.showTextDocument(doc);

            } catch (error) {
                vscode.window.showErrorMessage('Failed to get answer');
            }
        }
    );

    context.subscriptions.push(reviewCommand, askCommand);
}
