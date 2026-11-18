import * as React from 'react';
import {
  Camera,
  Monitor,
  Play,
  RefreshCw,
  Square,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type {
  CaptureProviderType,
  CaptureSessionResponse,
  DisplayInfo,
} from '@autonom/shared-types';

export const VisualCaptureTab: React.FC = () => {
  const [monitors, setMonitors] = React.useState<DisplayInfo[]>([]);
  const [selectedDisplayIndex, setSelectedDisplayIndex] = React.useState<number>(0);
  const [selectedProvider, setSelectedProvider] = React.useState<CaptureProviderType>('mss');
  const [activeSession, setActiveSession] = React.useState<CaptureSessionResponse | null>(null);
  const [frameData, setFrameData] = React.useState<{
    frame_id: string;
    metadata: any;
    thumbnail_b64: string;
  } | null>(null);
  const [isCapturing, setIsCapturing] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  React.useEffect(() => {
    apiClient.listVisualMonitors().then(setMonitors).catch(console.error);
  }, []);

  const handleCaptureSingle = async () => {
    setIsCapturing(true);
    setErrorMsg(null);
    try {
      const sess = await apiClient.createVisualSession({
        target_type: 'display',
        display_index: selectedDisplayIndex,
        provider: selectedProvider,
      });
      const frame = await apiClient.captureVisualFrame(sess.session_id);
      setFrameData(frame);
      await apiClient.closeVisualSession(sess.session_id);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to capture frame');
    } finally {
      setIsCapturing(false);
    }
  };

  const handleStartSession = async () => {
    try {
      const sess = await apiClient.createVisualSession({
        target_type: 'display',
        display_index: selectedDisplayIndex,
        provider: selectedProvider,
      });
      setActiveSession(sess);
      const frame = await apiClient.captureVisualFrame(sess.session_id);
      setFrameData(frame);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to start session');
    }
  };

  const handleStopSession = async () => {
    if (!activeSession) return;
    try {
      await apiClient.closeVisualSession(activeSession.session_id);
      setActiveSession(null);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to stop session');
    }
  };

  return (
    <div className="space-y-6">
      {/* Capture Controls Card */}
      <Card className="border-border/60 bg-card/40">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Camera className="h-5 w-5 text-cyan-400" />
            Capture Target & Engine Configuration
          </CardTitle>
          <CardDescription className="text-xs">
            Configure multi-monitor physical coordinates, hardware providers, and instant frame acquisition.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Display Monitor</label>
              <select
                value={selectedDisplayIndex}
                onChange={(e) => setSelectedDisplayIndex(Number(e.target.value))}
                className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-xs font-mono shadow-sm focus:outline-none focus:ring-1 focus:ring-cyan-500"
              >
                {monitors.map((m) => (
                  <option key={m.display_index} value={m.display_index}>
                    {m.name || `Display ${m.display_index}`} ({m.width}x{m.height} • Scale: {m.scale_factor}x) {m.is_primary ? '• Primary' : ''}
                  </option>
                ))}
                {monitors.length === 0 && <option value={0}>Display 0 (Default Desktop)</option>}
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Capture Provider</label>
              <select
                value={selectedProvider}
                onChange={(e) => setSelectedProvider(e.target.value as CaptureProviderType)}
                className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-xs font-mono shadow-sm focus:outline-none focus:ring-1 focus:ring-cyan-500"
              >
                <option value="mss">MSS (Fast Multi-Monitor Virtual Screen)</option>
                <option value="gdi">GDI BitBlt / PrintWindow (Win32 Native)</option>
                <option value="wgc">Windows Graphics Capture (Direct3D 11)</option>
              </select>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleCaptureSingle}
                disabled={isCapturing}
                className="flex-1 gap-1.5 bg-cyan-600 hover:bg-cyan-500 text-white text-xs h-9"
              >
                {isCapturing ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Camera className="h-3.5 w-3.5" />}
                Capture Snapshot
              </Button>
              {activeSession ? (
                <Button
                  onClick={handleStopSession}
                  variant="destructive"
                  size="sm"
                  className="gap-1.5 text-xs h-9"
                >
                  <Square className="h-3.5 w-3.5" />
                  Close Session
                </Button>
              ) : (
                <Button
                  onClick={handleStartSession}
                  variant="outline"
                  size="sm"
                  className="gap-1.5 text-xs h-9 border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
                >
                  <Play className="h-3.5 w-3.5" />
                  Open Session
                </Button>
              )}
            </div>
          </div>

          {errorMsg && (
            <div className="mt-3 p-2.5 rounded bg-rose-500/10 border border-rose-500/30 text-xs text-rose-400 font-mono">
              Error: {errorMsg}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Frame Preview Viewport */}
      <Card className="border-border/60 bg-card/40">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-base font-semibold flex items-center gap-2">
              <Monitor className="h-5 w-5 text-emerald-400" />
              Live Visual Frame Viewport
            </CardTitle>
            {frameData && (
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 text-xs font-mono">
                  {frameData.metadata.width}x{frameData.metadata.height}
                </Badge>
                <Badge variant="outline" className="text-xs font-mono text-muted-foreground">
                  Scale: {frameData.metadata.dpi_scale}x
                </Badge>
                <Badge variant="outline" className="text-xs font-mono text-muted-foreground">
                  SHA-256: {frameData.metadata.content_hash.slice(0, 8)}...
                </Badge>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent>
          {frameData ? (
            <div className="rounded-lg border border-border overflow-hidden bg-black/60 flex items-center justify-center p-2">
              <img
                src={`data:image/png;base64,${frameData.thumbnail_b64}`}
                alt="Captured Screen Frame"
                className="max-h-[540px] w-auto object-contain rounded"
              />
            </div>
          ) : (
            <div className="h-64 rounded-lg border border-dashed border-border/80 flex flex-col items-center justify-center text-muted-foreground text-xs space-y-2">
              <Camera className="h-8 w-8 text-muted-foreground/40" />
              <span>No frame captured yet. Click "Capture Snapshot" to acquire an instantaneous screen frame.</span>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
