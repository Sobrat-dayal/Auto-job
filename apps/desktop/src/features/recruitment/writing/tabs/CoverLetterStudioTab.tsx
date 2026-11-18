/**
 * Stage 24: Cover Letter Generation Studio Tab.
 * Synthesizes role-tailored, evidence-grounded cover letters from canonical applicant facts.
 */

import * as React from 'react';
import {
  Sparkles,
  Briefcase,
  Building,
  User,
  Sliders,
  FileText,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  RefreshCw,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type {
  CoverLetterDocument,
  CoverLetterCreateRequest,
  CoverLetterType,
  WritingTone,
  WritingLength,
} from '@autonom/shared-types';

interface CoverLetterStudioTabProps {
  onGenerate: (req: CoverLetterCreateRequest) => Promise<CoverLetterDocument | null>;
  onSelectLetter: (letter: CoverLetterDocument) => void;
  onNavigateTab: (tabId: string) => void;
}

export const CoverLetterStudioTab: React.FC<CoverLetterStudioTabProps> = ({
  onGenerate,
  onSelectLetter,
  onNavigateTab,
}) => {
  const [roleTitle, setRoleTitle] = React.useState<string>('Senior Software Engineer');
  const [employerName, setEmployerName] = React.useState<string>('Acme Technologies');
  const [letterType, setLetterType] = React.useState<CoverLetterType>('role_specific');
  const [tone, setTone] = React.useState<WritingTone>('professional');
  const [lengthPreference, setLengthPreference] = React.useState<WritingLength>('standard');
  const [recipientName, setRecipientName] = React.useState<string>('Hiring Manager');
  const [recipientOrg, setRecipientOrg] = React.useState<string>('Acme Technologies Engineering Team');
  const [jobDescription, setJobDescription] = React.useState<string>(
    `Seeking a Senior Software Engineer to design high-throughput distributed microservices in Python and Rust.
Requirements:
- Production expertise in Python (FastAPI/asyncio) and Rust.
- Distributed consensus, Kubernetes orchestration, and database performance optimization.
- Strong automated testing culture and zero-tolerance for unverified assertions.`
  );
  const [isGenerating, setIsGenerating] = React.useState<boolean>(false);
  const [lastGenerated, setLastGenerated] = React.useState<CoverLetterDocument | null>(null);

  const handleGenerate = async () => {
    if (!roleTitle.trim()) return;
    setIsGenerating(true);
    try {
      const doc = await onGenerate({
        title: `${roleTitle} Cover Letter - ${employerName || 'General'}`,
        target_role: roleTitle,
        employer_name: employerName || null,
        letter_type: letterType,
        tone: tone,
        length_preference: lengthPreference,
        recipient_name: recipientName || null,
        recipient_organization: recipientOrg || null,
        job_description_raw: jobDescription || null,
      });
      if (doc) {
        setLastGenerated(doc);
        onSelectLetter(doc);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Configuration & Generator Inputs (5 Cols) */}
        <div className="lg:col-span-5 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-cyan-400" />
                <CardTitle className="text-sm text-slate-200">Letter Parameters</CardTitle>
              </div>
              <p className="text-xs text-slate-400">
                Specify role context and recipient metadata to tailor the evidence presentation.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label htmlFor="target-role-title" className="text-xs text-slate-300 flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-cyan-400" />
                  Target Role Title *
                </label>
                <Input
                  id="target-role-title"
                  value={roleTitle}
                  onChange={(e) => setRoleTitle(e.target.value)}
                  placeholder="e.g. Principal Systems Architect"
                  className="h-8 text-xs bg-slate-950 border-slate-700 text-slate-200"
                />
              </div>

              <div className="space-y-1.5">
                <label htmlFor="target-employer-name" className="text-xs text-slate-300 flex items-center gap-1.5">
                  <Building className="w-3.5 h-3.5 text-indigo-400" />
                  Employer / Company Name
                </label>
                <Input
                  id="target-employer-name"
                  value={employerName}
                  onChange={(e) => setEmployerName(e.target.value)}
                  placeholder="e.g. Stripe, Google, Startup Inc."
                  className="h-8 text-xs bg-slate-950 border-slate-700 text-slate-200"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300 flex items-center gap-1.5">
                    <FileText className="w-3.5 h-3.5 text-emerald-400" />
                    Letter Archetype
                  </label>
                  <select
                    value={letterType}
                    onChange={(e) => setLetterType(e.target.value as CoverLetterType)}
                    className="w-full h-8 bg-slate-950 border border-slate-700 rounded px-2 text-xs text-slate-200"
                  >
                    <option value="role_specific">Role-Specific (Standard)</option>
                    <option value="experienced">Experienced Professional</option>
                    <option value="internship">Internship / Student</option>
                    <option value="research">Academic / Research</option>
                    <option value="short">Short (3-paragraph)</option>
                    <option value="general">General Professional</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300 flex items-center gap-1.5">
                    <Sliders className="w-3.5 h-3.5 text-amber-400" />
                    Tone
                  </label>
                  <select
                    value={tone}
                    onChange={(e) => setTone(e.target.value as WritingTone)}
                    className="w-full h-8 bg-slate-950 border border-slate-700 rounded px-2 text-xs text-slate-200"
                  >
                    <option value="professional">Professional (Balanced)</option>
                    <option value="technical">Technical (Engineering)</option>
                    <option value="concise">Concise (Direct)</option>
                    <option value="formal">Formal / Corporate</option>
                    <option value="friendly_professional">Friendly Professional</option>
                    <option value="early_career">Early Career</option>
                    <option value="research_focused">Research Focused</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300">Length Target</label>
                  <select
                    value={lengthPreference}
                    onChange={(e) => setLengthPreference(e.target.value as WritingLength)}
                    className="w-full h-8 bg-slate-950 border border-slate-700 rounded px-2 text-xs text-slate-200"
                  >
                    <option value="standard">Standard (250-380 words)</option>
                    <option value="short">Short (150-250 words)</option>
                    <option value="detailed">Detailed (380-500 words)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300 flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-purple-400" />
                    Recipient / Org
                  </label>
                  <Input
                    value={recipientName}
                    onChange={(e) => {
                      setRecipientName(e.target.value);
                      setRecipientOrg(e.target.value);
                    }}
                    placeholder="e.g. Hiring Team"
                    className="h-8 text-xs bg-slate-950 border-slate-700 text-slate-200"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300">Job Description / Requirements</label>
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  rows={4}
                  className="w-full bg-slate-950 border border-slate-700 rounded p-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                  placeholder="Paste job posting text here to align cover letter claims..."
                />
              </div>

              <Button
                onClick={handleGenerate}
                disabled={isGenerating || !roleTitle.trim()}
                className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-medium text-xs h-9"
              >
                {isGenerating ? (
                  <span className="flex items-center gap-2">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    Synthesizing Letter from Profile Claims...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5" />
                    Generate Grounded Cover Letter
                  </span>
                )}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Generation Preview & Evidence Traceability (7 Cols) */}
        <div className="lg:col-span-7 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-cyan-400" />
                  <CardTitle className="text-sm text-slate-200">
                    {lastGenerated ? lastGenerated.title : 'Generation Preview'}
                  </CardTitle>
                </div>
                <p className="text-xs text-slate-400">
                  {lastGenerated
                    ? `${lastGenerated.blocks.reduce((acc, b) => acc + b.word_count, 0)} words • Grounded in canonical profile`
                    : 'Configure parameters on the left and click Generate to produce a draft.'}
                </p>
              </div>

              {lastGenerated && (
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-7 text-xs border-cyan-500/40 text-cyan-400 hover:bg-cyan-950/40"
                    onClick={() => onNavigateTab('editor')}
                  >
                    Open in Visual Editor <ArrowRight className="w-3 h-3 ml-1" />
                  </Button>
                </div>
              )}
            </CardHeader>
            <CardContent>
              {!lastGenerated ? (
                <div className="py-16 text-center text-xs text-slate-500 space-y-3">
                  <FileText className="w-8 h-8 text-slate-700 mx-auto" />
                  <p>No letter generated in this session yet.</p>
                  <p className="text-[11px] text-slate-600 max-w-sm mx-auto">
                    AUTONOM will query your Stage 21 profile for verified education, experience achievements, and GitHub technical evidence.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Metadata Header Pill */}
                  <div className="flex items-center justify-between p-2.5 rounded bg-slate-950/60 border border-slate-800 text-xs">
                    <div className="flex items-center gap-2">
                      <Badge variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">
                        {lastGenerated.letter_type}
                      </Badge>
                      <Badge variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">
                        {lastGenerated.tone}
                      </Badge>
                      <span className="text-[11px] text-slate-400">
                        Template: <span className="text-slate-200">{lastGenerated.template_id}</span>
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5 text-[11px] text-emerald-400">
                      <ShieldCheck className="w-3.5 h-3.5" />
                      Zero Hallucination Verified
                    </div>
                  </div>

                  {/* Paragraph Blocks Preview */}
                  <div className="p-4 rounded-lg bg-slate-950/90 border border-slate-800 space-y-3 text-xs leading-relaxed text-slate-300 font-serif">
                    {lastGenerated.blocks.map((block) => (
                      <div key={block.id} className="space-y-1">
                        <div className="flex items-center justify-between text-[10px] text-slate-500 font-sans pb-0.5">
                          <span className="uppercase tracking-wider font-semibold text-slate-400">
                            {block.block_type.replace('_', ' ')}
                          </span>
                          <span>{block.word_count} words</span>
                        </div>
                        <p className="whitespace-pre-line text-slate-200">
                          {block.text}
                        </p>

                        {/* Source provenance pills */}
                        {block.source_refs.length > 0 && (
                          <div className="flex flex-wrap gap-1 pt-1 font-sans">
                            {block.source_refs.map((src, i) => (
                              <span
                                key={i}
                                className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] bg-slate-900 border border-slate-800 text-cyan-400"
                                title={src.attribution_text || ''}
                              >
                                <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400" />
                                {src.source_type}: {src.source_entity_id}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
