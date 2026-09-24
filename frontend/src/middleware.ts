import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Middleware: Minimal — only redirects authenticated users away from auth pages.
 *
 * Route PROTECTION for /dashboard etc. is handled client-side by the
 * dashboard layout (see AuthContext + ProtectedRoute). We do NOT try to
 * validate sessions here because the Next.js edge runtime cannot access
 * localStorage (where the JWT lives) and the httpOnly backend cookie is
 * scoped to onrender.com, not vercel.app.
 *
 * Security is enforced server-side: every backend API endpoint independently
 * validates the Bearer token. The frontend redirect is UX-only.
 */
export function middleware(request: NextRequest) {
  // No blocking redirects — let all pages load.
  // The dashboard layout handles unauthenticated redirects client-side.
  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|.*\\.png$|.*\\.mp4$|.*\\.ico$).*)'],
};
