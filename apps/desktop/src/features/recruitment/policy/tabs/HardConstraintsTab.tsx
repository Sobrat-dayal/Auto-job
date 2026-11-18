import * as React from 'react';
import {
  ShieldAlert,
  OctagonX,
  AlertTriangle,
  Lock,
  Building2,
  CheckCircle2,
  Sliders,
  Layers,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';

export const HardConstraintsTab: React.FC = () => {
  const precedenceLevels = [
    {
      level: 1,
      name: 'Emergency Stop Engaged',
      icon: OctagonX,
      color: 'border-rose-700 bg-rose-950/70 text-rose-300',
      badge: 'PROHIBITED',
      desc: 'Active system kill-switch immediately halts all autonomous discovery, evaluation, and drafting across all agents.',
    },
    {
      level: 2,
      name: 'Security & Auth Invariants',
      icon: Lock,
      color: 'border-red-700 bg-red-950/60 text-red-300',
      badge: 'PROHIBITED',
      desc: 'Enforces system authentication boundaries, DPAPI vault integrity, and user authorization engine constraints.',
    },
    {
      level: 3,
      name: 'Explicit Denials & Revocations',
      icon: ShieldAlert,
      color: 'border-orange-800 bg-orange-950/60 text-orange-300',
      badge: 'PROHIBITED',
      desc: 'Explicit past revocations or administrative denials permanently override standing grants or policy allowances.',
    },
    {
      level: 4,
      name: 'Platform / Source Restrictions',
      icon: Layers,
      color: 'border-amber-800 bg-amber-950/60 text-amber-300',
      badge: 'PROHIBITED',
      desc: 'Untrusted job boards, unauthorized scraping targets, or recruiter spam channels are blocked.',
    },
    {
      level: 5,
      name: 'Sensitive Legal Safeguards',
      icon: AlertTriangle,
      color: 'border-yellow-800 bg-yellow-950/60 text-yellow-300',
      badge: 'NEEDS_REVIEW',
      desc: 'Government security clearance, visa attestations, or non-compete questions require explicit human sign-off.',
    },
    {
      level: 6,
      name: 'Employer Blocklists',
      icon: Building2,
      color: 'border-purple-800 bg-purple-950/60 text-purple-300',
      badge: 'PROHIBITED',
      desc: 'Named current employers, blacklisted competitors, or restricted parent companies are strictly excluded.',
    },
    {
      level: 7,
      name: 'Hard Eligibility Failures',
      icon: OctagonX,
      color: 'border-pink-800 bg-pink-950/60 text-pink-300',
      badge: 'INELIGIBLE',
      desc: 'Missing mandatory educational degrees, insufficient verified work years, or failed work authorization.',
    },
    {
      level: 8,
      name: 'Hard Career Preferences',
      icon: Sliders,
      color: 'border-blue-800 bg-blue-950/60 text-blue-300',
      badge: 'REJECTED',
      desc: 'Compensation below the hard salary floor, disallowed work arrangements (e.g. onsite), or excluded cities.',
    },
    {
      level: 9,
      name: 'Scoped Standing Grants',
      icon: CheckCircle2,
      color: 'border-teal-800 bg-teal-950/60 text-teal-300',
      badge: 'PROCEED_CONDITIONAL',
      desc: 'Explicit preauthorized agent grants permit preparation within daily rate limits without asking per job.',
    },
    {
      level: 10,
      name: 'Soft Preference Scoring',
      icon: CheckCircle2,
      color: 'border-emerald-800 bg-emerald-950/60 text-emerald-300',
      badge: 'PROCEED',
      desc: 'Multi-criteria scoring ranks matching jobs from highest affinity (100.0) down to lowest acceptable.',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">10-Level Precedence Hierarchy & Absolute Vetoes</h3>
        <p className="text-xs text-slate-400">
          The recruitment engine enforces an immutable rule priority ladder. Higher-priority rules decisively override lower-priority allowances.
        </p>
      </div>

      <div className="space-y-2.5">
        {precedenceLevels.map((lvl) => {
          const Icon = lvl.icon;
          return (
            <div
              key={lvl.level}
              className={`p-3 rounded-lg border ${lvl.color} flex items-center justify-between transition-all`}
            >
              <div className="flex items-start gap-3">
                <div className="p-1.5 rounded bg-black/40 border border-white/10 mt-0.5">
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-xs">Level {lvl.level}: {lvl.name}</span>
                  </div>
                  <p className="text-[11px] opacity-80 mt-0.5">{lvl.desc}</p>
                </div>
              </div>
              <Badge variant="neutral" className="text-[10px] font-mono tracking-wider font-bold">
                {lvl.badge}
              </Badge>
            </div>
          );
        })}
      </div>
    </div>
  );
};
