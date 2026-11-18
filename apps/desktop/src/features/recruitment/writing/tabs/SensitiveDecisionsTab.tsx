/**
 * Stage 24: Sensitive Decisions & Human Attestation Tab.
 * Strictly guards work authorization, compensation, voluntary demographic disclosures,
 * and user legal attestations against autonomous AI completion.
 */

import * as React from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  Lock,
  UserCheck,
} from 'lucide-react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import type {
  SensitiveDecisionItem,
  UserAttestationRequest,
} from '@autonom/shared-types';

interface SensitiveDecisionsTabProps {
  decisions: SensitiveDecisionItem[];
  onRecordAttestation: (req: UserAttestationRequest) => Promise<void>;
  onRefresh: () => Promise<void>;
}

export const SensitiveDecisionsTab: React.FC<SensitiveDecisionsTabProps> = ({
  decisions,
  onRecordAttestation,
  onRefresh,
}) => {
  const [selectedChoices, setSelectedChoices] = React.useState<Record<string, string>>({});
  const [attestationChecked, setAttestationChecked] = React.useState<Record<string, boolean>>({});
  const [isSubmitting, setIsSubmitting] = React.useState<Record<string, boolean>>({});

  const handleSelectChoice = (itemId: string, choice: string) => {
    setSelectedChoices((prev) => ({ ...prev, [itemId]: choice }));
  };

  const handleToggleAttestation = (itemId: string) => {
    setAttestationChecked((prev) => ({ ...prev, [itemId]: !prev[itemId] }));
  };

  const handleSubmitDecision = async (item: SensitiveDecisionItem) => {
    const choice = selectedChoices[item.id] || item.allowed_choices[0];
    const isAttested = !!attestationChecked[item.id];

    setIsSubmitting((prev) => ({ ...prev, [item.id]: true }));
    try {
      await onRecordAttestation({
        decision_item_id: item.id,
        selected_choice: choice,
        accepted_attestation: isAttested,
      });
      await onRefresh();
    } finally {
      setIsSubmitting((prev) => ({ ...prev, [item.id]: false }));
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Strict AI Guard Explanation */}
      <div className="p-4 rounded-lg bg-amber-950/20 border border-amber-500/30 flex items-start gap-3">
        <Lock className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <h3 className="text-xs font-semibold text-amber-200">
            Strict Human Decision Guard (Stage 24 Zero-Automation Boundary)
          </h3>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            By design and legal mandate, AUTONOM recruitment agents are prohibited from autonomously answering work authorization, visa sponsorship, compensation targets, protected demographic disclosures, or legal attestations. Every item below requires your explicit manual selection.
          </p>
        </div>
      </div>

      {/* Decisions List */}
      <div className="space-y-4">
        {decisions.length === 0 ? (
          <Card className="bg-slate-900/40 border-slate-800 text-center py-12">
            <CardContent className="space-y-2">
              <ShieldCheck className="w-8 h-8 text-emerald-400 mx-auto" />
              <p className="text-xs text-slate-300">
                All sensitive disclosures and attestations are completed and sealed.
              </p>
            </CardContent>
          </Card>
        ) : (
          decisions.map((item) => {
            const currentChoice = selectedChoices[item.id] || item.user_decision || '';
            const isConfirmed = item.attestation_accepted;
            const isBusy = !!isSubmitting[item.id];

            return (
              <Card
                key={item.id}
                className={`bg-slate-900/60 border ${
                  isConfirmed ? 'border-emerald-500/40' : 'border-amber-500/40'
                }`}
              >
                <CardHeader className="pb-2 space-y-1">
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="neutral" className="bg-amber-950/60 text-amber-400 border-amber-800 text-[10px]">
                          {item.category.replace('_', ' ').toUpperCase()}
                        </Badge>
                        {item.is_voluntary && (
                          <Badge variant="neutral" className="bg-slate-800 text-slate-400 text-[10px]">
                            Voluntary
                          </Badge>
                        )}
                        {isConfirmed && (
                          <Badge variant="neutral" className="bg-emerald-950 text-emerald-400 border-emerald-800 text-[10px] flex items-center gap-1">
                            <CheckCircle2 className="w-3 h-3" /> Sealed
                          </Badge>
                        )}
                      </div>
                      <h4 className="text-xs font-semibold text-slate-200">
                        {item.question_text}
                      </h4>
                    </div>

                    {item.decided_at && (
                      <span className="text-[10px] text-slate-500 font-mono">
                        Confirmed: {new Date(item.decided_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="space-y-4 pt-1 text-xs">
                  {/* Option Choices */}
                  <div className="space-y-2">
                    <span className="text-[11px] text-slate-400 block font-medium">Select your answer:</span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                      {item.allowed_choices.map((choice) => {
                        const isSelected = currentChoice === choice;
                        return (
                          <button
                            key={choice}
                            type="button"
                            onClick={() => handleSelectChoice(item.id, choice)}
                            className={`p-2.5 rounded-lg border text-left text-xs transition-all ${
                              isSelected
                                ? 'bg-cyan-950/60 border-cyan-500 text-cyan-200 ring-1 ring-cyan-500/30'
                                : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700'
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span>{choice}</span>
                              {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Legal Attestation Checkbox */}
                  <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 space-y-2">
                    <label className="flex items-start gap-2.5 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={!!attestationChecked[item.id] || isConfirmed}
                        onChange={() => handleToggleAttestation(item.id)}
                        className="mt-0.5 rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0"
                      />
                      <span className="text-[11px] text-slate-300 leading-snug">
                        I hereby attest and confirm this statement is accurate and truthful. I understand that AUTONOM records this user confirmation as a verified provenance assertion.
                      </span>
                    </label>
                  </div>

                  {/* Submission Button */}
                  <div className="flex justify-end pt-1">
                    <Button
                      size="sm"
                      className="h-8 text-xs bg-emerald-600 hover:bg-emerald-500 text-white"
                      onClick={() => handleSubmitDecision(item)}
                      disabled={isBusy || !currentChoice || (!attestationChecked[item.id] && !isConfirmed)}
                    >
                      <UserCheck className="w-3.5 h-3.5 mr-1" />
                      {isBusy ? 'Sealing...' : isConfirmed ? 'Update Sealed Decision' : 'Confirm & Seal Decision'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
};
