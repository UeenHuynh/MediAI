import { create } from "zustand";
import { persist } from "zustand/middleware";
import apiClient from "@/lib/api-client";

interface User {
    username: string;
    email?: string;
    full_name?: string;
    role?: string;
}

interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;

    login: (username: string, password: string) => Promise<boolean>;
    logout: () => void;
    refreshUser: () => Promise<void>;
    clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,

            login: async (username: string, password: string) => {
                set({ isLoading: true, error: null });

                try {
                    // OAuth2 password flow uses form data
                    const formData = new URLSearchParams();
                    formData.append("username", username);
                    formData.append("password", password);

                    const response = await apiClient.post("/auth/login", formData, {
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                    });

                    const { access_token, refresh_token } = response.data;

                    localStorage.setItem("access_token", access_token);
                    localStorage.setItem("refresh_token", refresh_token);

                    // Get user info
                    const userResponse = await apiClient.get("/auth/me");
                    const user = userResponse.data;

                    set({
                        user,
                        isAuthenticated: true,
                        isLoading: false,
                    });

                    return true;
                } catch (error: any) {
                    const message =
                        error.response?.data?.detail || "Login failed. Please try again.";
                    set({
                        error: message,
                        isLoading: false,
                        isAuthenticated: false,
                    });
                    return false;
                }
            },

            logout: () => {
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                set({
                    user: null,
                    isAuthenticated: false,
                    error: null,
                });
            },

            refreshUser: async () => {
                try {
                    const response = await apiClient.get("/auth/me");
                    set({ user: response.data, isAuthenticated: true });
                } catch {
                    set({ user: null, isAuthenticated: false });
                }
            },

            clearError: () => set({ error: null }),
        }),
        {
            name: "auth-storage",
            partialize: (state) => ({
                user: state.user,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
);
