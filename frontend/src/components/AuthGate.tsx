import React, { useEffect, useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';

const PUBLIC_PATHS = new Set(['/login', '/signup', '/']);
const ADMIN_PATH_PREFIX = '/admin';

type JwtPayload = {
  sub?: string;
  role?: string;
};

const decodeJwtPayload = (token: string): JwtPayload | null => {
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64.padEnd(base64.length + (4 - (base64.length % 4)) % 4, '=');
    const json = atob(padded);
    return JSON.parse(json) as JwtPayload;
  } catch {
    return null;
  }
};

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);
  const { setAuth, token, role } = useAuthStore();

  useEffect(() => {
    // pathname이 없는 초기 시점 방어
    if (!pathname) return;

    // 1. 세션 스토리지에서 토큰 확인 (Zustand persist가 알아서 하지만, 명시적 동기화가 필요할 수 있음)
    // Zustand persist is async by default regarding hydration in some versions, but createJSONStorage with sessionStorage is sync?
    // Let's rely on sessionStorage directly for initial check to prevent flash or use Store's state if hydrated.
    // For simplicity, we sync from sessionStorage manually here to ensure immediate validity check.
    const storedToken = sessionStorage.getItem('auth_token');
    
    // 토큰 디코딩
    const payload = storedToken ? decodeJwtPayload(storedToken) : null;
    const email = payload?.sub ?? null;
    const userRole = payload?.role ?? null;

    // 스토어 업데이트 (값이 다를 때만)
    if (storedToken !== token) {
        setAuth({ token: storedToken, email, role: userRole });
    }

    const currentRole = userRole || role; // 우선순위: 새로 읽은 값 > 기존 값
    const currentToken = storedToken || token;

    // 2. 공개 경로 체크
    if (PUBLIC_PATHS.has(pathname)) {
      setReady(true);
      return;
    }

    // 3. 비로그인 처리
    if (!currentToken) {
      setReady(false);
      router.replace('/login');
      return;
    }

    // 4. 권한 체크 (Admin)
    if (pathname.startsWith(ADMIN_PATH_PREFIX) && currentRole !== 'admin') {
      setReady(false);
      router.replace('/');
      return;
    }

    // 통과
    setReady(true);
  }, [pathname, router, setAuth, token, role]);

  // 준비되지 않았고 공개 경로도 아니라면 렌더링 차단 (NULL 반환)
  // 단, SSR 불일치 방지를 위해 useEffect 이후 ready가 true일 때 렌더링
  // 혹은, 공개 경로는 즉시 렌더링 허용
  if (!ready && !PUBLIC_PATHS.has(pathname || '')) {
    return null;
  }

  return <>{children}</>;
}

// useAuth Hook - 이제 Zustand 스토어를 직접 사용하거나, 
// 기존 컴포넌트 호환성을 위해 여기서 래핑해서 내보낼 수 있음.
export function useAuth() {
  return useAuthStore();
}
