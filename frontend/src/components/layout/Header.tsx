import React from 'react';
import { Home, Layers, AlertCircle, RefreshCw, Zap } from 'lucide-react';
import { HealthResponse } from '@/types';

interface HeaderProps {
  activeTab: 'workspace' | 'explorer';
  onTabChange: (tab: 'workspace' | 'explorer') => void;
  health: HealthResponse | null;
  healthLoading: boolean;
  onRefreshHealth: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onTabChange,
  health,
  healthLoading,
  onRefreshHealth,
}) => {
  return (
    <header className="border-b border-[#1c202d] bg-[#0c0e14] sticky top-0 z-30 select-none shadow-md shadow-black/20">
      <div className="max-w-[1750px] mx-auto px-6 sm:px-8 lg:px-10 h-[72px] flex items-center justify-between">
        {/* Brand & Title with Glowing Flame Orange Emblem */}
        <div className="flex items-center space-x-3.5">
          <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-orange-500 to-amber-600 flex items-center justify-center shadow-lg shadow-orange-500/35 border border-orange-400/40 flex-shrink-0">
            <Zap className="h-5 w-5 text-white fill-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base sm:text-lg font-bold text-white tracking-tight">
                AI Agent Workflow Automation
              </h1>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block font-normal mt-0.5">
              Excel-Driven Dynamic AI Execution Engine
            </p>
          </div>
        </div>

        {/* Navigation Tabs (Centered & Spacious) */}
        <nav className="flex items-center space-x-2.5 bg-[#0a0c12] p-1.5 px-2 rounded-2xl border border-[#1e2333] shadow-inner">
          <button
            onClick={() => onTabChange('workspace')}
            className={`relative flex items-center space-x-2.5 px-5 py-2.5 rounded-xl transition-all cursor-pointer ${
              activeTab === 'workspace'
                ? 'bg-orange-500/15 border border-orange-500/30 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-[#151824]'
            }`}
          >
            <Home className={`h-4 w-4 ${activeTab === 'workspace' ? 'text-orange-300 stroke-[2.2]' : 'text-slate-400'}`} />
            <span className={`text-[13px] tracking-wide ${activeTab === 'workspace' ? 'text-white font-semibold' : 'text-slate-400 font-medium'}`}>
              Workspace
            </span>
            {activeTab === 'workspace' && (
              <span className="absolute bottom-0 left-3 right-3 h-[2.5px] bg-gradient-to-r from-orange-500 via-amber-400 to-orange-500 rounded-t-sm shadow-md shadow-orange-500" />
            )}
          </button>
          <button
            onClick={() => onTabChange('explorer')}
            className={`relative flex items-center space-x-2.5 px-5 py-2.5 rounded-xl transition-all cursor-pointer ${
              activeTab === 'explorer'
                ? 'bg-orange-500/15 border border-orange-500/30 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-[#151824]'
            }`}
          >
            <Layers className={`h-4 w-4 ${activeTab === 'explorer' ? 'text-orange-300 stroke-[2.2]' : 'text-slate-400'}`} />
            <span className={`text-[13px] tracking-wide ${activeTab === 'explorer' ? 'text-white font-semibold' : 'text-slate-400 font-medium'}`}>
              Workflows
            </span>
            {activeTab === 'explorer' && (
              <span className="absolute bottom-0 left-3 right-3 h-[2.5px] bg-gradient-to-r from-orange-500 via-amber-400 to-orange-500 rounded-t-sm shadow-md shadow-orange-500" />
            )}
          </button>
        </nav>

        {/* Live Backend Registry Status (No JD circle) */}
        <div className="flex items-center space-x-3.5">
          <button
            onClick={onRefreshHealth}
            title="Refresh backend status"
            disabled={healthLoading}
            className="p-2 text-slate-400 hover:text-white hover:bg-[#181d2c] rounded-xl transition-colors border border-transparent hover:border-[#1e2332]"
          >
            <RefreshCw className={`h-4 w-4 ${healthLoading ? 'animate-spin' : ''}`} />
          </button>

          <div className="flex items-center space-x-3 bg-[#07080b] px-4 py-2 rounded-full border border-[#1e2332] shadow-sm">
            {health?.status === 'ok' ? (
              <>
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400"></span>
                </span>
                <span className="text-xs text-slate-300 font-mono">
                  Registry: <strong className="text-white font-bold">{health.workflows_loaded} Workflows</strong>
                </span>
              </>
            ) : (
              <>
                <AlertCircle className="h-4 w-4 text-rose-500" />
                <span className="text-xs text-rose-400 font-semibold">Backend Offline</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
