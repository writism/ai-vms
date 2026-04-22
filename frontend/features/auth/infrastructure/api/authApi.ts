import { http } from "@/infrastructure/http/httpClient";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  id: string;
  email: string;
  name: string;
  role: string;
}

export const authApi = {
  login: (data: LoginRequest) =>
    http.post<TokenResponse>("/api/auth/login", data),

  me: () => http.get<UserResponse>("/api/auth/me"),
};
