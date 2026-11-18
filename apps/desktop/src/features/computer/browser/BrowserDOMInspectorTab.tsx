import * as React from 'react';
import {
  Code2,
  FileText,
  Search,
  MousePointer,
  RefreshCw,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import {
  BrowserSessionResponse,
  DOMInspectionResponse,
  DOMElementNode,
} from '@autonom/shared-types';

interface BrowserDOMInspectorTabProps {
  session: BrowserSessionResponse | null;
  onInspectDOM: (sessionId: string) => Promise<DOMInspectionResponse>;
  onExecuteAction: (sessionId: string, req: any) => Promise<any>;
  isLoading: boolean;
}

export const BrowserDOMInspectorTab: React.FC<BrowserDOMInspectorTabProps> = ({
  session,
  onInspectDOM,
  onExecuteAction,
  isLoading,
}) => {
  const [domData, setDomData] = React.useState<DOMInspectionResponse | null>(null);
  const [isInspecting, setIsInspecting] = React.useState<boolean>(false);
  const [filterText, setFilterText] = React.useState<string>('');
  const [actingNodeId, setActingNodeId] = React.useState<number | null>(null);

  const handleInspect = async () => {
    if (!session) return;
    setIsInspecting(true);
    try {
      const data = await onInspectDOM(session.id);
      setDomData(data);
    } finally {
      setIsInspecting(false);
    }
  };

  const handleQuickClick = async (el: DOMElementNode) => {
    if (!session) return;
    setActingNodeId(el.id);
    try {
      await onExecuteAction(session.id, {
        action_type: 'click',
        target_locator: el.selector,
      });
      // Re-inspect DOM after click
      await handleInspect();
    } finally {
      setActingNodeId(null);
    }
  };

  if (!session) {
    return (
      <Card className="border-border/60 bg-card/60">
        <CardContent className="py-16 text-center text-muted-foreground">
          <Code2 className="h-10 w-10 mx-auto mb-3 opacity-30" />
          <p className="text-sm font-medium">No session selected</p>
          <p className="text-xs mt-1">Select an active session to inspect its DOM hierarchy.</p>
        </CardContent>
      </Card>
    );
  }

  const filteredElements = (domData?.elements || []).filter((el) => {
    if (!filterText) return true;
    const q = filterText.toLowerCase();
    return (
      el.tag.toLowerCase().includes(q) ||
      (el.role && el.role.toLowerCase().includes(q)) ||
      (el.name && el.name.toLowerCase().includes(q)) ||
      (el.text && el.text.toLowerCase().includes(q)) ||
      el.selector.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="space-y-0.5">
              <CardTitle className="text-base font-semibold flex items-center gap-2">
                <Code2 className="h-4 w-4 text-primary" />
                Structured DOM & Accessibility Inspector
              </CardTitle>
              <CardDescription className="text-xs">
                Extracts compact, actionable elements and form definitions optimized for AI agent reasoning.
              </CardDescription>
            </div>
            <div className="flex items-center gap-3">
              {domData && (
                <Badge variant="outline" className="font-mono text-xs text-primary">
                  ~{domData.token_estimate} LLM tokens
                </Badge>
              )}
              <Button
                onClick={handleInspect}
                disabled={isInspecting || isLoading}
                className="gap-1.5 text-xs font-semibold h-8"
              >
                <RefreshCw className={`h-3.5 w-3.5 ${isInspecting ? 'animate-spin' : ''}`} />
                {isInspecting ? 'Extracting Tree...' : 'Inspect Live Page'}
              </Button>
            </div>
          </div>
        </CardHeader>
        {domData && (
          <CardContent className="pt-0">
            <div className="flex items-center justify-between text-xs text-muted-foreground border-t border-border/40 pt-3">
              <span className="truncate">
                URL: <span className="font-mono text-foreground">{domData.url}</span>
              </span>
              <span>
                Discovered: <strong className="text-foreground">{domData.total_elements_count}</strong> controls,{' '}
                <strong className="text-foreground">{domData.forms.length}</strong> forms
              </span>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Discovered Forms Section */}
      {domData?.forms && domData.forms.length > 0 && (
        <Card className="border-border/60 bg-card/60">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <FileText className="h-4 w-4 text-purple-400" />
              Detected Forms & Application Inputs ({domData.forms.length})
            </CardTitle>
            <CardDescription className="text-xs">
              Form structures identified on the page. Field filling is safe; form submission requires Stage 14 approval.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {domData.forms.map((form, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-lg border border-border/40 bg-background/40 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 font-mono text-xs">
                      <span className="font-bold text-foreground">Form #{idx + 1}</span>
                      <Badge variant="neutral" className="text-[10px] uppercase font-mono">
                        {form.method}
                      </Badge>
                      <span className="text-muted-foreground truncate max-w-sm">
                        {form.action_url || 'local submit'}
                      </span>
                    </div>
                    <Badge variant="outline" className="text-[10px] border-amber-500/40 text-amber-400">
                      Submission Gate Active
                    </Badge>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                    {form.fields.map((fld, fIdx) => (
                      <div
                        key={fIdx}
                        className="p-2 rounded border border-border/30 bg-background/60 text-xs space-y-0.5"
                      >
                        <div className="flex items-center justify-between font-mono">
                          <span className="font-semibold text-primary">{fld.name}</span>
                          <span className="text-[10px] text-muted-foreground">{fld.field_type}</span>
                        </div>
                        {fld.label && <p className="text-[11px] text-muted-foreground truncate">{fld.label}</p>}
                        {fld.required && (
                          <Badge variant="outline" className="text-[9px] text-amber-400">
                            Required
                          </Badge>
                        )}
                      </div>
                    ))}
                  </div>

                  {form.submit_button_selector && (
                    <div className="flex items-center gap-2 text-xs font-mono text-muted-foreground pt-1">
                      <span>Submit Trigger:</span>
                      <code className="text-primary bg-primary/10 px-1.5 py-0.5 rounded">
                        {form.submit_button_selector}
                      </code>
                      {form.submit_button_text && (
                        <span>("{form.submit_button_text}")</span>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Interactive Elements Table */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-4">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <MousePointer className="h-4 w-4 text-cyan-400" />
              Interactive Controls Hierarchy
            </CardTitle>
            <div className="relative w-64">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
              <Input
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
                placeholder="Filter elements..."
                className="pl-8 h-8 text-xs font-mono"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {!domData ? (
            <div className="py-12 text-center text-muted-foreground">
              <Code2 className="h-10 w-10 mx-auto mb-3 opacity-30" />
              <p className="text-sm font-medium">Page DOM not yet inspected</p>
              <p className="text-xs mt-1">
                Click "Inspect Live Page" above to analyze all buttons, links, inputs, and interactive controls.
              </p>
            </div>
          ) : filteredElements.length === 0 ? (
            <p className="text-xs text-muted-foreground text-center py-8">
              No elements matched filter "{filterText}"
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-border/40 text-left text-muted-foreground">
                    <th className="pb-2 font-mono">ID</th>
                    <th className="pb-2">Tag / Role</th>
                    <th className="pb-2">Accessible Name / Text</th>
                    <th className="pb-2 font-mono">Selector</th>
                    <th className="pb-2 text-right">Quick Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border/20">
                  {filteredElements.map((el) => (
                    <tr key={el.id} className="hover:bg-background/40 transition-colors">
                      <td className="py-2.5 font-mono text-primary font-bold">[{el.id}]</td>
                      <td className="py-2.5">
                        <div className="flex items-center gap-1.5">
                          <span className="font-mono font-medium uppercase text-[11px]">{el.tag}</span>
                          {el.role && (
                            <Badge variant="neutral" className="text-[9px] uppercase font-mono">
                              {el.role}
                            </Badge>
                          )}
                        </div>
                      </td>
                      <td className="py-2.5 max-w-xs truncate">
                        <span className="text-foreground font-medium">
                          {el.name || el.text || el.placeholder || '<unnamed>'}
                        </span>
                      </td>
                      <td className="py-2.5 font-mono text-muted-foreground text-[11px] truncate max-w-xs">
                        {el.selector}
                      </td>
                      <td className="py-2.5 text-right">
                        {el.is_clickable && (
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={actingNodeId === el.id}
                            onClick={() => handleQuickClick(el)}
                            className="h-6 text-[10px] gap-1 px-2 font-mono text-primary hover:bg-primary/10"
                          >
                            <MousePointer className="h-3 w-3" />
                            Click
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
