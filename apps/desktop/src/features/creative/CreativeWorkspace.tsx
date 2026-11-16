import * as React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Box, Palette } from 'lucide-react';
import {
  ModulePage,
  ModuleHeader,
  ModuleTabs,
  ModuleUnavailableState,
  ModuleEmptyState,
} from '@/components/module';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export const CreativeWorkspace: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const getInitialTab = (): string => {
    if (location.pathname.includes('/creative/animation')) return 'animation';
    if (location.pathname.includes('/creative/graphics')) return 'graphics';
    if (location.pathname.includes('/creative/media')) return 'media';
    if (location.pathname.includes('/creative/renders')) return 'renders';
    if (location.pathname.includes('/creative/assets')) return 'assets';
    return '3d';
  };

  const [activeTab, setActiveTab] = React.useState<string>(getInitialTab());

  React.useEffect(() => {
    setActiveTab(getInitialTab());
  }, [location.pathname]);

  const handleTabChange = (tabId: string) => {
    setActiveTab(tabId);
    if (tabId === '3d') navigate('/creative/3d');
    else navigate(`/creative/${tabId}`);
  };

  const tabs = [
    { id: '3d', label: '3D Viewport & Meshes' },
    { id: 'animation', label: 'Animation Timelines' },
    { id: 'graphics', label: 'Vector & UI Graphics' },
    { id: 'media', label: 'Video & Audio Synthesis' },
    { id: 'renders', label: 'Render Queue', badge: 0 },
    { id: 'assets', label: 'Creative Asset Library' },
  ];

  return (
    <ModulePage>
      <ModuleHeader
        title="Creative Studio & 3D Pipeline"
        description="Headless 3D rendering, procedural geometry generation, animation scripting, and media synthesis."
        icon={Box}
        stageTag="Stage 43 Planned"
        badgeLabel="Renderer Offline"
        badgeVariant="outline"
      />

      <ModuleUnavailableState
        moduleName="Autonomous 3D & Creative Media Suite"
        stageTag="Stage 43"
        stageName="Creative Studio & Render Farm"
        description="Procedural 3D asset generation (Blender Python API), video editing timelines, and AI graphics generation activate in Stage 43. Assets are cataloged under durable artifact storage."
        plannedCapabilities={[
          'Headless Blender scene script generation & rendering (Stage 43)',
          'Vector graphics & icon design generation (Stage 43)',
          'Automated audio/video sequence clipping (Stage 43)',
          'Direct integration with artifact asset storage (Active)',
        ]}
      />

      <ModuleTabs tabs={tabs} activeTab={activeTab} onTabChange={handleTabChange} />

      {activeTab === '3d' ? (
        <Card className="border-border/60 bg-card/60">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Box className="h-4 w-4 text-primary" />
              WebGL 3D Canvas Viewport
            </CardTitle>
            <CardDescription className="text-xs">
              Interactive 3D geometry and mesh inspector
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative aspect-video w-full overflow-hidden rounded-lg border border-border/80 bg-background/90 flex flex-col items-center justify-center p-6 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-muted/60 text-muted-foreground ring-1 ring-border">
                <Box className="h-6 w-6" />
              </div>
              <h4 className="mt-3 text-sm font-semibold text-foreground">
                3D Viewport Canvas Scheduled for Stage 43
              </h4>
              <p className="mt-1 max-w-sm text-xs text-muted-foreground">
                Three.js / WebGL viewport for inspecting agent-generated 3D GLTF models and scene
                renders will display here.
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <ModuleEmptyState
          icon={Palette}
          title={`No creative ${activeTab} assets found`}
          description="Generated 3D scenes, renders, and media files will be cataloged here once Stage 43 tools are active."
        />
      )}
    </ModulePage>
  );
};

export default CreativeWorkspace;
