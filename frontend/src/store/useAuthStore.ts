'use client';

import { create } from 'zustand';
import { devtools, persist, createJSONStorage } from 'zustand/middleware';

interface AuthState {
  token: string | null;
  email: string | null;
  role: string | null;
  setAuth: (auth: { token: string | null; email: string | null; role: string | null }) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set) => ({
        token: null,
        email: null,
        role: null,
        setAuth: (auth) => set(auth),
        clearAuth: () => {
          sessionStorage.removeItem('auth_token');
          set({ token: null, email: null, role: null });
        },
      }),
      {
        name: 'auth-storage',
        storage: createJSONStorage(() => sessionStorage),
      }
    )
  )
);
