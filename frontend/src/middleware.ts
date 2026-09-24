import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PROTECTED_ROUTES = [
  '/dashboard',
  '/inbox',
  '/approvals',
  '/audit',
  '/settings',
  '/integrations',
];

const AUTH_ROUTES = ['/login', '/signup'];

export function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;

  const isProtectedRoute = PROTECTED_ROUTES.some(r => pathname.startsWith(r));
  const isAuthRoute = AUTH_ROUTES.some(r => pathname.startsWith(r));

  /**
   * We check for 'auth_indicator' — a lightweight non-httpOnly cookie set on
   * vercel.app by the frontend after a successful login. This cookie is readable
   * by the Next.js edge middleware (unlike the httpOnly 'session' cookie that
   * lives on onrender.com).
   *
   * The actual JWT for backend requests lives in localStorage and is sent as a
   * Bearer token — the middleware does not need to validate it.
   */
  const isAuthenticated = !!request.cookies.get('auth_indicator')?.value;

  if (!isAuthenticated && isProtectedRoute) {
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }

  if (isAuthenticated && isAuthRoute) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$|.*\\.mp4$|.*\\.ico$|auth/callback).*)'],
};
