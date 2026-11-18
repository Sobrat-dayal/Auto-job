import * as React from 'react';
import {
  Circle,
  Play,
  Square,
  Pause,
  Shield,
  Clock,
  Sparkles,
  Lock,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type { RecordingSession, RecordedAction } from '@autonom/shared-types';

interface RecordingStudioTabProps {
  onCompileProcedure?: (sessionId: string) => void;
}

export const RecordingStudioTab: React.FC<RecordingStudioTabProps> = ({ onCompileProcedure }) => {
  const [activeSession, setActiveSession] = React.useState<RecordingSession | null>(null);
  const [recordingsList, setRecordingsList] = React.useState<RecordingSession[]>([]);
  const [sessionName, setSessionName] = React.useState<string>('Standard Web & Desktop Workflow');
  const [appScopes, setAppScopes] = React.useState<string>('notepad.exe, calc.exe, msedge.exe');
  const [webOrigins, setWebOrigins] = React.useState<string>('https://jobs.example.com, https://linkedin.com');
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [statusMessage, setStatusMessage] = React.useState<string | null>(null);
  const [mockActionInput, setMockActionInput] = React.useState<string>('Search query');

  const fetchRecordings = React.useCallback(async () => {
    try {
      const list = await apiClient.listRecordings(20);
      setRecordingsList(list);
      const active = list.find((s) => s.status === 'active' || s.status === 'paused');
      if (active) {
        const full = await apiClient.getRecording(active.session_id);
        setActiveSession(full);
      }
    } catch (err: any) {
      console.error('Failed to load recordings:', err);
    }
  }, []);

  React.useEffect(() => {
    fetchRecordings();
    const interval = setInterval(fetchRecordings, 4000);
    return () => clearInterval(interval);
  }, [fetchRecordings]);

  const handleStart = async () => {
    setIsLoading(true);
    setStatusMessage(null);
    try {
      const scopes = appScopes.split(',').map((s) => s.trim()).filter(Boolean);
      const origins = webOrigins.split(',').map((s) => s.trim()).filter(Boolean);
      const session = await apiClient.startRecording({
        name: sessionName || 'Action Recording Session',
        allowed_app_scopes: scopes,
        allowed_web_origins: origins,
      });
      setActiveSession(session);
      setStatusMessage(`Started recording session ${session.session_id}`);
      await fetchRecordings();
    } catch (err: any) {
      setStatusMessage(`Error: ${err.message || 'Failed to start recording'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePause = async () => {
    if (!activeSession) return;
    try {
      const updated = await apiClient.pauseRecording(activeSession.session_id);
      setActiveSession(updated);
      setStatusMessage('Recording paused');
    } catch (err: any) {
      setStatusMessage(`Error: ${err.message}`);
    }
  };

  const handleResume = async () => {
    if (!activeSession) return;
    try {
      const updated = await apiClient.resumeRecording(activeSession.session_id);
      setActiveSession(updated);
      setStatusMessage('Recording resumed');
    } catch (err: any) {
      setStatusMessage(`Error: ${err.message}`);
    }
  };

  const handleStop = async () => {
    if (!activeSession) return;
    setIsLoading(true);
    try {
      const stopped = await apiClient.stopRecording(activeSession.session_id);
      setActiveSession(stopped);
      setStatusMessage(`Session sealed with SHA-256 hash: ${stopped.integrity_hash?.slice(0, 16)}...`);
      await fetchRecordings();
    } catch (err: any) {
      setStatusMessage(`Error: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSimulateAction = async (adapter: 'browser' | 'desktop' | 'visual' | 'hybrid', actionType: string) => {
    if (!activeSession || activeSession.status !== 'active') return;
    try {
      const action: Partial<RecordedAction> = {
        source_adapter: adapter,
        action_type: actionType,
        application_name: 'notepad.exe',
        window_title: 'Untitled - Notepad',
        web_origin: 'https://jobs.example.com',
        raw_parameters: { text: mockActionInput, target_name: 'Edit Area', secret_password: 'super_secret_token_123' },
        normalized_parameters: { text: mockActionInput },
        target_locator: { strategy: 'accessibility_id', value: '15' },
      };
      await apiClient.recordAction(activeSession.session_id, action);
      const full = await apiClient.getRecording(activeSession.session_id);
      setActiveSession(full);
      setStatusMessage(`Recorded ${actionType} on ${adapter}`);
    } catch (err: any) {
      setStatusMessage(`Record error: ${err.message}`);
    }
  };

  const isRecording = activeSession?.status === 'active';
  const isPaused = activeSession?.status === 'paused';

  return (
    <div className="space-y-6" data-testid="recording-studio-tab">
      {/* Recording Control Banner */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Circle className={`h-4 w-4 ${isRecording ? 'text-red-500 fill-red-500 animate-pulse' : isPaused ? 'text-amber-500' : 'text-slate-500'}`} />
                Action Recording Studio
                {isRecording && <Badge variant="outline" className="border-red-500/30 bg-red-500/10 text-red-400 font-mono text-[11px]">LIVE RECORDING</Badge>}
                {isPaused && <Badge variant="outline" className="border-amber-500/30 bg-amber-500/10 text-amber-400 font-mono text-[11px]">PAUSED</Badge>}
                {!isRecording && !isPaused && <Badge variant="outline" className="text-slate-400 font-mono text-[11px]">IDLE</Badge>}
              </CardTitle>
              <CardDescription className="text-xs">
                Captures user and agent computer operations across Chromium DOM, Windows UIA, and Visual Grounding with automatic privacy redaction.
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={fetchRecordings}
                className="h-8 gap-1 text-xs"
              >
                <RefreshCw className="h-3 w-3" />
                Refresh
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Configuration Form when idle */}
          {!isRecording && !isPaused && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">Session Name</label>
                <Input
                  value={sessionName}
                  onChange={(e) => setSessionName(e.target.value)}
                  placeholder="e.g. Job Application Pipeline"
                  className="h-8 text-xs bg-slate-900/60"
                  data-testid="recording-name-input"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">Allowed Applications (Process Scope)</label>
                <Input
                  value={appScopes}
                  onChange={(e) => setAppScopes(e.target.value)}
                  placeholder="e.g. notepad.exe, msedge.exe"
                  className="h-8 text-xs bg-slate-900/60"
                />
              </div>
              <div className="space-y-1">
                <label className="text-xs font-medium text-slate-300">Allowed Web Origins (Origin Scope)</label>
                <Input
                  value={webOrigins}
                  onChange={(e) => setWebOrigins(e.target.value)}
                  placeholder="e.g. https://example.com"
                  className="h-8 text-xs bg-slate-900/60"
                />
              </div>
            </div>
          )}

          {/* Action Control Buttons */}
          <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-slate-800">
            {!isRecording && !isPaused ? (
              <Button
                onClick={handleStart}
                disabled={isLoading}
                size="sm"
                className="gap-1.5 bg-red-600 hover:bg-red-700 text-white h-8 text-xs font-medium"
                data-testid="start-recording-btn"
              >
                <Circle className="h-3 w-3 fill-current" />
                Start Recording
              </Button>
            ) : (
              <>
                {isRecording ? (
                  <Button
                    onClick={handlePause}
                    variant="outline"
                    size="sm"
                    className="gap-1.5 h-8 text-xs font-medium border-amber-500/40 text-amber-400 hover:bg-amber-500/10"
                    data-testid="pause-recording-btn"
                  >
                    <Pause className="h-3 w-3" />
                    Pause
                  </Button>
                ) : (
                  <Button
                    onClick={handleResume}
                    variant="outline"
                    size="sm"
                    className="gap-1.5 h-8 text-xs font-medium border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10"
                    data-testid="resume-recording-btn"
                  >
                    <Play className="h-3 w-3" />
                    Resume
                  </Button>
                )}
                <Button
                  onClick={handleStop}
                  disabled={isLoading}
                  variant="destructive"
                  size="sm"
                  className="gap-1.5 h-8 text-xs font-medium"
                  data-testid="stop-recording-btn"
                >
                  <Square className="h-3 w-3 fill-current" />
                  Stop & Seal Recording
                </Button>
              </>
            )}

            {/* Test Action Simulation Controls (when active) */}
            {isRecording && (
              <div className="flex items-center gap-2 ml-auto">
                <Input
                  value={mockActionInput}
                  onChange={(e) => setMockActionInput(e.target.value)}
                  placeholder="Action payload text"
                  className="h-8 text-xs w-40 bg-slate-900/60"
                />
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSimulateAction('desktop', 'type_text')}
                  className="h-8 text-xs"
                >
                  Record UIA Type
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSimulateAction('browser', 'click')}
                  className="h-8 text-xs"
                >
                  Record DOM Click
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSimulateAction('visual', 'click')}
                  className="h-8 text-xs"
                >
                  Record Visual Click
                </Button>
              </div>
            )}
          </div>

          {statusMessage && (
            <div className="text-xs p-2 rounded bg-slate-800/80 border border-slate-700 text-slate-300 font-mono">
              {statusMessage}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Active Session Captured Action Stream */}
      {activeSession && (
        <Card className="border-border/60 bg-card/60">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-sm font-semibold flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-400" />
                  Captured Action Timeline ({activeSession.actions.length} actions)
                </CardTitle>
                <CardDescription className="text-xs">
                  Session ID: <span className="font-mono text-slate-300">{activeSession.session_id}</span>
                  {activeSession.integrity_hash && (
                    <span className="ml-3 font-mono text-emerald-400">
                      SHA-256: {activeSession.integrity_hash.slice(0, 16)}...
                    </span>
                  )}
                </CardDescription>
              </div>
              {activeSession.status === 'stopped' && (
                <Button
                  size="sm"
                  onClick={() => onCompileProcedure?.(activeSession.session_id)}
                  className="gap-1.5 h-8 text-xs bg-blue-600 hover:bg-blue-700 text-white"
                  data-testid="compile-from-session-btn"
                >
                  <Sparkles className="h-3 w-3" />
                  Compile into Procedure
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {activeSession.actions.length === 0 ? (
              <div className="text-center py-8 text-slate-400 text-xs">
                No actions recorded yet in this session. Perform operations or use test simulation buttons.
              </div>
            ) : (
              <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
                {activeSession.actions.map((act) => (
                  <div
                    key={act.action_id}
                    className="flex items-start justify-between gap-3 p-2.5 rounded border border-slate-800 bg-slate-900/50 text-xs"
                    data-testid={`action-row-${act.sequence_number}`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-slate-500 font-semibold w-6">#{act.sequence_number}</span>
                      <Badge variant="outline" className="font-mono text-[10px] uppercase">
                        {act.source_adapter}
                      </Badge>
                      <span className="font-semibold text-slate-200">{act.action_type}</span>
                      {act.application_name && (
                        <span className="text-slate-400 text-[11px] font-mono">
                          [{act.application_name}]
                        </span>
                      )}
                      {act.is_sensitive && (
                        <Badge variant="outline" className="border-amber-500/40 text-amber-400 font-mono text-[10px] flex items-center gap-1">
                          <Lock className="h-2.5 w-2.5" /> Redacted
                        </Badge>
                      )}
                    </div>
                    <div className="text-right">
                      <span className="text-slate-500 text-[11px] font-mono">
                        {new Date(act.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Historical Recording Sessions List */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2">
            <Shield className="h-4 w-4 text-emerald-400" />
            Completed Recording Sessions ({recordingsList.length})
          </CardTitle>
          <CardDescription className="text-xs">
            Sealed sessions ready for parameterized procedure compilation.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {recordingsList.length === 0 ? (
            <div className="text-center py-6 text-slate-400 text-xs">
              No recording sessions found.
            </div>
          ) : (
            <div className="space-y-2">
              {recordingsList.map((rec) => (
                <div
                  key={rec.session_id}
                  className="flex items-center justify-between p-3 rounded border border-slate-800 bg-slate-900/40 text-xs"
                >
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-slate-200">{rec.name}</span>
                      <Badge
                        variant="outline"
                        className={`font-mono text-[10px] uppercase ${
                          rec.status === 'stopped'
                            ? 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10'
                            : 'border-slate-700 text-slate-400'
                        }`}
                      >
                        {rec.status}
                      </Badge>
                      <span className="text-slate-400 text-[11px]">
                        {rec.captured_actions_count} actions
                      </span>
                    </div>
                    <div className="text-slate-500 text-[11px] font-mono">
                      ID: {rec.session_id} • Created: {new Date(rec.created_at).toLocaleString()}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setActiveSession(rec)}
                      className="h-7 text-xs"
                    >
                      View Actions
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => onCompileProcedure?.(rec.session_id)}
                      className="h-7 text-xs gap-1 bg-blue-600 hover:bg-blue-700 text-white"
                    >
                      Compile <ArrowRight className="h-3 w-3" />
                    </Button>
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
