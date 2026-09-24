import type { Metadata } from 'next';
import './globals.css';
import NavigationHeader from '@/components/NavigationHeader';

export const metadata: Metadata = {
  title: 'The Semantic Entropy Engine | AI Observatory',
  description: 'Mitigating LLM Hallucinations via RL-Driven Context Optimization for Academic Institution Policies',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-bgBase text-gray-100 min-h-screen relative font-sans antialiased selection:bg-accentTeal selection:text-black">
        {/* Glowing Radial Background Blobs */}
        <div className="fixed top-0 left-1/4 w-96 h-96 bg-teal-500/10 rounded-full filter blur-[120px] pointer-events-none" />
        <div className="fixed bottom-10 right-1/4 w-[500px] h-[500px] bg-indigo-600/10 rounded-full filter blur-[140px] pointer-events-none" />

        <div className="flex flex-col min-h-screen relative z-10">
          <NavigationHeader />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </main>
          <footer className="border-t border-panelBorder py-4 text-center text-xs text-gray-500 font-mono">
            The Semantic Entropy Engine • Capstone Prototype • Academic Policy Domain
          </footer>
        </div>
      </body>
    </html>
  );
}
