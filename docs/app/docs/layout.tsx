import { DocsLayout } from 'fumadocs-ui/layouts/docs';
import type { ReactNode } from 'react';
import { source } from '@/lib/source';
import Link from 'next/link';

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <DocsLayout
      tree={source.pageTree}
      nav={{
        title: (
          <Link href="/" className="font-black text-lg tracking-tight">
            ETMDB
          </Link>
        ),
        transparentMode: 'top',
      }}
      links={[
        {
          text: 'GitHub',
          url: 'https://github.com/dawitlabs/etmdb',
          external: true,
        },
      ]}
    >
      {children}
    </DocsLayout>
  );
}
