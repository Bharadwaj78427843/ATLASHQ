/**
 * src/app/(auth)/layout.tsx
 * Centered card layout for login and register pages.
 */
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="auth-shell">
      <div className="auth-card">{children}</div>
    </div>
  );
}
