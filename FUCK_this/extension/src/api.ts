import axios, { AxiosInstance } from 'axios';

export interface CodeReviewRequest {
    code: string;
    language: string;
    file_path?: string;
}

export interface Issue {
    type: string;
    severity: string;
    line: number;
    description: string;
    suggestion: string;
    tool?: string;
}

export interface CodeReviewResponse {
    issues: Issue[];
    total_issues: number;
    score: number;
}

export interface DocumentationRequest {
    code: string;
    doc_type: string;
    style: string;
}

export interface DocumentationResponse {
    documentation: string;
    doc_type: string;
}

export interface QuestionRequest {
    question: string;
    context?: string;
}

export interface Reference {
    file: string;
    line: number;
    code: string;
    relevance: number;
}

export interface QuestionResponse {
    answer: string;
    references: Reference[];
}

export class APIClient {
    private client: AxiosInstance;

    constructor(baseURL: string = 'http://localhost:8000') {
        this.client = axios.create({
            baseURL,
            timeout: 30000,
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }

    async reviewCode(request: CodeReviewRequest): Promise<CodeReviewResponse> {
        const response = await this.client.post('/review', request);
        return response.data;
    }

    async generateDocumentation(request: DocumentationRequest): Promise<DocumentationResponse> {
        const response = await this.client.post('/generate-docs', request);
        return response.data;
    }

    async askQuestion(request: QuestionRequest): Promise<QuestionResponse> {
        const response = await this.client.post('/ask', request);
        return response.data;
    }

    async indexProject(projectPath: string, fileExtensions: string[]): Promise<any> {
        const response = await this.client.post('/index', {
            project_path: projectPath,
            file_extensions: fileExtensions,
        });
        return response.data;
    }

    async checkHealth(): Promise<any> {
        const response = await this.client.get('/health');
        return response.data;
    }
}
