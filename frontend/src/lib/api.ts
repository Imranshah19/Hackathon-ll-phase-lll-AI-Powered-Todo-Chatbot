/**
 * API Client for backend communication.
 *
 * Handles all HTTP requests with automatic JWT token injection.
 */

import Cookies from "js-cookie";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Cookie configuration
const TOKEN_COOKIE = "access_token";
const COOKIE_OPTIONS = {
  secure: process.env.NODE_ENV === "production",
  sameSite: "strict" as const,
  expires: 1, // 1 day
};

// =============================================================================
// Token Management
// =============================================================================

export function getToken(): string | undefined {
  return Cookies.get(TOKEN_COOKIE);
}

export function setToken(token: string): void {
  Cookies.set(TOKEN_COOKIE, token, COOKIE_OPTIONS);
}

export function removeToken(): void {
  Cookies.remove(TOKEN_COOKIE);
}

// =============================================================================
// API Types
// =============================================================================

export interface User {
  id: string;
  email: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface TaskCreateRequest {
  title: string;
  description?: string;
  is_completed?: boolean;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  is_completed?: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterResponse {
  user: User;
  access_token: string;
  token_type: string;
}

export interface ApiError {
  detail: string;
  errors?: Array<{
    field: string;
    message: string;
    type: string;
  }>;
}

// =============================================================================
// API Client
// =============================================================================

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getHeaders(includeAuth = true): HeadersInit {
    const headers: HeadersInit = {
      "Content-Type": "application/json",
    };

    if (includeAuth) {
      const token = getToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    includeAuth = true
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(includeAuth),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        detail: `Request failed with status ${response.status}`,
      }));
      throw new ApiClientError(response.status, error);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    return response.json();
  }

  // ---------------------------------------------------------------------------
  // Auth Endpoints
  // ---------------------------------------------------------------------------

  async register(data: RegisterRequest): Promise<RegisterResponse> {
    const response = await this.request<RegisterResponse>(
      "/api/auth/register",
      {
        method: "POST",
        body: JSON.stringify(data),
      },
      false
    );
    setToken(response.access_token);
    return response;
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await this.request<TokenResponse>(
      "/api/auth/login",
      {
        method: "POST",
        body: JSON.stringify(data),
      },
      false
    );
    setToken(response.access_token);
    return response;
  }

  async getMe(): Promise<User> {
    return this.request<User>("/api/auth/me");
  }

  logout(): void {
    removeToken();
  }

  // ---------------------------------------------------------------------------
  // Task Endpoints
  // ---------------------------------------------------------------------------

  async getTasks(completed?: boolean): Promise<Task[]> {
    const params = completed !== undefined ? `?completed=${completed}` : "";
    return this.request<Task[]>(`/api/tasks${params}`);
  }

  async getTask(id: string): Promise<Task> {
    return this.request<Task>(`/api/tasks/${id}`);
  }

  async createTask(data: TaskCreateRequest): Promise<Task> {
    return this.request<Task>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTask(id: string, data: TaskUpdateRequest): Promise<Task> {
    return this.request<Task>(`/api/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }

  async deleteTask(id: string): Promise<void> {
    return this.request<void>(`/api/tasks/${id}`, {
      method: "DELETE",
    });
  }
}

// =============================================================================
// Error Handling
// =============================================================================

export class ApiClientError extends Error {
  status: number;
  error: ApiError;

  constructor(status: number, error: ApiError) {
    super(error.detail);
    this.name = "ApiClientError";
    this.status = status;
    this.error = error;
  }
}

// =============================================================================
// Export
// =============================================================================

export const api = new ApiClient(API_BASE_URL);
