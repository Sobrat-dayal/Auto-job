import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { MessagesSquare, Inbox } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleToolbar,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleEmptyState,
} from '@/components/module';

export const CommunicationsWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/communications/conversations')) return 'conversations';
    if (location.pathname.includes('/communications/email')) return 'email';
    if (location.pathname.includes('/communications/telegram')) return 'telegram';
    if (location.pathname.includes('/communications/whatsapp')) return 'whatsapp';
    if (location.pathname.includes('/communications/follow-ups')) return 'follow-ups';
    return 'inbox';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());
  const [searchQuery, setSearchQuery] = React.useState('');

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === 'inbox') navigate('/communications/inbox');
    else navigate(`/communications/${tabId}`);
  };

  const tabs = [
    { id: 'inbox', label: 'Unified Inbox', badge: 0 },
    { id: 'conversations', label: 'Conversations' },
    { id: 'email', label: 'Email & IMAP', badge: 'Ready' },
    { id: 'telegram', label: 'Telegram' },
    { id: 'whatsapp', label: 'WhatsApp' },
    { id: 'follow-ups', label: 'Scheduled Follow-Ups', badge: 0 },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Communications & Messaging Hub"
        description="Unified recruiter correspondence, automated email tracking, and AI-assisted follow-up staging."
        icon={MessagesSquare}
        stageTag="Stage 36 Planned"
        badgeLabel="Inbox Clean"
        badgeVariant="outline"
      />

      <ModuleUnavailableState
        moduleName="Unified Communications & Outreach Engine"
        stageTag="Stage 36"
        stageName="Recruitment Communications & Messaging"
        description="Autonomous email monitoring, recruiter reply detection, and context-aware follow-up drafting will be implemented in Stage 36. Per security rules, outgoing emails and messages require explicit user approval."
        plannedCapabilities={[
          'OAuth 2.0 Gmail & Microsoft 365 IMAP sync (Stage 36)',
          'AI detection of interview requests, rejections, and inquiries (Stage 36)',
          'Contextual follow-up letter generation with evidence citation (Stage 37)',
          'Telegram and WhatsApp notification bot dispatch (Stage 38)',
        ]}
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      <ModuleToolbar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        searchPlaceholder="Filter communications or search recruiter messages..."
      />

      <ModuleEmptyState
        icon={Inbox}
        title="No messages in inbox"
        description="Recruitment communications from email and messaging channels will appear here once Stage 36 integrations are configured. Zero fake messages displayed."
      />
    </ModulePage>
  );
};

export default CommunicationsWorkspace;
