'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Cpu, FileText, BarChart3, Database } from 'lucide-react';

export default function NavigationHeader() {
  const pathname = usePathname();

  const navItems = [
    { name: 'Observatory Console', href: '/', icon: Cpu },
    { name: 'Policy Ingestion', href: '/ingest', icon: Database },
    { name: 'Analytics & Benchmarks', href: '/analytics', icon: BarChart3 },
  ];

  return (
    <header className="border-b border-panelBorder bg-bgBase/80 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-9 h-9 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-accentTeal group-hover:shadow-[0_0_15px_rgba(20,184,166,0.4)] transition-all">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h1 className="font-heading font-bold text-lg text-white leading-none tracking-tight">
              SEMANTIC ENTROPY <span className="text-accentTeal">ENGINE</span>
            </h1>
            <p className="text-[10px] font-mono text-gray-400 mt-0.5">
              RL-Driven Context Optimization
            </p>
          </div>
        </Link>

        <nav className="flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-teal-500/10 text-accentTeal border border-teal-500/30 shadow-[0_0_10px_rgba(20,184,166,0.15)]'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
