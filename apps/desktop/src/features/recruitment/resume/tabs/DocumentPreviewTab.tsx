/**
 * Stage 23: Document Preview & Direct Export Tab.
 * Renders realistic printable page sheet with zoom controls and quick DOCX/PDF export triggers.
 */

import * as React from 'react';
import {
  FileText,
  Download,
  ZoomIn,
  ZoomOut,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';
import type { ExportFormat, ResumeDocument } from '@autonom/shared-types';

interface DocumentPreviewTabProps {
  resume: ResumeDocument | null;
  onExport: (format: ExportFormat) => Promise<void>;
  onNavigateTab: (tabId: string) => void;
}

export const DocumentPreviewTab: React.FC<DocumentPreviewTabProps> = ({
  resume,
  onExport,
  onNavigateTab,
}) => {
  const [htmlContent, setHtmlContent] = React.useState<string>('');
  const [zoomLevel, setZoomLevel] = React.useState<number>(100);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);
  const [isExporting, setIsExporting] = React.useState<boolean>(false);

  const fetchPreview = React.useCallback(async () => {
    if (!resume) return;
    setIsLoading(true);
    try {
      const data = await apiClient.getResumePreview(resume.id);
      setHtmlContent(data.html);
    } finally {
      setIsLoading(false);
    }
  }, [resume]);

  React.useEffect(() => {
    fetchPreview();
  }, [fetchPreview]);

  const handleExport = async (format: ExportFormat) => {
    setIsExporting(true);
    try {
      await onExport(format);
      onNavigateTab('exports');
    } finally {
      setIsExporting(false);
    }
  };

  if (!resume) {
    return (
      <Card className="bg-slate-900/60 border-slate-800 text-center py-16">
        <CardContent className="space-y-3">
          <FileText className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-semibold text-slate-300">No Resume Selected</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Select a resume to view its live paginated preview.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Control Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-slate-200">{resume.title}</span>
          <Badge variant="neutral" className="bg-slate-800 text-slate-400 font-mono text-xs">
            {resume.template_id}
          </Badge>
          <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800/60 text-xs">
            {resume.page_format.toUpperCase()}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          {/* Zoom controls */}
          <div className="flex items-center gap-1 bg-slate-950 border border-slate-700 rounded px-1.5 py-0.5 text-xs text-slate-300">
            <button
              onClick={() => setZoomLevel((z) => Math.max(60, z - 10))}
              className="p-1 hover:text-cyan-400"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono px-1 w-10 text-center">{zoomLevel}%</span>
            <button
              onClick={() => setZoomLevel((z) => Math.min(140, z + 10))}
              className="p-1 hover:text-cyan-400"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          <Button
            size="sm"
            variant="outline"
            disabled={isLoading}
            onClick={fetchPreview}
            className="border-slate-700 text-slate-300"
          >
            <RefreshCw className={`w-3.5 h-3.5 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>

          <Button
            size="sm"
            variant="outline"
            disabled={isExporting}
            onClick={() => handleExport('docx')}
            className="border-slate-700 text-slate-300 hover:text-cyan-400"
          >
            <Download className="w-3.5 h-3.5 mr-1.5" />
            Export DOCX
          </Button>

          <Button
            size="sm"
            variant="primary"
            disabled={isExporting}
            onClick={() => handleExport('pdf')}
            className="bg-cyan-600 hover:bg-cyan-500 text-white"
          >
            <Download className="w-3.5 h-3.5 mr-1.5" />
            Export PDF
          </Button>
        </div>
      </div>

      {/* Printable Sheet Canvas */}
      <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-8 flex justify-center overflow-x-auto min-h-[600px]">
        <div
          style={{ transform: `scale(${zoomLevel / 100})`, transformOrigin: 'top center' }}
          className="transition-transform duration-150"
        >
          {/* Virtual Paper Sheet (US Letter / A4) */}
          <div className="w-[794px] min-h-[1123px] bg-white text-slate-900 shadow-2xl p-10 rounded-sm font-sans text-xs leading-normal select-text">
            {htmlContent ? (
              <div
                dangerouslySetInnerHTML={{ __html: htmlContent }}
                className="resume-printable-content"
              />
            ) : (
              <div className="flex items-center justify-center h-96 text-slate-400">
                <RefreshCw className="w-6 h-6 animate-spin mr-2" />
                Rendering printable preview...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

