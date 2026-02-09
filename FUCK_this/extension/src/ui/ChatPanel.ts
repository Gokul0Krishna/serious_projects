import * as vscode from 'vscode';
import { QuestionResponse } from '../api';

export class ChatPanel {
    private static currentPanel: ChatPanel | undefined;
    private readonly panel: vscode.WebviewPanel;
    private disposables: vscode.Disposable[] = [];
    private conversationHistory: Array<{question: string, answer: string}> = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this.panel = panel;
        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);
        this.panel.webview.onDidReceiveMessage(
            message => {
                if (message.command === 'newQuestion') {
                    vscode.commands.executeCommand('codeReviewAI.askQuestion');
                }
            },
            null,
            this.disposables
        );
        
        this.update();
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (ChatPanel.currentPanel) {
            ChatPanel.currentPanel.panel.reveal(column);
            return ChatPanel.currentPanel;
        }

        const panel = vscode.window.createWebviewPanel(
            'codebaseChat',
            'Codebase Q&A',
            column || vscode.ViewColumn.Two,
            {
                enableScripts: true,
                localResourceRoots: [extensionUri],
            }
        );

        ChatPanel.currentPanel = new ChatPanel(panel, extensionUri);
        return ChatPanel.currentPanel;
    }

    public addAnswer(question: string, response: QuestionResponse) {
        this.conversationHistory.push({
            question,
            answer: response.answer
        });
        this.update();
    }

    private update() {
        this.panel.webview.html = this.getWebviewContent();
    }

    private getWebviewContent(): string {
        return `<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Codebase Q&A</title>
            <style>
                body {
                    font-family: var(--vscode-font-family);
                    padding: 20px;
                    color: var(--vscode-foreground);
                }
                .conversation {
                    max-width: 800px;
                    margin: 0 auto;
                }
                .message {
                    margin: 20px 0;
                    padding: 15px;
                    border-radius: 5px;
                }
                .question {
                    background: var(--vscode-input-background);
                    border-left: 4px solid var(--vscode-textLink-foreground);
                }
                .answer {
                    background: var(--vscode-editor-background);
                    border-left: 4px solid #4caf50;
                }
                .label {
                    font-weight: bold;
                    margin-bottom: 10px;
                    font-size: 12px;
                    text-transform: uppercase;
                    color: var(--vscode-descriptionForeground);
                }
                .new-question-btn {
                    background: var(--vscode-button-background);
                    color: var(--vscode-button-foreground);
                    border: none;
                    padding: 10px 20px;
                    border-radius: 3px;
                    cursor: pointer;
                    font-size: 14px;
                    margin: 20px 0;
                }
                .new-question-btn:hover {
                    background: var(--vscode-button-hoverBackground);
                }
                .empty-state {
                    text-align: center;
                    padding: 60px 20px;
                    color: var(--vscode-descriptionForeground);
                }
            </style>
        </head>
        <body>
            <div class="conversation">
                <h1>Codebase Q&A</h1>
                
                <button class="new-question-btn" onclick="askNewQuestion()">
                    Ask New Question
                </button>
                
                ${this.conversationHistory.length === 0 ? `
                    <div class="empty-state">
                        <h2>No questions yet</h2>
                        <p>Click "Ask New Question" to start chatting with your codebase</p>
                    </div>
                ` : this.conversationHistory.map(item => `
                    <div class="message question">
                        <div class="label">You asked:</div>
                        <div>${item.question}</div>
                    </div>
                    <div class="message answer">
                        <div class="label">Answer:</div>
                        <div>${this.formatAnswer(item.answer)}</div>
                    </div>
                `).join('')}
            </div>
            
            <script>
                const vscode = acquireVsCodeApi();
                
                function askNewQuestion() {
                    vscode.postMessage({ command: 'newQuestion' });
                }
            </script>
        </body>
        </html>`;
    }
    private formatAnswer(answer: string): string {
        return answer
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }
    public dispose() {
        ChatPanel.currentPanel = undefined;
        this.panel.dispose();
        while (this.disposables.length) {
            const disposable = this.disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }
}