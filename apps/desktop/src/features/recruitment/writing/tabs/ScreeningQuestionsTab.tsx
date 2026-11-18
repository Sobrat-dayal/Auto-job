/**
 * Stage 24: Application Screening Question Intelligence Tab.
 * Ingests application questions, categorizes them, and generates truthful, grounded responses.
 */

import * as React from 'react';
import {
  HelpCircle,
  Sparkles,
  CheckCircle2,
  ShieldAlert,
  RefreshCw,
  Edit2,
} from 'lucide-react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type {
  ApplicationQuestionSet,
  QuestionSetCreateRequest,
} from '@autonom/shared-types';

interface ScreeningQuestionsTabProps {
  questionSets: ApplicationQuestionSet[];
  selectedSet: ApplicationQuestionSet | null;
  onSelectSet: (set: ApplicationQuestionSet) => void;
  onCreateSet: (req: QuestionSetCreateRequest) => Promise<ApplicationQuestionSet | null>;
  onGenerateAnswers: (setId: string) => Promise<void>;
  onUpdateAnswer: (setId: string, questionId: string, answerText: string) => Promise<void>;
  onNavigateTab: (tabId: string) => void;
}

export const ScreeningQuestionsTab: React.FC<ScreeningQuestionsTabProps> = ({
  questionSets,
  selectedSet,
  onSelectSet,
  onCreateSet,
  onGenerateAnswers,
  onUpdateAnswer,
  onNavigateTab,
}) => {
  const [isCreating, setIsCreating] = React.useState<boolean>(false);
  const [newTitle, setNewTitle] = React.useState<string>('Engineering Application Questions');
  const [jobTitle, setJobTitle] = React.useState<string>('Senior Software Engineer');
  const [employer, setEmployer] = React.useState<string>('Acme Technologies');
  const [rawQuestionsText, setRawQuestionsText] = React.useState<string>(
    `1. How many years of experience do you have with Python and FastAPI?
2. Describe a time you resolved a major production outage under pressure.
3. Are you legally authorized to work in the United States without sponsorship?
4. What is your desired annual base compensation range?
5. Why are you interested in joining our engineering team?`
  );
  const [isGenerating, setIsGenerating] = React.useState<boolean>(false);
  const [editingQuestionId, setEditingQuestionId] = React.useState<string | null>(null);
  const [editText, setEditText] = React.useState<string>('');

  const handleCreateSet = async () => {
    if (!jobTitle.trim() || !rawQuestionsText.trim()) return;
    setIsCreating(true);
    try {
      const questionsList = rawQuestionsText
        .split('\n')
        .map((line) => line.replace(/^\d+[\.\)]\s*/, '').trim())
        .filter(Boolean)
        .map((q) => ({
          question_text: q,
          is_required: true,
        }));

      const created = await onCreateSet({
        title: newTitle || `${jobTitle} Questions`,
        job_title: jobTitle,
        employer: employer || null,
        raw_text: rawQuestionsText,
        questions: questionsList,
      });

      if (created) {
        onSelectSet(created);
        setRawQuestionsText('');
      }
    } finally {
      setIsCreating(false);
    }
  };

  const handleGenerate = async () => {
    if (!selectedSet) return;
    setIsGenerating(true);
    try {
      await onGenerateAnswers(selectedSet.id);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveEdit = async (questionId: string) => {
    if (!selectedSet) return;
    await onUpdateAnswer(selectedSet.id, questionId, editText);
    setEditingQuestionId(null);
  };

  const getCategoryBadge = (cat: string) => {
    switch (cat) {
      case 'experience':
        return <Badge variant="neutral" className="bg-blue-950/60 text-blue-400 border-blue-800/60 text-[10px]">Experience</Badge>;
      case 'behavioral':
        return <Badge variant="neutral" className="bg-purple-950/60 text-purple-400 border-purple-800/60 text-[10px]">Behavioral</Badge>;
      case 'technical':
        return <Badge variant="neutral" className="bg-cyan-950/60 text-cyan-400 border-cyan-800/60 text-[10px]">Technical</Badge>;
      case 'work_eligibility':
        return <Badge variant="neutral" className="bg-emerald-950/60 text-emerald-400 border-emerald-800/60 text-[10px]">Work Eligibility</Badge>;
      case 'compensation':
        return <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 border-amber-800/60 text-[10px]">Compensation</Badge>;
      case 'motivation':
        return <Badge variant="neutral" className="bg-indigo-950/60 text-indigo-400 border-indigo-800/60 text-[10px]">Motivation</Badge>;
      default:
        return <Badge variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">{cat}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Sets Selector & Importer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Question Ingestion / Set Creator (4 Cols) */}
        <div className="lg:col-span-4 space-y-4">
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <HelpCircle className="w-4 h-4 text-indigo-400" />
                <CardTitle className="text-sm text-slate-200">Import Question Set</CardTitle>
              </div>
              <p className="text-xs text-slate-400">
                Paste questions from application portals or job postings.
              </p>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-1.5">
                <label className="text-xs text-slate-300">Set Title</label>
                <Input
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  placeholder="e.g. Stripe Application Screening"
                  className="h-8 text-xs bg-slate-950 border-slate-700 text-slate-200"
                />
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300">Role</label>
                  <Input
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    placeholder="e.g. Systems Engineer"
                    className="h-8 text-xs bg-slate-950 border-slate-700 text-slate-200"
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs text-slate-300">Company</label>
                  <Input
                    value={employer}
                    onChange={(e) => setEmployer(e.target.value)}
                    placeholder="e.g. Acme Inc"
                    className="h-8 text-xs bg-slate-950 border-slate-700 text-slate-200"
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-slate-300">Raw Questions (One per line)</label>
                <textarea
                  value={rawQuestionsText}
                  onChange={(e) => setRawQuestionsText(e.target.value)}
                  rows={6}
                  className="w-full bg-slate-950 border border-slate-700 rounded p-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
                  placeholder="Paste questions here..."
                />
              </div>

              <Button
                onClick={handleCreateSet}
                disabled={isCreating || !rawQuestionsText.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs h-8"
              >
                {isCreating ? 'Parsing & Classifying...' : 'Create Question Set'}
              </Button>
            </CardContent>
          </Card>

          {/* Question Sets List */}
          <Card className="bg-slate-900/60 border-slate-800">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs text-slate-300">Saved Question Sets</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 p-2">
              {questionSets.length === 0 ? (
                <div className="text-center py-4 text-xs text-slate-500">
                  No question sets created yet.
                </div>
              ) : (
                questionSets.map((qs) => {
                  const isSelected = selectedSet?.id === qs.id;
                  return (
                    <div
                      key={qs.id}
                      onClick={() => onSelectSet(qs)}
                      className={`p-2.5 rounded text-xs cursor-pointer border transition-all ${
                        isSelected
                          ? 'bg-slate-950 border-indigo-500/80 text-slate-100 ring-1 ring-indigo-500/20'
                          : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                      }`}
                    >
                      <div className="font-semibold text-slate-200 truncate">{qs.title}</div>
                      <div className="flex items-center justify-between text-[11px] text-slate-500 pt-1">
                        <span>{qs.questions.length} questions</span>
                        <span>{qs.employer || 'General'}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Questions & Answer Cards (8 Cols) */}
        <div className="lg:col-span-8 space-y-4">
          {!selectedSet ? (
            <Card className="bg-slate-900/40 border-slate-800 text-center py-16">
              <CardContent className="space-y-2">
                <HelpCircle className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-xs text-slate-400">Select or create a question set to review answers.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {/* Question Set Header */}
              <div className="flex items-center justify-between p-3 rounded-lg bg-slate-900/80 border border-slate-800">
                <div className="space-y-0.5">
                  <h3 className="text-xs font-semibold text-slate-200">{selectedSet.title}</h3>
                  <p className="text-[11px] text-slate-400">
                    {selectedSet.job_title} {selectedSet.employer ? `• ${selectedSet.employer}` : ''} • {selectedSet.questions.length} questions
                  </p>
                </div>

                <Button
                  size="sm"
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="h-8 text-xs bg-cyan-600 hover:bg-cyan-500 text-white"
                >
                  {isGenerating ? (
                    <span className="flex items-center gap-1.5">
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      Generating Answers...
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      Generate Grounded Answers
                    </span>
                  )}
                </Button>
              </div>

              {/* Questions List */}
              <div className="space-y-3">
                {selectedSet.questions.map((q, idx) => {
                  const ans = q.current_answer;
                  const isEditing = editingQuestionId === q.id;

                  return (
                    <Card key={q.id} className="bg-slate-900/60 border-slate-800">
                      <CardHeader className="pb-2 space-y-2">
                        <div className="flex items-start justify-between gap-3">
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-[11px] font-mono text-slate-500 font-bold">#{idx + 1}</span>
                              {getCategoryBadge(q.category)}
                              {q.is_sensitive && (
                                <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 border-amber-800 text-[10px]">
                                  Sensitive
                                </Badge>
                              )}
                              {q.requires_attestation && (
                                <Badge variant="neutral" className="bg-rose-950/60 text-rose-400 border-rose-800 text-[10px]">
                                  Attestation Required
                                </Badge>
                              )}
                            </div>
                            <h4 className="text-xs font-medium text-slate-200 leading-snug">
                              {q.exact_question_text || q.question_text}
                            </h4>
                          </div>

                          <span className="text-[10px] text-slate-500 uppercase font-mono">
                            {q.answer_type.replace('_', ' ')}
                          </span>
                        </div>
                      </CardHeader>

                      <CardContent className="space-y-3 pt-1 text-xs">
                        {/* Sensitive Decision Warning */}
                        {q.is_sensitive && !ans?.is_user_overridden && (
                          <div className="p-2.5 rounded bg-amber-950/20 border border-amber-500/30 flex items-center justify-between text-amber-300 text-[11px]">
                            <span className="flex items-center gap-1.5">
                              <ShieldAlert className="w-3.5 h-3.5 shrink-0" />
                              This question touches on legal or protected status. Direct user election required.
                            </span>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-6 text-[10px] text-amber-400 hover:text-amber-200"
                              onClick={() => onNavigateTab('sensitive')}
                            >
                              Elect in Sensitive Tab
                            </Button>
                          </div>
                        )}

                        {/* Answer Body / Editor */}
                        {isEditing ? (
                          <div className="space-y-2">
                            <textarea
                              value={editText}
                              onChange={(e) => setEditText(e.target.value)}
                              rows={4}
                              className="w-full bg-slate-950 border border-slate-700 rounded p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                            />
                            <div className="flex items-center gap-2">
                              <Button
                                size="sm"
                                className="h-7 text-xs bg-cyan-600 hover:bg-cyan-500 text-white"
                                onClick={() => handleSaveEdit(q.id)}
                              >
                                Save Answer
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                className="h-7 text-xs text-slate-400"
                                onClick={() => setEditingQuestionId(null)}
                              >
                                Cancel
                              </Button>
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <div className="p-3 rounded bg-slate-950/70 border border-slate-800 text-slate-200 text-xs leading-relaxed whitespace-pre-line">
                              {ans ? ans.answer_text : <span className="text-slate-500 italic">No answer generated yet. Click "Generate Grounded Answers" or edit directly.</span>}
                            </div>

                            {ans && (
                              <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-500 pt-1 border-t border-slate-800/60 gap-2">
                                <div className="flex items-center gap-2">
                                  <span className="text-emerald-400 flex items-center gap-1">
                                    <CheckCircle2 className="w-3 h-3" />
                                    Confidence: {(ans.confidence_score * 100).toFixed(0)}%
                                  </span>
                                  {ans.source_refs.length > 0 && (
                                    <span className="text-cyan-400">
                                      {ans.source_refs.length} profile facts linked
                                    </span>
                                  )}
                                  {ans.is_user_overridden && (
                                    <Badge variant="neutral" className="bg-slate-800 text-slate-300 text-[10px]">
                                      User Override
                                    </Badge>
                                  )}
                                </div>

                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="h-6 text-xs text-cyan-400 hover:text-cyan-300 p-1"
                                  onClick={() => {
                                    setEditingQuestionId(q.id);
                                    setEditText(ans.answer_text);
                                  }}
                                >
                                  <Edit2 className="w-3 h-3 mr-1" />
                                  Edit Answer
                                </Button>
                              </div>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
