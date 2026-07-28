import React from 'react';

export default async function Home() {
  let statusText = "Backend Offline";
  try {
    const res = await fetch('http://127.0.0.1:8000/health', { cache: 'no-store' });
    if (res.ok) {
      statusText = "Atlas Platform Running";
    }
  } catch (error) {
    console.error("Failed to fetch health endpoint", error);
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-black text-white">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold tracking-tight text-white sm:text-6xl">
          {statusText}
        </h1>
      </div>
    </main>
  );
}
