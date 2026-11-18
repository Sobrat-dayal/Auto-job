import * as React from 'react';
import {
  CheckCircle2,
  Crosshair,
  Eye,
  Layers,
  MousePointer,
  RefreshCw,
  Search,
  Sparkles,
  Type,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { apiClient } from '@/lib/api-client';
import type {
  OCRResult,
  VisualElementDetection,
  VisualGroundingResult,
} from '@autonom/shared-types';

export const VisualGroundingTab: React.FC = () => {
  const [query, setQuery] = React.useState('');
  const [frameData, setFrameData] = React.useState<{
    frame_id: string;
    metadata: any;
    thumbnail_b64: string;
  } | null>(null);
  const [elements, setElements] = React.useState<VisualElementDetection[]>([]);
  const [ocrResult, setOcrResult] = React.useState<OCRResult | null>(null);
  const [groundingResult, setGroundingResult] = React.useState<VisualGroundingResult | null>(null);
  const [selectedElement, setSelectedElement] = React.useState<VisualElementDetection | null>(null);
  const [isProcessing, setIsProcessing] = React.useState(false);
  const [clickStatus, setClickStatus] = React.useState<string | null>(null);

  const handleScanScreen = async () => {
    setIsProcessing(true);
    setClickStatus(null);
    try {
      const sess = await apiClient.createVisualSession({ display_index: 0 });
      const [frame, detectedElements, ocr] = await Promise.all([
        apiClient.captureVisualFrame(sess.session_id),
        apiClient.detectVisualElements(sess.session_id),
        apiClient.runVisualOCR(sess.session_id),
      ]);
      setFrameData(frame);
      setElements(detectedElements);
      setOcrResult(ocr);
      await apiClient.closeVisualSession(sess.session_id);
    } catch (err) {
      console.error('Screen scan failed:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleGroundQuery = async () => {
    if (!query.trim()) return;
    setIsProcessing(true);
    setClickStatus(null);
    try {
      const sess = await apiClient.createVisualSession({ display_index: 0 });
      const [frame, groundRes] = await Promise.all([
        apiClient.captureVisualFrame(sess.session_id),
        apiClient.groundVisualQuery(sess.session_id, query.trim()),
      ]);
      setFrameData(frame);
      setGroundingResult(groundRes);
      await apiClient.closeVisualSession(sess.session_id);
    } catch (err) {
      console.error('Grounding failed:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClickPoint = async (x: number, y: number) => {
    try {
      const sess = await apiClient.createVisualSession({ display_index: 0 });
      const res = await apiClient.quickVisualClick(sess.session_id, x, y);
      setClickStatus(`Clicked (${x}, ${y}) - Verification: ${res.verification_status}`);
      await apiClient.closeVisualSession(sess.session_id);
    } catch (err: any) {
      setClickStatus(`Click error: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search & Actions Bar */}
      <Card className="border-border/60 bg-card/40">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Eye className="h-5 w-5 text-emerald-400" />
            Visual Grounding & Semantic Element Resolution
          </CardTitle>
          <CardDescription className="text-xs">
            Query the active screen using natural language or text. The engine runs offline WinRT OCR and visual heuristics to resolve exact desktop coordinates.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Query element (e.g. 'Start button', 'Save', 'Search field', 'OK', 'Cancel')..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleGroundQuery()}
                className="pl-9 font-mono text-sm"
              />
            </div>
            <Button
              onClick={handleGroundQuery}
              disabled={isProcessing || !query.trim()}
              className="gap-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs"
            >
              {isProcessing ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Crosshair className="h-4 w-4" />}
              Ground Query
            </Button>
            <Button
              onClick={handleScanScreen}
              disabled={isProcessing}
              variant="outline"
              className="gap-2 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 text-xs"
            >
              <Sparkles className="h-4 w-4" />
              Scan All Elements & OCR
            </Button>
          </div>

          {groundingResult && (
            <div className="p-3 rounded border border-emerald-500/30 bg-emerald-500/5 flex items-center justify-between">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className={groundingResult.success ? 'border-emerald-500/40 text-emerald-400' : 'border-rose-500/40 text-rose-400'}>
                    {groundingResult.success ? 'Matched' : 'Not Found'}
                  </Badge>
                  <span className="text-xs font-mono font-medium">{groundingResult.explanation}</span>
                </div>
                {groundingResult.target_point && (
                  <p className="text-[11px] text-muted-foreground font-mono">
                    Target Point: ({groundingResult.target_point.x}, {groundingResult.target_point.y}) • Confidence: {(groundingResult.confidence * 100).toFixed(1)}%
                  </p>
                )}
              </div>
              {groundingResult.target_point && (
                <Button
                  size="sm"
                  onClick={() => handleClickPoint(groundingResult.target_point!.x, groundingResult.target_point!.y)}
                  className="gap-1.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs"
                >
                  <MousePointer className="h-3.5 w-3.5" />
                  Click ({groundingResult.target_point.x}, {groundingResult.target_point.y})
                </Button>
              )}
            </div>
          )}

          {clickStatus && (
            <div className="p-2.5 rounded bg-card border border-border text-xs font-mono text-cyan-400 flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4" />
              <span>{clickStatus}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Main Grounding Canvas & Detected Elements Sidebar */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Visual Canvas with Overlay */}
        <Card className="lg:col-span-3 border-border/60 bg-card/40">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Layers className="h-4 w-4 text-cyan-400" />
                Screen Bounding Box Overlay
              </CardTitle>
              {frameData && (
                <div className="flex items-center gap-2 text-[11px] text-muted-foreground font-mono">
                  <span>{frameData.metadata.width}x{frameData.metadata.height}</span>
                  <span>•</span>
                  <span>{elements.length} Elements</span>
                  <span>•</span>
                  <span>{ocrResult?.lines.length ?? 0} OCR Lines</span>
                </div>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {frameData ? (
              <div className="relative rounded-lg border border-border overflow-hidden bg-black/70 flex items-center justify-center p-1">
                <img
                  src={`data:image/png;base64,${frameData.thumbnail_b64}`}
                  alt="Visual Screen Canvas"
                  className="max-h-[500px] w-auto object-contain rounded"
                />

                {/* Grounded Target Highlight Ring */}
                {groundingResult?.target_point && frameData.metadata.width > 0 && (
                  <div
                    style={{
                      position: 'absolute',
                      left: `${(groundingResult.target_point.x / frameData.metadata.width) * 100}%`,
                      top: `${(groundingResult.target_point.y / frameData.metadata.height) * 100}%`,
                      transform: 'translate(-50%, -50%)',
                    }}
                    className="w-8 h-8 rounded-full border-2 border-emerald-400 bg-emerald-400/20 animate-ping pointer-events-none"
                  />
                )}
              </div>
            ) : (
              <div className="h-72 rounded-lg border border-dashed border-border/80 flex flex-col items-center justify-center text-muted-foreground text-xs space-y-2">
                <Eye className="h-8 w-8 text-muted-foreground/40" />
                <span>Click "Scan All Elements & OCR" or "Ground Query" to visualize UI elements on screen.</span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Elements / OCR Inspector Panel */}
        <Card className="border-border/60 bg-card/40 flex flex-col h-[580px]">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Type className="h-4 w-4 text-emerald-400" />
              Detected Controls ({elements.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto space-y-2 text-xs font-mono">
            {elements.length === 0 && (
              <div className="text-center text-muted-foreground py-8">
                No elements detected yet.
              </div>
            )}
            {elements.map((el, i) => (
              <div
                key={i}
                onClick={() => setSelectedElement(el)}
                className={`p-2 rounded border cursor-pointer transition-colors ${
                  selectedElement === el
                    ? 'border-emerald-500 bg-emerald-500/10'
                    : 'border-border/60 hover:bg-card/80'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <Badge variant="outline" className="text-[10px] uppercase font-mono">
                    {el.category}
                  </Badge>
                  <span className="text-[10px] text-muted-foreground">
                    ({el.bounding_box.left}, {el.bounding_box.top})
                  </span>
                </div>
                <div className="text-foreground truncate font-sans text-xs">
                  {el.label || '<unlabeled control>'}
                </div>
                <div className="text-[10px] text-muted-foreground mt-1 flex justify-between">
                  <span>{el.bounding_box.width}x{el.bounding_box.height}px</span>
                  <span>Conf: {(el.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
