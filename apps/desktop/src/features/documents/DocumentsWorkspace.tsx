import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Files, FileText, Eye } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleDetailPanel,
  ModuleLoadingState,
  ModuleEmptyState,
  ModuleErrorState,
} from '@/components/module';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { apiClient } from '@/lib/api-client';
import type { ArtifactItem } from '@/types/modules';

export const DocumentsWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/documents/docs')) return 'docs';
    if (location.pathname.includes('/documents/spreadsheets')) return 'spreadsheets';
    if (location.pathname.includes('/documents/presentations')) return 'presentations';
    if (location.pathname.includes('/documents/pdfs')) return 'pdfs';
    if (location.pathname.includes('/documents/artifacts')) return 'artifacts';
    return 'workspace';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [searchQuery, setSearchQuery] = React.useState('');
  const [selectedArtifact, setSelectedArtifact] = React.useState<ArtifactItem | null>(null);

  const [artifacts, setArtifacts] = React.useState<ArtifactItem[]>([]);
  const [totalArtifacts, setTotalArtifacts] = React.useState(0);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isRefreshing, setIsRefreshing] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const loadData = React.useCallback(async () => {
    setError(null);
    try {
      const res = await apiClient.listArtifacts();
      setArtifacts(res.items);
      setTotalArtifacts(res.total);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to query artifact records.');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    loadData();
  }, [loadData]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'workspace') navigate('/documents/workspace');
    else navigate(`/documents/${tabId}`);
  };

  const filteredArtifacts = artifacts.filter((item) => {
    const matchesSearch =
      item.storage_path.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.artifact_type.toLowerCase().includes(searchQuery.toLowerCase());

    if (activeTab === 'pdfs') {
      return matchesSearch && item.artifact_type.includes('pdf');
    }
    if (activeTab === 'spreadsheets') {
      return (
        matchesSearch &&
        (item.artifact_type.includes('sheet') || item.artifact_type.includes('csv'))
      );
    }
    if (activeTab === 'presentations') {
      return matchesSearch && item.artifact_type.includes('presentation');
    }
    if (activeTab === 'docs') {
      return (
        matchesSearch &&
        (item.artifact_type.includes('doc') || item.artifact_type.includes('report'))
      );
    }
    return matchesSearch;
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const tabs = [
    { id: 'workspace', label: 'All Artifacts', badge: totalArtifacts },
    { id: 'docs', label: 'Word & Text Docs' },
    { id: 'spreadsheets', label: 'Spreadsheets' },
    { id: 'presentations', label: 'Presentations' },
    { id: 'pdfs', label: 'PDFs & Resumes' },
    { id: 'artifacts', label: 'Task Execution Blobs' },
  ];

  return (
    <ModulePage
      isDetailOpen={!!selectedArtifact}
      detailPanel={
        selectedArtifact ? (
          <ModuleDetailPanel
            title={selectedArtifact.storage_path.split('/').pop() || selectedArtifact.id}
            subtitle={selectedArtifact.artifact_type}
            onClose={() => setSelectedArtifact(null)}
            actions={
              <Badge variant="outline" className="text-xs">
                {selectedArtifact.retention_class}
              </Badge>
            }
          >
            <div className="space-y-5">
              <div className="rounded-lg border border-border/80 bg-background/60 p-3">
                <span className="text-[11px] font-semibold text-muted-foreground uppercase">
                  Storage Path
                </span>
                <p className="mt-1 font-mono text-xs text-foreground break-all">
                  {selectedArtifact.storage_path}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="rounded-lg border border-border/40 bg-background/50 p-2.5">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">
                    File Size
                  </span>
                  <p className="mt-0.5 text-sm font-semibold font-mono text-foreground">
                    {formatFileSize(selectedArtifact.file_size)}
                  </p>
                </div>
                <div className="rounded-lg border border-border/40 bg-background/50 p-2.5">
                  <span className="text-[10px] text-muted-foreground uppercase font-semibold">
                    Retention
                  </span>
                  <p className="mt-0.5 text-sm font-semibold font-mono text-foreground">
                    {selectedArtifact.retention_class}
                  </p>
                </div>
              </div>

              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  SHA-256 Checksum
                </span>
                <p className="mt-1 font-mono text-[11px] text-muted-foreground break-all bg-muted/40 p-2 rounded">
                  {selectedArtifact.checksum}
                </p>
              </div>

              <div className="border-t border-border/40 pt-3 text-[11px] text-muted-foreground font-mono">
                Persisted: {new Date(selectedArtifact.created_at).toLocaleString()}
              </div>
            </div>
          </ModuleDetailPanel>
        ) : null
      }
    >
      <ModuleHeader
        title="Documents & Artifacts Storage"
        description="Encrypted artifact storage, compiled resumes, spreadsheets, and document deliverables."
        icon={Files}
        stageTag="Stage 42 Planned"
        badgeLabel={`${totalArtifacts} Blobs`}
        badgeVariant="outline"
      />

      <ModuleUnavailableState
        moduleName="Autonomous Document, Spreadsheet & Presentation Engine"
        stageTag="Stage 42"
        stageName="Office Suite & Artifact Generation"
        description="Autonomous generation of DOCX, XLSX, PPTX, and LaTeX documents activates in Stage 42. Active SQLite artifact cataloging and cryptographic integrity verification are running below."
        plannedCapabilities={[
          'Evidence-verified PDF resume generation (Stage 31 / 42)',
          'Automated Excel financial & analytical models (Stage 42)',
          'High-impact presentation decks with slide notes (Stage 42)',
          'Cryptographic SHA-256 integrity checks at rest (Active)',
        ]}
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      <ModuleToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder="Filter artifacts by path, filename, or type..."
        onRefresh={() => {
          setIsRefreshing(true);
          loadData();
        }}
        isRefreshing={isRefreshing}
      />

      {error ? (
        <ModuleErrorState
          title="Could not query artifact storage"
          message={error}
          onRetry={loadData}
          isRetrying={isRefreshing}
        />
      ) : isLoading ? (
        <ModuleLoadingState rows={4} layout="table" />
      ) : filteredArtifacts.length === 0 ? (
        <ModuleEmptyState
          icon={Files}
          title="No documents or artifacts found"
          description="When tasks generate resumes, reports, or data sheets, genuine metadata records will be cataloged here."
        />
      ) : (
        <div className="space-y-3">
          {filteredArtifacts.map((art) => (
            <Card
              key={art.id}
              className={`cursor-pointer border border-border/60 bg-card/60 transition-all hover:border-primary/50 hover:bg-card/90 ${
                selectedArtifact?.id === art.id ? 'ring-2 ring-primary border-primary' : ''
              }`}
              onClick={() => setSelectedArtifact(art)}
            >
              <CardContent className="flex flex-col gap-2 p-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-primary/20 bg-primary/10 text-primary">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div className="min-w-0">
                    <h4 className="truncate text-sm font-semibold text-foreground">
                      {art.storage_path.split('/').pop() || art.id}
                    </h4>
                    <p className="truncate text-xs text-muted-foreground font-mono">
                      {art.storage_path}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0 self-end sm:self-center">
                  <Badge variant="neutral" className="text-xs font-mono">
                    {formatFileSize(art.file_size)}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {art.artifact_type}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 gap-1.5 text-xs text-muted-foreground hover:text-foreground"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedArtifact(art);
                    }}
                  >
                    <Eye className="h-3.5 w-3.5" />
                    Inspect
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </ModulePage>
  );
};

export default DocumentsWorkspace;
