/**
 * Stage 21: Applicant Evidence Library Tab.
 * Verifiable document provenance, cryptographic SHA-256 fingerprints, and claim linkage.
 */

import * as React from 'react';
import { FileCheck, Upload, Trash2, ShieldCheck, FileText, Hash, Calendar } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { EvidenceMetadata } from '@autonom/shared-types';

interface ApplicantEvidenceTabProps {
  evidenceList: EvidenceMetadata[];
  onUpload: (file: File, documentType: string, tags: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  isProcessing: boolean;
}

export const ApplicantEvidenceTab: React.FC<ApplicantEvidenceTabProps> = ({
  evidenceList,
  onUpload,
  onDelete,
  isProcessing,
}) => {
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [docType, setDocType] = React.useState<string>('resume');
  const [tags, setTags] = React.useState<string>('official, primary');
  const [isUploading, setIsUploading] = React.useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      await onUpload(selectedFile, docType, tags);
      setSelectedFile(null);
    } finally {
      setIsUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Authoritative Evidence Library</h3>
          <p className="text-sm text-muted-foreground">
            Cryptographically fingerprinted source documents (PDF, DOCX, TXT) establishing claim provenance.
          </p>
        </div>
      </div>

      {/* Upload Evidence Card */}
      <Card className="border-dashed border-2">
        <CardHeader>
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Upload className="h-4 w-4 text-primary" />
            Upload Verified Source Document
          </CardTitle>
          <CardDescription>
            Documents are digested with SHA-256 and stored in the local secure artifact vault.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleUploadSubmit} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-3">
              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Select Document File *
                </label>
                <Input
                  required
                  type="file"
                  accept=".pdf,.docx,.txt,.json,.md"
                  onChange={handleFileChange}
                  className="mt-1"
                />
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Document Type
                </label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="mt-1 flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  <option value="resume">Resume / CV</option>
                  <option value="transcript">Official Transcript</option>
                  <option value="certificate">Certification Certificate</option>
                  <option value="recommendation">Recommendation Letter</option>
                  <option value="portfolio">Portfolio Export</option>
                  <option value="other">Other Supporting Proof</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  Document Tags (Comma separated)
                </label>
                <Input
                  value={tags}
                  onChange={(e) => setTags(e.target.value)}
                  placeholder="e.g. 2026, tech-focus, verified"
                  className="mt-1"
                />
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <Button type="submit" disabled={!selectedFile || isUploading || isProcessing}>
                <ShieldCheck className="mr-2 h-4 w-4" />
                {isUploading ? 'Computing SHA-256 & Uploading...' : 'Digest & Store Evidence'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Evidence Files Table/List */}
      {evidenceList.length === 0 ? (
        <Card className="flex flex-col items-center justify-center p-8 text-center text-muted-foreground">
          <FileCheck className="mb-2 h-10 w-10 text-muted-foreground" />
          <p className="font-medium text-foreground">No Evidence Documents Attached</p>
          <p className="text-xs text-muted-foreground mt-1 max-w-sm">
            Upload PDF or DOCX resumes to extract claims and prove credentials with cryptographic verification.
          </p>
        </Card>
      ) : (
        <div className="space-y-3">
          {evidenceList.map((doc) => (
            <Card key={doc.id} className="relative overflow-hidden">
              <CardContent className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <FileText className="h-4 w-4 text-primary" />
                    <span className="font-semibold text-sm">{doc.filename}</span>
                    <Badge variant="outline" className="text-[10px] capitalize">
                      {doc.document_type}
                    </Badge>
                    <span className="text-xs text-muted-foreground">({formatFileSize(doc.file_size_bytes)})</span>
                  </div>

                  <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground pt-1">
                    <div className="flex items-center gap-1 font-mono text-[11px] bg-muted px-2 py-0.5 rounded">
                      <Hash className="h-3 w-3 text-primary" />
                      <span>SHA-256: {doc.content_hash_sha256.substring(0, 16)}...</span>
                    </div>

                    <div className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      <span>{new Date(doc.uploaded_at).toLocaleString()}</span>
                    </div>

                    {doc.linked_claims && doc.linked_claims.length > 0 && (
                      <span className="text-emerald-600 font-medium flex items-center gap-1">
                        <ShieldCheck className="h-3 w-3" /> {doc.linked_claims.length} claims linked
                      </span>
                    )}
                  </div>

                  {doc.tags && doc.tags.length > 0 && (
                    <div className="flex gap-1 pt-1.5">
                      {doc.tags.map((t, idx) => (
                        <span key={idx} className="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.2 rounded">
                          #{t}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete(doc.id)}
                  disabled={isProcessing}
                  className="text-destructive hover:bg-destructive/10 self-end md:self-center"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
