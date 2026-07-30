/**
 * src/app/api/[...path]/route.ts
 *
 * Server-side proxy to the FastAPI backend.
 *
 * Why this exists:
 * - Next.js rewrites (/api/:path*) strip trailing slashes from the captured path,
 *   causing FastAPI to emit 307 Temporary Redirects.
 * - Browsers drop the Authorization header when following 307 redirects
 *   (Fetch spec §4.4: headers are not re-sent across redirects for sensitive headers).
 * - This Route Handler intercepts ALL /api/* requests, reads every header from the
 *   incoming browser request (including Authorization), and forwards them verbatim
 *   to FastAPI — including the correct trailing slash — without letting the browser
 *   see any redirect.
 */

import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL = "http://localhost:8000";

async function handler(req: NextRequest): Promise<NextResponse> {
  // Reconstruct the backend URL from the request URL.
  // req.nextUrl.pathname = /api/organizations/  →  strip /api prefix  →  /organizations/
  const apiPrefix = "/api";
  const backendPath = req.nextUrl.pathname.slice(apiPrefix.length);
  const search = req.nextUrl.search ?? "";
  const targetUrl = `${BACKEND_URL}${backendPath}${search}`;

  // Forward all incoming headers verbatim.
  // This preserves Authorization: Bearer <token> set by the browser-side request().
  const forwardHeaders: Record<string, string> = {};
  req.headers.forEach((value, key) => {
    // Skip hop-by-hop headers that must not be forwarded.
    const skip = ["host", "connection", "transfer-encoding", "keep-alive", "upgrade"];
    if (!skip.includes(key.toLowerCase())) {
      forwardHeaders[key] = value;
    }
  });

  // Read the body for mutating methods.
  let body: BodyInit | undefined;
  if (!["GET", "HEAD"].includes(req.method)) {
    body = await req.arrayBuffer();
  }

  // Forward the request to FastAPI.
  // redirect: "follow" because we are server-side and will re-emit the body.
  const backendRes = await fetch(targetUrl, {
    method: req.method,
    headers: forwardHeaders,
    body,
    // Do NOT follow redirects — return them so we can re-issue the request
    // with Authorization preserved.
    redirect: "manual",
  });

  // If FastAPI issued a redirect (307/308/301/302), follow it ourselves
  // on the server side, preserving Authorization.
  if (
    backendRes.status === 307 ||
    backendRes.status === 308 ||
    backendRes.status === 301 ||
    backendRes.status === 302
  ) {
    const location = backendRes.headers.get("location");
    if (location) {
      // Resolve relative Location against the backend base URL.
      const redirectTarget = location.startsWith("http")
        ? location
        : `${BACKEND_URL}${location}`;

      // Re-issue the request to the redirected URL WITH Authorization.
      const redirectRes = await fetch(redirectTarget, {
        method: req.method,
        headers: forwardHeaders,
        body,
        redirect: "manual",
      });

      const responseBody = await redirectRes.arrayBuffer();
      return new NextResponse(responseBody, {
        status: redirectRes.status,
        headers: Object.fromEntries(redirectRes.headers.entries()),
      });
    }
  }

  // Normal (non-redirect) response: return it as-is.
  const responseBody = await backendRes.arrayBuffer();
  return new NextResponse(responseBody, {
    status: backendRes.status,
    headers: Object.fromEntries(backendRes.headers.entries()),
  });
}

export const GET = handler;
export const POST = handler;
export const PUT = handler;
export const PATCH = handler;
export const DELETE = handler;
export const OPTIONS = handler;
export const HEAD = handler;
