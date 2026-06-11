import Link from 'next/link';

const STATS = [
  { label: 'Movies', value: '468+' },
  { label: 'Series', value: '32+' },
  { label: 'YouTube Links', value: '861+' },
  { label: 'Free to Use', value: '100%' },
];

const ENDPOINTS = [
  { method: 'GET', path: '/movies/popular', desc: 'Popular Ethiopian movies' },
  { method: 'GET', path: '/series', desc: 'Ethiopian TV series' },
  { method: 'GET', path: '/search/multi?q=', desc: 'Search across all content' },
  { method: 'GET', path: '/discover', desc: 'Advanced filtering & sorting' },
  { method: 'GET', path: '/trending/movie/week', desc: 'Trending by YouTube views' },
  { method: 'POST', path: '/auth/register', desc: 'Get your free API key' },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-white dark:bg-black text-black dark:text-white">
      {/* Nav */}
      <nav className="border-b border-black/10 dark:border-white/10 px-6 py-4 flex items-center justify-between max-w-6xl mx-auto">
        <span className="font-black text-xl tracking-tight">ETMDB</span>
        <div className="flex items-center gap-6 text-sm">
          <Link href="/docs" className="opacity-60 hover:opacity-100 transition-opacity">Docs</Link>
          <Link href="https://github.com/dawitlabs/etmdb" target="_blank" className="opacity-60 hover:opacity-100 transition-opacity">GitHub</Link>
          <Link
            href="/docs/getting-started"
            className="bg-black dark:bg-white text-white dark:text-black px-4 py-1.5 text-sm font-medium hover:opacity-80 transition-opacity"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-24 pb-20">
        <p className="text-xs font-mono tracking-widest uppercase opacity-40 mb-6">Open API · Free · No key required</p>
        <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-none mb-8 max-w-4xl">
          Ethiopian<br />Movie Database
        </h1>
        <p className="text-xl opacity-60 max-w-2xl mb-12 leading-relaxed">
          A public REST API for Ethiopian and Amharic-language films and series.
          Browse, search, discover, and explore 500+ titles with YouTube links, ratings, and metadata.
        </p>
        <div className="flex flex-wrap gap-4">
          <Link
            href="/docs/getting-started"
            className="bg-black dark:bg-white text-white dark:text-black px-8 py-3 font-semibold hover:opacity-80 transition-opacity"
          >
            Read the Docs
          </Link>
          <Link
            href="https://github.com/dawitlabs/etmdb"
            target="_blank"
            className="border border-black/20 dark:border-white/20 px-8 py-3 font-semibold hover:border-black dark:hover:border-white transition-colors"
          >
            View on GitHub
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="border-t border-b border-black/10 dark:border-white/10">
        <div className="max-w-6xl mx-auto px-6 py-12 grid grid-cols-2 md:grid-cols-4 divide-x divide-black/10 dark:divide-white/10">
          {STATS.map((s) => (
            <div key={s.label} className="px-8 first:pl-0 last:pr-0">
              <div className="text-4xl font-black tracking-tight mb-1">{s.value}</div>
              <div className="text-sm opacity-50">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Quick example */}
      <section className="max-w-6xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-16 items-start">
        <div>
          <h2 className="text-3xl font-black tracking-tight mb-4">No key required</h2>
          <p className="opacity-60 mb-6 leading-relaxed">
            All read endpoints are fully open. Call the API directly — no signup, no credit card, no rate limit for casual use.
          </p>
          <p className="opacity-60 leading-relaxed">
            Register for a free API key to track usage and unlock higher rate limits.
          </p>
        </div>
        <div className="bg-black dark:bg-white/5 text-white dark:text-white p-6 font-mono text-sm leading-relaxed overflow-x-auto">
          <div className="opacity-40 mb-3 text-xs"># No authentication needed</div>
          <div>
            <span className="text-green-400">curl</span>{' '}
            <span className="opacity-70 break-all">https://api.etmdb.dawit.dev/api/v1/movies/popular</span>
          </div>
          <div className="mt-4 opacity-40 text-xs"># Search across all content</div>
          <div>
            <span className="text-green-400">curl</span>{' '}
            <span className="opacity-70 break-all">"https://api.etmdb.dawit.dev/api/v1/search/multi?q=Difret"</span>
          </div>
          <div className="mt-4 opacity-40 text-xs"># Trending this week</div>
          <div>
            <span className="text-green-400">curl</span>{' '}
            <span className="opacity-70 break-all">https://api.etmdb.dawit.dev/api/v1/trending/movie/week</span>
          </div>
        </div>
      </section>

      {/* Endpoints */}
      <section className="border-t border-black/10 dark:border-white/10">
        <div className="max-w-6xl mx-auto px-6 py-20">
          <h2 className="text-3xl font-black tracking-tight mb-12">Endpoints</h2>
          <div className="grid md:grid-cols-2 gap-px bg-black/10 dark:bg-white/10 border border-black/10 dark:border-white/10">
            {ENDPOINTS.map((e) => (
              <div key={e.path} className="bg-white dark:bg-black p-6 flex items-start gap-4">
                <span className={`text-xs font-mono font-bold px-2 py-1 shrink-0 ${e.method === 'POST' ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-black/5 dark:bg-white/10 text-black dark:text-white'}`}>
                  {e.method}
                </span>
                <div>
                  <code className="text-sm font-mono">/api/v1{e.path}</code>
                  <p className="text-sm opacity-50 mt-1">{e.desc}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-8 text-center">
            <Link href="/docs" className="text-sm opacity-50 hover:opacity-100 transition-opacity underline underline-offset-4">
              View full API reference →
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-black/10 dark:border-white/10 px-6 py-8 max-w-6xl mx-auto flex items-center justify-between text-sm opacity-40">
        <span>ETMDB · Ethiopian Movie Database</span>
        <div className="flex gap-6">
          <Link href="https://github.com/dawitlabs/etmdb" target="_blank" className="hover:opacity-100 transition-opacity">GitHub</Link>
          <Link href="/docs" className="hover:opacity-100 transition-opacity">Docs</Link>
        </div>
      </footer>
    </main>
  );
}
