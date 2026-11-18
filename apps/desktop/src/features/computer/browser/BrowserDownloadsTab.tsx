import * as React from 'react';
import {
  FolderDown,
  FileCheck,
  HardDrive,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { BrowserDownloadResponse } from '@autonom/shared-types';

interface BrowserDownloadsTabProps {
  downloads: BrowserDownloadResponse[];
  onRefresh: () => void;
  isLoading: boolean;
}

export const BrowserDownloadsTab: React.FC<BrowserDownloadsTabProps> = ({
  downloads,
  onRefresh,
  isLoading,
}) => {
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  return (
    <div className="space-y-6">
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <FolderDown className="h-4 w-4 text-primary" />
                Browser Downloads & Artifact Interceptor
              </CardTitle>
              <CardDescription className="text-xs">
                Files downloaded during autonomous web workflows with cryptographic SHA-256 verification.
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={onRefresh}
              disabled={isLoading}
              className="gap-1.5 text-xs h-8"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {downloads.length === 0 ? (
            <div className="py-12 text-center text-muted-foreground">
              <FolderDown className="h-10 w-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm font-medium">No downloaded files recorded</p>
              <p className="text-xs mt-1">
                Any resumes, job descriptions, or documents downloaded will appear here.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {downloads.map((d) => (
                <div
                  key={d.id}
                  className="p-3.5 rounded-lg border border-border/40 bg-background/40 hover:bg-background/80 transition-colors space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <FileCheck className="h-4 w-4 text-emerald-400" />
                      <span className="font-semibold text-xs text-foreground">
                        {d.suggested_filename}
                      </span>
                      <Badge variant="outline" className="font-mono text-[10px]">
                        {formatBytes(d.file_size_bytes)}
                      </Badge>
                      <Badge
                        variant={d.status === 'completed' ? 'success' : 'neutral'}
                        className="text-[10px] uppercase font-mono"
                      >
                        {d.status}
                      </Badge>
                    </div>
                    <span className="text-[10px] text-muted-foreground font-mono">
                      {new Date(d.created_at).toLocaleTimeString()}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-2 text-xs font-mono text-muted-foreground pt-1">
                    <div className="flex items-center gap-1.5 truncate max-w-lg">
                      <HardDrive className="h-3 w-3 text-primary flex-shrink-0" />
                      <span className="truncate">{d.destination_path}</span>
                    </div>

                    {d.sha256_checksum && (
                      <div className="flex items-center gap-1.5 bg-emerald-500/10 text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20 text-[10px]">
                        <ShieldCheck className="h-3 w-3" />
                        <span>SHA-256: {d.sha256_checksum.slice(0, 16)}...</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
