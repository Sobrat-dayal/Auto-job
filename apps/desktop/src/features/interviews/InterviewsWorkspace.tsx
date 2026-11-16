import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CalendarCheck, Calendar, Sparkles, Mic } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleEmptyState,
} from '@/components/module';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export const InterviewsWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/interviews/calendar')) return 'calendar';
    if (location.pathname.includes('/interviews/prep')) return 'prep';
    if (location.pathname.includes('/interviews/mock')) return 'mock';
    if (location.pathname.includes('/interviews/history')) return 'history';
    return 'upcoming';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'upcoming') navigate('/interviews/upcoming');
    else navigate(`/interviews/${tabId}`);
  };

  const tabs = [
    { id: 'upcoming', label: 'Upcoming Rounds', badge: 0 },
    { id: 'calendar', label: 'Interview Calendar' },
    { id: 'prep', label: 'Company & Technical Prep' },
    { id: 'mock', label: 'AI Mock Simulator' },
    { id: 'history', label: 'Historical Reviews' },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Interview Coordination & Coaching"
        description="Schedule rounds, generate company-specific prep dossiers, and practice with AI mock simulations."
        icon={CalendarCheck}
        stageTag="Stage 39 Planned"
        badgeLabel="0 Scheduled"
        badgeVariant="outline"
      />

      <ModuleUnavailableState
        moduleName="Interview Management & Mock Simulation Suite"
        stageTag="Stage 39 & 40"
        stageName="Interview Coaching Engine"
        description="Calendar syncing, automated interview confirmation parsing, and conversational AI mock interview simulations will go live in Stage 39. In accordance with zero-fake-data rules, only genuine interview invitations will be scheduled."
        plannedCapabilities={[
          'Automated ICS calendar invitation parsing (Stage 39)',
          'Company architecture & culture briefing generator (Stage 39)',
          'Interactive STAR method technical mock interviewer (Stage 40)',
          'Post-round transcript feedback and follow-up generation (Stage 40)',
        ]}
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      {activeTab === 'mock' ? (
        <Card className="border-border/60 bg-card/60">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Mic className="h-4 w-4 text-primary" />
              Autonomous Mock Interview Studio
            </CardTitle>
            <CardDescription className="text-xs">
              Simulate technical system design or behavioral rounds with real-time feedback
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded-lg border border-dashed border-border/80 bg-background/50 p-8 text-center">
              <Sparkles className="mx-auto h-8 w-8 text-primary/70" />
              <h4 className="mt-2 text-sm font-semibold text-foreground">
                Mock Simulation Engine Activates in Stage 40
              </h4>
              <p className="mt-1 text-xs text-muted-foreground max-w-sm mx-auto">
                Practice against strict interviewer personas with live speech-to-text and instant
                behavioral analysis.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <ModuleEmptyState
          icon={Calendar}
          title="No upcoming interviews scheduled"
          description="When recruiter emails or invitations are parsed by the communications engine, upcoming interview schedules and preparation materials will be organized here."
        />
      )}
    </ModulePage>
  );
};

export default InterviewsWorkspace;
