/**
 * Base Application Configuration Schemas
 */

export interface SystemHardwareConfig {
  maxVramAllocationMb: number;
  singleActiveModelEnforced: boolean;
  idleModelUnloadTimeoutSeconds: number;
  adaptiveScreenCaptureFps: {
    idle: number;
    active: number;
    burst: number;
  };
}

export interface AutonomConfig {
  appName: string;
  version: string;
  backendHost: string;
  backendPort: number;
  dataDirectory: string;
  databaseFilename: string;
  hardware: SystemHardwareConfig;
  governance: {
    maxDailyApplications: number;
    requireApprovalForSubmissions: boolean;
    emergencyHotkey: string;
  };
}
