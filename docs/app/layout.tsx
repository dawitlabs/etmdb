import { RootProvider } from 'fumadocs-ui/provider';
import { Archivo } from 'next/font/google';
import type { ReactNode } from 'react';
import './globals.css';

const archivo = Archivo({ subsets: ['latin'], variable: '--font-sans' });

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className={archivo.variable} suppressHydrationWarning>
      <body className="flex min-h-screen flex-col">
        <RootProvider>{children}</RootProvider>
      </body>
    </html>
  );
}

export const metadata = {
  title: { default: 'ETMDB — Ethiopian Movie Database API', template: '%s · ETMDB' },
  description: 'Open REST API for Ethiopian and Amharic-language films and series.',
};
