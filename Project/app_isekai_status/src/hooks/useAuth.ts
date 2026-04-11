import { useState } from 'react';

const ALLOWED_EMAIL = import.meta.env.VITE_ALLOWED_EMAIL as string;

interface AuthState {
  isAuthenticated: boolean;
  error?: string;
}

export function useAuth() {
  const [auth, setAuth] = useState<AuthState>({ isAuthenticated: false });

  const handleLogin = async (accessToken: string) => {
    try {
      const res = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const user = await res.json();

      if (user.email === ALLOWED_EMAIL) {
        setAuth({ isAuthenticated: true });
      } else {
        setAuth({ isAuthenticated: false, error: `このアカウント（${user.email}）はアクセスできません` });
      }
    } catch {
      setAuth({ isAuthenticated: false, error: '認証エラーが発生しました' });
    }
  };

  return { auth, handleLogin };
}
