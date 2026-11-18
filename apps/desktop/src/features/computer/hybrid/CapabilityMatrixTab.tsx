import * as React from 'react';
import { Check, X } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface MatrixRow {
  action: string;
  dom: boolean;
  uia: boolean;
  win32: boolean;
  visual: boolean;
  risk: string;
  idempotent: boolean;
  notes: string;
}

const MATRIX_DATA: MatrixRow[] = [
  {
    action: 'Click Element',
    dom: true,
    uia: true,
    win32: true,
    visual: true,
    risk: 'REPEATABLE',
    idempotent: true,
    notes: 'DOM: role/test-id; UIA: InvokePattern; Visual: SendInput coordinates',
  },
  {
    action: 'Double Click',
    dom: true,
    uia: true,
    win32: true,
    visual: true,
    risk: 'REPEATABLE',
    idempotent: true,
    notes: 'Native double click event propagation',
  },
  {
    action: 'Right Click',
    dom: true,
    uia: false,
    win32: true,
    visual: true,
    risk: 'REPEATABLE',
    idempotent: true,
    notes: 'Context menu invocation across mouse or DOM event',
  },
  {
    action: 'Enter Text / Fill',
    dom: true,
    uia: true,
    win32: true,
    visual: true,
    risk: 'REPEATABLE',
    idempotent: true,
    notes: 'DOM: fill(); UIA: ValuePattern; Win32: WM_SETTEXT; Visual: SendInput keys',
  },
  {
    action: 'Navigate URL',
    dom: true,
    uia: false,
    win32: false,
    visual: false,
    risk: 'REPEATABLE',
    idempotent: true,
    notes: 'Playwright Page.goto() with fail-closed origin whitelist',
  },
  {
    action: 'Scroll Content',
    dom: true,
    uia: true,
    win32: true,
    visual: true,
    risk: 'REPEATABLE',
    idempotent: true,
    notes: 'DOM: mouse.wheel; UIA: ScrollPattern; Visual: mouse_event WHEEL',
  },
  {
    action: 'Press Key / Hotkey',
    dom: true,
    uia: true,
    win32: true,
    visual: true,
    risk: 'REPEATABLE',
    idempotent: true,
    notes: 'Direct virtual keycode injection or SendInput keyboard array',
  },
  {
    action: 'Inspect Structure',
    dom: true,
    uia: true,
    win32: true,
    visual: true,
    risk: 'READ_ONLY',
    idempotent: true,
    notes: 'DOM: interactive tree; UIA: accessibility tree; Visual: WinRT OCR',
  },
  {
    action: 'Submit Application',
    dom: true,
    uia: true,
    win32: false,
    visual: true,
    risk: 'NON_IDEMPOTENT',
    idempotent: false,
    notes: 'Stage 14 Approval Required. Blind fallback blocked on unknown outcome!',
  },
  {
    action: 'Select Option',
    dom: true,
    uia: true,
    win32: false,
    visual: true,
    risk: 'REPEATABLE',
    idempotent: true,
    notes: 'DOM: selectOption; UIA: SelectionItemPattern; Visual: OCR click',
  },
];

export const CapabilityMatrixTab: React.FC = () => {
  return (
    <div className="space-y-6">
      <Card className="border-slate-800 bg-slate-900/40">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-base text-slate-100">Cross-Method Capability & Fallback Matrix</CardTitle>
              <CardDescription className="text-xs text-slate-400">
                Action-level applicability, relative compute cost, and idempotency boundaries across all 4 interaction adapters.
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline" className="border-emerald-500/30 bg-emerald-500/10 text-xs text-emerald-400">
                DOM: Cost 1/5
              </Badge>
              <Badge variant="outline" className="border-cyan-500/30 bg-cyan-500/10 text-xs text-cyan-400">
                UIA: Cost 2/5
              </Badge>
              <Badge variant="outline" className="border-purple-500/30 bg-purple-500/10 text-xs text-purple-400">
                Visual: Cost 4/5
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="border-b border-slate-800 bg-slate-950/60 font-mono text-[11px] text-slate-400">
                <tr>
                  <th className="py-2.5 px-3">Operation / Action</th>
                  <th className="py-2.5 px-3">Browser DOM</th>
                  <th className="py-2.5 px-3">Windows UIA</th>
                  <th className="py-2.5 px-3">Win32</th>
                  <th className="py-2.5 px-3">Visual Grounding</th>
                  <th className="py-2.5 px-3">Risk Level</th>
                  <th className="py-2.5 px-3">Notes & Safeguards</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {MATRIX_DATA.map((row) => (
                  <tr key={row.action} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-2.5 px-3 font-medium text-slate-200">{row.action}</td>
                    <td className="py-2.5 px-3">
                      {row.dom ? (
                        <Check className="h-4 w-4 text-emerald-400" />
                      ) : (
                        <X className="h-4 w-4 text-slate-600" />
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      {row.uia ? (
                        <Check className="h-4 w-4 text-cyan-400" />
                      ) : (
                        <X className="h-4 w-4 text-slate-600" />
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      {row.win32 ? (
                        <Check className="h-4 w-4 text-blue-400" />
                      ) : (
                        <X className="h-4 w-4 text-slate-600" />
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      {row.visual ? (
                        <Check className="h-4 w-4 text-purple-400" />
                      ) : (
                        <X className="h-4 w-4 text-slate-600" />
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      <Badge
                        variant="outline"
                        className={`text-[10px] ${
                          row.risk === 'NON_IDEMPOTENT'
                            ? 'border-amber-500/30 bg-amber-500/10 text-amber-400'
                            : row.risk === 'READ_ONLY'
                            ? 'border-blue-500/30 bg-blue-500/10 text-blue-400'
                            : 'border-slate-700 bg-slate-800 text-slate-300'
                        }`}
                      >
                        {row.risk}
                      </Badge>
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-400">{row.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
