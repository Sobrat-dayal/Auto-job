import React, { useEffect, useState } from 'react';
import { getNativeAppInfo, type AppInfo } from '@/services/tauri';
import { apiClient, type BackendVersion } from '@/lib/api-client';
import { Info } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { SettingsSection, SettingsField } from '../components';

export const AboutSettingsPage: React.FC = () => {
  const [appInfo, setAppInfo] = useState<AppInfo | null>(null);
  const [backendVersion, setBackendVersion] = useState<BackendVersion | null>(null);
  const [channel, setChannel] = useState<'stable' | 'beta' | 'dev'>('dev');

  useEffect(() => {
    getNativeAppInfo()
      .then(setAppInfo)
      .catch(() => null);
    apiClient
      .getVersion()
      .then(setBackendVersion)
      .catch(() => null);
  }, []);

  return (
    <div className="space-y-6">
      <SettingsSection
        title="AUTONOM — Autonomous Multi-Agent Assistant"
        description="Desktop application for autonomous job scouting, recruitment management, computer automation, and complex agentic workflows."
      >
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-lg bg-primary/10 border border-primary/20">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-base font-bold text-foreground tracking-tight">
                AUTONOM Desktop Shell
              </span>
              <Badge variant="cyan" className="text-[10px] font-mono">
                v{appInfo?.version || '0.1.0-dev'}
              </Badge>
              <Badge variant="outline" className="text-[10px]">
                Stage 10 Complete
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              Phase 2: Frontend & User Experience final release. Phase 3 (AI Engine & Autonomy)
              begins with Stage 11.
            </p>
          </div>

          <Badge variant="neutral" className="text-xs font-mono py-1 px-3 shrink-0">
            Windows 11 x86_64
          </Badge>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs pt-2">
          <div className="p-3 rounded-lg border border-border/40 bg-card/40 space-y-1">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Native Desktop Host
            </span>
            <div className="font-mono text-foreground">
              Tauri v{appInfo?.tauri_version || '2.0.0'} | Rust 2021 Edition
            </div>
            <p className="text-[11px] text-muted-foreground">
              Windows 11 Webview2 host with native process supervisor and system tray containment.
            </p>
          </div>

          <div className="p-3 rounded-lg border border-border/40 bg-card/40 space-y-1">
            <span className="text-[10px] text-muted-foreground uppercase font-semibold">
              Local Sidecar Service
            </span>
            <div className="font-mono text-foreground">
              FastAPI {backendVersion?.version || '0.1.0'} (
              {backendVersion?.python_version || 'Python 3.12+'})
            </div>
            <p className="text-[11px] text-muted-foreground">
              SQLite WAL database with DPAPI encrypted credential vault and SSE event streaming.
            </p>
          </div>
        </div>
      </SettingsSection>

      <SettingsSection
        title="Application Release Channel & Updates"
        description="Signed auto-update infrastructure is scheduled for Stage 49. Development mode is currently active."
      >
        <SettingsField
          label="Release Update Channel"
          description="Select preferred update stream for future signed desktop releases."
        >
          <select
            value={channel}
            onChange={(e) => setChannel(e.target.value as 'stable' | 'beta' | 'dev')}
            className="h-8 rounded-md border border-input bg-card px-2.5 py-1 text-xs text-foreground focus:outline-hidden focus:ring-1 focus:ring-primary"
            aria-label="Release Update Channel"
          >
            <option value="dev">Development (Stage 01–10 Active Monorepo)</option>
            <option value="beta">Beta / Early Access</option>
            <option value="stable">Stable (Production Releases)</option>
          </select>
        </SettingsField>

        <div className="p-3 rounded-lg bg-card/40 border border-border/30 text-xs text-muted-foreground space-y-1">
          <div className="font-semibold text-foreground flex items-center gap-1.5">
            <Info className="h-3.5 w-3.5 text-cyan" />
            <span>Update Mechanism Attribution (Zero-Fake-Data)</span>
          </div>
          <p className="leading-relaxed">
            Cryptographically signed background updates and Windows MSI installer lifecycle belong
            to <strong>Stage 49</strong>. Current installation is running directly from the local
            development workspace.
          </p>
        </div>
      </SettingsSection>

      <SettingsSection
        title="Open Source Licenses & Architecture"
        description="Core libraries powering the AUTONOM desktop client."
      >
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
          <div className="p-2 rounded bg-card/30 border border-border/30">
            <div className="font-semibold text-foreground">Tauri 2</div>
            <div className="text-[10px] text-muted-foreground">MIT / Apache-2.0</div>
          </div>
          <div className="p-2 rounded bg-card/30 border border-border/30">
            <div className="font-semibold text-foreground">React 18 & Vite</div>
            <div className="text-[10px] text-muted-foreground">MIT License</div>
          </div>
          <div className="p-2 rounded bg-card/30 border border-border/30">
            <div className="font-semibold text-foreground">FastAPI & Pydantic</div>
            <div className="text-[10px] text-muted-foreground">MIT License</div>
          </div>
          <div className="p-2 rounded bg-card/30 border border-border/30">
            <div className="font-semibold text-foreground">SQLite (aiosqlite)</div>
            <div className="text-[10px] text-muted-foreground">Public Domain</div>
          </div>
        </div>
      </SettingsSection>
    </div>
  );
};
