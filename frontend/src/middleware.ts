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

  // Check for session cookie (set by backend with SameSite=None)
  const sessionCookie = request.cookies.get('session')?.value;

  // Check for token in custom header (set by frontend for Bearer-token flow)
  // The frontend sets this header via a request interceptor when using localStorage token
  const bearerToken = request.headers.get('x-auth-token');

  const isAuthenticated = !!(sessionCookie || bearerToken);

  if (!isAuthenticated && isProtectedRoute) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
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
