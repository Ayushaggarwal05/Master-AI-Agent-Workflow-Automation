import React from 'react';
import { Bot, Activity, Layers, History, AlertCircle, RefreshCw } from 'lucide-react';
import { HealthResponse } from '@/types';

interface HeaderProps {
  activeTab: 'workspace' | 'explorer' | 'history';
  onTabChange: (tab: 'workspace' | 'explorer' | 'history') => void;
  health: HealthResponse | null;
  healthLoading: boolean;
  onRefreshHealth: () => void;
  historyCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onTabChange,
  health,
  healthLoading,
  onRefreshHealth,
  historyCount,
}) => {
  return (
    <header className="border-b border-dark-750 bg-dark-900/80 backdrop-blur-md sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Title */}
        <div className="flex items-center space-x-3">
          <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-brand-600 to-accent-purple flex items-center justify-center shadow-lg shadow-brand-500/20">
            <Bot className="h-5 w-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-semibold text-white tracking-tight">
                AI Agent Workflow Automation
              </h1>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20 font-medium">
                v1.0.0
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Excel-Driven Dynamic AI Execution Engine
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-dark-950 p-1 rounded-lg border border-dark-750">
          <button
            onClick={() => onTabChange('workspace')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeTab === 'workspace'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-dark-800'
            }`}
          >
            <Activity className="h-3.5 w-3.5" />
            <span>Workspace</span>
          </button>
          <button
            onClick={() => onTabChange('explorer')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
              activeTab === 'explorer'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-dark-800'
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            <span>Workflows</span>
          </button>
          <button
            onClick={() => onTabChange('history')}
            className={`flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium rounded-md transition-colors relative ${
              activeTab === 'history'
                ? 'bg-brand-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-dark-800'
            }`}
          >
            <History className="h-3.5 w-3.5" />
            <span>Executions</span>
            {historyCount > 0 && (
              <span className="ml-1 px-1.5 py-0.2 bg-brand-400/20 text-brand-300 text-[10px] rounded-full font-mono">
                {historyCount}
              </span>
            )}
          </button>
        </nav>

        {/* Live Backend Status */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onRefreshHealth}
            title="Refresh backend status"
            disabled={healthLoading}
            className="p-1.5 text-slate-400 hover:text-slate-200 hover:bg-dark-800 rounded-md transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${healthLoading ? 'animate-spin' : ''}`} />
          </button>

          <div className="flex items-center space-x-2 bg-dark-950 px-2.5 py-1.5 rounded-full border border-dark-750">
            {health?.status === 'ok' ? (
              <>
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-emerald opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-accent-emerald"></span>
                </span>
                <span className="text-xs text-slate-300 font-mono">
                  Registry: <strong className="text-accent-emerald">{health.workflows_loaded}</strong> WFs
                </span>
              </>
            ) : (
              <>
                <AlertCircle className="h-3.5 w-3.5 text-accent-rose" />
                <span className="text-xs text-accent-rose font-medium">Backend Offline</span>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
