import { useState, useEffect, useRef } from 'react';
import {
  Shield,
  Settings,
  Terminal,
  RefreshCw,
  Sliders
} from 'lucide-react';

interface DiscordUser {
  username: string;
  discriminator: string;
  avatar_url?: string;
  banner_url?: string;
  banner_color?: string;
}

interface GameInfo {
  details?: string;
  state?: string;
  start_time?: number;
}

interface LiveStatus {
  is_valorant_running: boolean;
  is_discord_running: boolean;
  player_name: string;
  player_tag: string;
  region: string;
  version: string;
  game_info?: GameInfo;
  discord_user?: DiscordUser;
}

interface AppConfig {
  presence_refresh_interval?: number;
  rpc_enabled?: boolean;
  region?: [string, string[]];
  locale?: [string, string[]];
  presences?: {
    menu?: {
      show_rank_in_comp_lobby?: boolean;
    };
    modes?: {
      all?: {
        large_image?: [string, string[]];
        small_image?: [string, string[]];
      };
      range?: {
        show_rank_in_range?: boolean;
      };
    };
  };
  startup?: {
    game_launch_timeout?: number;
    presence_timeout?: number;
    show_github_link?: boolean;
    auto_launch_skincli?: boolean;
  };
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'presence' | 'privacy' | 'system' | 'logs'>('presence');
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [status, setStatus] = useState<LiveStatus | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [toast, setToast] = useState<{ show: boolean; msg: string; success: boolean }>({
    show: false,
    msg: '',
    success: true,
  });

  const saveTimeout = useRef<any>(null);
  const logsInterval = useRef<any>(null);
  const statusInterval = useRef<any>(null);
  const logConsoleRef = useRef<HTMLDivElement | null>(null);

  // Load configuration on mount
  useEffect(() => {
    fetchConfig();
    fetchStatus();

    // Poll live status
    statusInterval.current = setInterval(fetchStatus, 2500);

    return () => {
      if (saveTimeout.current) clearTimeout(saveTimeout.current);
      if (statusInterval.current) clearInterval(statusInterval.current);
      if (logsInterval.current) clearInterval(logsInterval.current);
    };
  }, []);

  // Poll logs on demand
  useEffect(() => {
    if (activeTab === 'logs') {
      fetchLogs();
      logsInterval.current = setInterval(fetchLogs, 2000);
    } else {
      if (logsInterval.current) {
        clearInterval(logsInterval.current);
        logsInterval.current = null;
      }
    }
  }, [activeTab]);

  // Scroll to bottom of logs
  useEffect(() => {
    if (activeTab === 'logs' && logConsoleRef.current) {
      logConsoleRef.current.scrollTop = logConsoleRef.current.scrollHeight;
    }
  }, [logs, activeTab]);

  const fetchConfig = async () => {
    try {
      const res = await fetch('/api/config');
      if (res.ok) {
        const data = await res.json();
        setConfig(data);
      }
    } catch (err) {
      console.error('Error fetching config:', err);
    }
  };

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status');
      if (res.ok) {
        const data = await res.json();
        setStatus(data);
      }
    } catch (err) {
      console.error('Error fetching status:', err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch('/api/logs');
      if (res.ok) {
        const data = await res.json();
        setLogs(data.logs || []);
      }
    } catch (err) {
      console.error('Error fetching logs:', err);
    }
  };

  const showToastNotification = (msg: string, success: boolean = true) => {
    setToast({ show: true, msg, success });
    setTimeout(() => {
      setToast(prev => ({ ...prev, show: false }));
    }, 3000);
  };

  const triggerAutosave = (updatedConfig: AppConfig) => {
    setConfig(updatedConfig);

    if (saveTimeout.current) clearTimeout(saveTimeout.current);
    saveTimeout.current = setTimeout(() => {
      saveConfigToServer(updatedConfig);
    }, 600);
  };

  const saveConfigToServer = async (payload: AppConfig) => {
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const updated = await res.json();
        setConfig(updated);
        showToastNotification('Settings autosaved successfully!', true);
      } else {
        throw new Error('Server returned an error');
      }
    } catch (err) {
      console.error('Error saving config:', err);
      showToastNotification('Failed to autosave settings', false);
    }
  };

  const restartRPC = async () => {
    if (window.confirm('Are you sure you want to restart the Valorant RPC application? The interface will reload automatically.')) {
      showToastNotification('Sending restart signal...', true);
      try {
        const res = await fetch('/api/restart', { method: 'POST' });
        if (res.ok) {
          setTimeout(() => {
            window.location.reload();
          }, 4000);
        }
      } catch (err) {
        showToastNotification('Failed to restart client', false);
      }
    }
  };

  const handleToggleRPC = (checked: boolean) => {
    if (!config) return;
    const copy = { ...config, rpc_enabled: checked };
    triggerAutosave(copy);
  };

  const handleRefreshIntervalChange = (val: number) => {
    if (!config) return;
    const copy = { ...config, presence_refresh_interval: val };
    triggerAutosave(copy);
  };

  const handleLargeImageChange = (val: string) => {
    if (!config) return;
    const copy = JSON.parse(JSON.stringify(config));
    if (!copy.presences) copy.presences = {};
    if (!copy.presences.modes) copy.presences.modes = {};
    if (!copy.presences.modes.all) copy.presences.modes.all = {};
    if (!copy.presences.modes.all.large_image) {
      copy.presences.modes.all.large_image = ['map', ['rank', 'agent', 'map']];
    }
    copy.presences.modes.all.large_image[0] = val;
    triggerAutosave(copy);
  };

  const handleSmallImageChange = (val: string) => {
    if (!config) return;
    const copy = JSON.parse(JSON.stringify(config));
    if (!copy.presences) copy.presences = {};
    if (!copy.presences.modes) copy.presences.modes = {};
    if (!copy.presences.modes.all) copy.presences.modes.all = {};
    if (!copy.presences.modes.all.small_image) {
      copy.presences.modes.all.small_image = ['agent', ['rank', 'agent', 'map']];
    }
    copy.presences.modes.all.small_image[0] = val;
    triggerAutosave(copy);
  };

  const handleToggleRankInCompLobby = (checked: boolean) => {
    if (!config) return;
    const copy = JSON.parse(JSON.stringify(config));
    if (!copy.presences) copy.presences = {};
    if (!copy.presences.menu) copy.presences.menu = {};
    copy.presences.menu.show_rank_in_comp_lobby = checked;
    triggerAutosave(copy);
  };

  const handleToggleRankInRange = (checked: boolean) => {
    if (!config) return;
    const copy = JSON.parse(JSON.stringify(config));
    if (!copy.presences) copy.presences = {};
    if (!copy.presences.modes) copy.presences.modes = {};
    if (!copy.presences.modes.range) copy.presences.modes.range = {};
    copy.presences.modes.range.show_rank_in_range = checked;
    triggerAutosave(copy);
  };

  const handleToggleAutoLaunchSkincli = (checked: boolean) => {
    if (!config) return;
    const copy = JSON.parse(JSON.stringify(config));
    if (!copy.startup) copy.startup = {};
    copy.startup.auto_launch_skincli = checked;
    triggerAutosave(copy);
  };

  const handleToggleShowGithubLink = (checked: boolean) => {
    if (!config) return;
    const copy = JSON.parse(JSON.stringify(config));
    if (!copy.startup) copy.startup = {};
    copy.startup.show_github_link = checked;
    triggerAutosave(copy);
  };

  const handleRegionChange = (val: string) => {
    if (!config) return;
    const copy = JSON.parse(JSON.stringify(config));
    if (!copy.region) copy.region = ['', []];
    copy.region[0] = val;
    triggerAutosave(copy);
  };

  const handleGameLaunchTimeoutChange = (val: number) => {
    if (!config) return;
    const copy = JSON.parse(JSON.stringify(config));
    if (!copy.startup) copy.startup = {};
    copy.startup.game_launch_timeout = val;
    triggerAutosave(copy);
  };

  const handlePresenceTimeoutChange = (val: number) => {
    if (!config) return;
    const copy = JSON.parse(JSON.stringify(config));
    if (!copy.startup) copy.startup = {};
    copy.startup.presence_timeout = val;
    triggerAutosave(copy);
  };


  const getLargeImageBackground = () => {
    const largeVal = config?.presences?.modes?.all?.large_image?.[0] || 'map';
    if (largeVal === 'map') {
      return 'url("https://raw.githubusercontent.com/colinhartigan/valorant-rpc/v2/assets/maps/haven.png")';
    } else if (largeVal === 'agent') {
      return 'url("https://raw.githubusercontent.com/colinhartigan/valorant-rpc/v2/assets/agents/jett.png")';
    } else {
      return 'url("https://raw.githubusercontent.com/colinhartigan/valorant-rpc/v2/assets/rank_icons/18.png")';
    }
  };

  const getSmallImageBackground = () => {
    const smallVal = config?.presences?.modes?.all?.small_image?.[0] || 'agent';
    if (smallVal === 'map') {
      return 'url("https://raw.githubusercontent.com/colinhartigan/valorant-rpc/v2/assets/maps/haven.png")';
    } else if (smallVal === 'agent') {
      return 'url("https://raw.githubusercontent.com/colinhartigan/valorant-rpc/v2/assets/agents/jett.png")';
    } else {
      return 'url("https://raw.githubusercontent.com/colinhartigan/valorant-rpc/v2/assets/rank_icons/18.png")';
    }
  };

  if (!config) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-[#060608]">
        <div className="flex flex-col items-center gap-4">
          <RefreshCw className="h-10 w-10 animate-spin text-[#bcb1e7]" />
          <p className="text-sm font-semibold tracking-wider text-neutral-400">LOADING DASHBOARD...</p>
        </div>
      </div>
    );
  }

  const tabMeta = {
    presence: {
      title: 'Presence Customizer',
      subtitle: 'Configure what images, ranks, and metadata appear on your Discord profile.',
    },
    privacy: {
      title: 'Privacy Settings',
      subtitle: 'Toggle which aspects of your Valorant game session are shared on Discord.',
    },
    system: {
      title: 'System & Timers',
      subtitle: 'Manage connection limits, account region, client settings, and timeouts.',
    },
    logs: {
      title: 'Console Logs',
      subtitle: 'View the live rpc.log console of your running Valorant RPC application.',
    },
  };

  return (
    <div className="relative flex h-screen w-screen overflow-hidden bg-[#060608]">
      <div className="grain-overlay" />

      <div className="glow-sphere sphere-1" />
      <div className="glow-sphere sphere-2" />

      <aside className="relative z-10 flex w-[280px] flex-col border-r border-white/5 bg-black/40 p-6 backdrop-blur-2xl">
        <div className="mb-10 flex items-center gap-3">
          <svg className="h-9 w-9 filter drop-shadow-[0_4px_10px_rgba(188,177,231,0.25)]" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M90 10H70L40 70H60L90 10Z" fill="url(#grad1)" />
            <path d="M60 10H40L10 70H30L60 10Z" fill="url(#grad2)" />
            <defs>
              <linearGradient id="grad1" x1="40" y1="70" x2="90" y2="10" gradientUnits="userSpaceOnUse">
                <stop stopColor="#bcb1e7" />
                <stop offset="1" stopColor="#9a8fd1" />
              </linearGradient>
              <linearGradient id="grad2" x1="10" y1="70" x2="60" y2="10" gradientUnits="userSpaceOnUse">
                <stop stopColor="#8172c9" />
                <stop offset="1" stopColor="#5d4da6" />
              </linearGradient>
            </defs>
          </svg>
          <div className="flex flex-col">
            <h1 className="m-0 bg-gradient-to-r from-white to-[#bcb1e7] bg-clip-text text-base font-bold tracking-wider text-transparent uppercase">
              Valorant RPC
            </h1>
            <span className="mt-0.5 self-start rounded bg-[#bcb1e7]/10 px-1.5 py-0.5 font-mono text-[9px] font-semibold text-[#bcb1e7] border border-[#bcb1e7]/20">
              {status?.version || 'v3.2.3'}
            </span>
          </div>
        </div>

        <div className="mb-6 flex items-center justify-between rounded-xl border border-white/5 bg-white/2 px-4 py-3 text-xs">
          <span className="font-semibold text-white">RPC Active</span>
          <label className="switch">
            <input
              type="checkbox"
              checked={config.rpc_enabled !== false}
              onChange={(e) => handleToggleRPC(e.target.checked)}
            />
            <span className="switch-slider" />
          </label>
        </div>

        <nav className="flex flex-1 flex-col gap-2">
          <button
            onClick={() => setActiveTab('presence')}
            className={`group flex items-center gap-3.5 rounded-xl px-4 py-3.5 text-left text-sm font-medium transition-all duration-300 relative overflow-hidden ${activeTab === 'presence'
              ? 'text-white bg-gradient-to-r from-[#bcb1e7]/10 to-transparent'
              : 'text-neutral-400 hover:text-white hover:bg-white/5 hover:pl-6'
              }`}
          >
            {activeTab === 'presence' && (
              <span className="absolute left-0 top-[20%] h-[60%] w-0.5 rounded bg-[#bcb1e7] shadow-[0_0_8px_#bcb1e7]" />
            )}
            <Sliders className={`h-4.5 w-4.5 ${activeTab === 'presence' ? 'text-[#bcb1e7]' : 'text-neutral-400 group-hover:text-white'}`} />
            <span>Presence Customizer</span>
          </button>

          <button
            onClick={() => setActiveTab('privacy')}
            className={`group flex items-center gap-3.5 rounded-xl px-4 py-3.5 text-left text-sm font-medium transition-all duration-300 relative overflow-hidden ${activeTab === 'privacy'
              ? 'text-white bg-gradient-to-r from-[#bcb1e7]/10 to-transparent'
              : 'text-neutral-400 hover:text-white hover:bg-white/5 hover:pl-6'
              }`}
          >
            {activeTab === 'privacy' && (
              <span className="absolute left-0 top-[20%] h-[60%] w-0.5 rounded bg-[#bcb1e7] shadow-[0_0_8px_#bcb1e7]" />
            )}
            <Shield className={`h-4.5 w-4.5 ${activeTab === 'privacy' ? 'text-[#bcb1e7]' : 'text-neutral-400 group-hover:text-white'}`} />
            <span>Privacy Settings</span>
          </button>

          <button
            onClick={() => setActiveTab('system')}
            className={`group flex items-center gap-3.5 rounded-xl px-4 py-3.5 text-left text-sm font-medium transition-all duration-300 relative overflow-hidden ${activeTab === 'system'
              ? 'text-white bg-gradient-to-r from-[#bcb1e7]/10 to-transparent'
              : 'text-neutral-400 hover:text-white hover:bg-white/5 hover:pl-6'
              }`}
          >
            {activeTab === 'system' && (
              <span className="absolute left-0 top-[20%] h-[60%] w-0.5 rounded bg-[#bcb1e7] shadow-[0_0_8px_#bcb1e7]" />
            )}
            <Settings className={`h-4.5 w-4.5 ${activeTab === 'system' ? 'text-[#bcb1e7]' : 'text-neutral-400 group-hover:text-white'}`} />
            <span>System & Timers</span>
          </button>

          <button
            onClick={() => setActiveTab('logs')}
            className={`group flex items-center gap-3.5 rounded-xl px-4 py-3.5 text-left text-sm font-medium transition-all duration-300 relative overflow-hidden ${activeTab === 'logs'
              ? 'text-white bg-gradient-to-r from-[#bcb1e7]/10 to-transparent'
              : 'text-neutral-400 hover:text-white hover:bg-white/5 hover:pl-6'
              }`}
          >
            {activeTab === 'logs' && (
              <span className="absolute left-0 top-[20%] h-[60%] w-0.5 rounded bg-[#bcb1e7] shadow-[0_0_8px_#bcb1e7]" />
            )}
            <Terminal className={`h-4.5 w-4.5 ${activeTab === 'logs' ? 'text-[#bcb1e7]' : 'text-neutral-400 group-hover:text-white'}`} />
            <span>Console Logs</span>
          </button>
        </nav>

        <div className="mt-auto flex flex-col gap-5">
          <div className="flex flex-col gap-2.5 rounded-2xl border border-white/5 bg-white/2 px-4 py-3.5 text-xs">
            <div className="flex items-center justify-between">
              <span className="text-neutral-400">Valorant status:</span>
              <span className={`font-semibold ${status?.is_valorant_running ? 'text-[#4ade80] drop-shadow-[0_0_5px_rgba(74,222,128,0.2)]' : 'text-neutral-500'}`}>
                {status?.is_valorant_running ? 'Running' : 'Offline'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-neutral-400">Discord status:</span>
              <span className={`font-semibold ${status?.is_discord_running ? 'text-[#4ade80] drop-shadow-[0_0_5px_rgba(74,222,128,0.2)]' : 'text-neutral-500'}`}>
                {status?.is_discord_running ? 'Connected' : 'Offline'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-neutral-400">Region:</span>
              <span className="font-semibold text-white uppercase">{status?.region || '-'}</span>
            </div>
          </div>

          <button
            onClick={restartRPC}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-white/5 bg-white/5 py-3 text-xs font-semibold text-white hover:bg-white/10 hover:border-white/10"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Restart RPC</span>
          </button>

          <a
            href="https://discord.gg/RJjMucjhbj"
            target="_blank"
            rel="noopener noreferrer"
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-[#5865F2]/20 bg-[#5865F2]/10 py-3 text-xs font-semibold text-white hover:bg-[#5865F2]/20 hover:border-[#5865F2]/30 active:scale-95"
          >
            <svg className="h-3.5 w-3.5 fill-current text-[#5865F2]" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028c.462-.63.874-1.295 1.226-1.994.021-.041.001-.09-.041-.106a13.094 13.094 0 0 1-1.873-.894.077.077 0 0 1-.008-.128c.126-.093.252-.19.372-.287a.075.075 0 0 1 .077-.011c3.92 1.793 8.18 1.793 12.061 0a.073.073 0 0 1 .078.009c.12.099.246.195.373.289a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.894.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.156-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.156 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.156-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.156 2.418z" />
            </svg>
            <span>Support Discord</span>
          </a>

          <div className="mt-2 flex items-center justify-center gap-1.5 text-[10px] text-neutral-500 font-medium">
            <span>maintained by bae with</span>
            <svg className="h-3 w-3 fill-current text-rose-500/80 animate-pulse" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
          </div>
        </div>
      </aside>

      <main className="relative z-10 flex flex-1 flex-col overflow-hidden px-10 py-8 h-screen">
        <header className="mb-8 flex items-center justify-between border-b border-white/5 pb-6">
          <div className="flex flex-col gap-1">
            <h2 className="m-0 text-xl font-bold tracking-tight text-white uppercase">
              {tabMeta[activeTab].title}
            </h2>
            <p className="text-xs font-medium text-neutral-400">
              {tabMeta[activeTab].subtitle}
            </p>
          </div>

          <div className="flex items-center gap-2.5 rounded-full border border-white/5 bg-white/3 px-4 py-2 text-xs font-semibold">
            <span className={`h-2 w-2 rounded-full ${status?.is_discord_running ? 'bg-[#4ade80] animate-pulse shadow-[0_0_8px_#4ade80]' : 'bg-[#ef4444] shadow-[0_0_8px_#ef4444]'}`} />
            <span className="text-neutral-200">
              {status?.is_discord_running ? 'RPC Active' : 'Waiting for connection'}
            </span>
          </div>
        </header>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-12 flex-1 min-h-0">
          <section className="lg:col-span-7 flex flex-col gap-6 rounded-2xl border border-white/5 bg-white/2 p-6 backdrop-blur-md min-h-0 h-full overflow-hidden">

            {activeTab === 'presence' && (
              <div className="animate-[pageEnter_0.4s_ease-out_forwards] flex flex-col gap-6 overflow-y-auto pr-1 flex-1 min-h-0">
                <div className="border-b border-white/5 pb-5">
                  <h3 className="m-0 mb-3 text-sm font-semibold tracking-wide text-white uppercase">General Presence Settings</h3>
                  <div className="flex flex-col gap-2">
                    <label className="text-xs font-semibold text-neutral-400">Refresh Interval (seconds)</label>
                    <div className="flex items-center gap-4">
                      <input
                        type="range"
                        min="1"
                        max="15"
                        value={config.presence_refresh_interval || 3}
                        onChange={(e) => handleRefreshIntervalChange(parseInt(e.target.value))}
                        className="h-1.5 flex-1 rounded bg-white/15 outline-none accent-[#bcb1e7]"
                      />
                      <span className="font-mono text-xs font-semibold text-[#bcb1e7]">
                        {config.presence_refresh_interval || 3}s
                      </span>
                    </div>
                    <span className="text-[10px] text-neutral-500">Determines how frequently your Rich Presence status updates.</span>
                  </div>
                </div>

                <div>
                  <h3 className="m-0 mb-4 text-sm font-semibold tracking-wide text-white uppercase">Mode Appearance (Default/All)</h3>
                  <div className="flex flex-col gap-4">
                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-semibold text-neutral-400">Large Image Content</label>
                      <select
                        value={config.presences?.modes?.all?.large_image?.[0] || 'map'}
                        onChange={(e) => handleLargeImageChange(e.target.value)}
                        className="rounded-xl border border-white/5 bg-[#121214] px-4 py-3 text-xs font-semibold text-white outline-none focus:border-[#bcb1e7] focus:shadow-[0_0_10px_rgba(188,177,231,0.15)]"
                      >
                        <option value="map">Map (Current map art)</option>
                        <option value="agent">Agent (Selected agent artwork)</option>
                        <option value="rank">Rank (Competitive rank badge)</option>
                      </select>
                    </div>

                    <div className="flex flex-col gap-2">
                      <label className="text-xs font-semibold text-neutral-400">Small Image Content</label>
                      <select
                        value={config.presences?.modes?.all?.small_image?.[0] || 'agent'}
                        onChange={(e) => handleSmallImageChange(e.target.value)}
                        className="rounded-xl border border-white/5 bg-[#121214] px-4 py-3 text-xs font-semibold text-white outline-none focus:border-[#bcb1e7] focus:shadow-[0_0_10px_rgba(188,177,231,0.15)]"
                      >
                        <option value="agent">Agent (Selected agent artwork)</option>
                        <option value="rank">Rank (Competitive rank badge)</option>
                        <option value="map">Map (Current map art)</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="animate-[pageEnter_0.4s_ease-out_forwards] flex flex-col gap-4 overflow-y-auto pr-1 flex-1 min-h-0">
                <div className="border-b border-white/5 pb-4">
                  <h3 className="m-0 mb-1.5 text-sm font-semibold tracking-wide text-white uppercase">Privacy Options</h3>
                  <p className="m-0 text-xs text-neutral-400">Customize which aspects of your current lobby or status are shared publicly.</p>
                </div>

                <div className="flex flex-col gap-3">
                  <div className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/1 px-5 py-4 transition hover:bg-white/3">
                    <div className="flex flex-col gap-1 pr-6">
                      <h4 className="m-0 text-xs font-semibold text-white">Show Rank in Competitive Lobby</h4>
                      <p className="m-0 text-[10px] text-neutral-400">Displays your competitive rank icon and rating inside the competitive queue lobby.</p>
                    </div>
                    <label className="switch">
                      <input
                        type="checkbox"
                        checked={!!config.presences?.menu?.show_rank_in_comp_lobby}
                        onChange={(e) => handleToggleRankInCompLobby(e.target.checked)}
                      />
                      <span className="switch-slider" />
                    </label>
                  </div>

                  <div className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/1 px-5 py-4 transition hover:bg-white/3">
                    <div className="flex flex-col gap-1 pr-6">
                      <h4 className="m-0 text-xs font-semibold text-white">Show Rank in Range</h4>
                      <p className="m-0 text-[10px] text-neutral-400">Displays your rank when practicing inside the Shooting Range.</p>
                    </div>
                    <label className="switch">
                      <input
                        type="checkbox"
                        checked={!!config.presences?.modes?.range?.show_rank_in_range}
                        onChange={(e) => handleToggleRankInRange(e.target.checked)}
                      />
                      <span className="switch-slider" />
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'system' && (
              <div className="animate-[pageEnter_0.4s_ease-out_forwards] flex flex-col gap-5 overflow-y-auto pr-1 flex-1 min-h-0">
                <div className="border-b border-white/5 pb-4">
                  <h3 className="m-0 mb-3 text-sm font-semibold tracking-wide text-white uppercase">App Connections & Region</h3>
                  <div className="flex flex-col gap-4">
                    <div className="flex flex-col gap-2">
                      <label className="text-[10px] font-semibold text-neutral-400 uppercase">Valorant Account Region</label>
                      <select
                        value={config.region?.[0] || ''}
                        onChange={(e) => handleRegionChange(e.target.value)}
                        className="rounded-xl border border-white/5 bg-[#121214] px-4 py-3 text-xs font-semibold text-white outline-none focus:border-[#bcb1e7]"
                      >
                        <option value="">Auto-Detect</option>
                        {config.region?.[1]?.map((reg) => (
                          <option key={reg} value={reg}>{reg.toUpperCase()}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                <div className="border-b border-white/5 pb-4">
                  <h3 className="m-0 mb-3 text-sm font-semibold tracking-wide text-white uppercase">Session Timeouts</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex flex-col gap-2">
                      <label className="text-[10px] font-semibold text-neutral-400 uppercase">Launch Timeout (sec)</label>
                      <input
                        type="number"
                        min="10"
                        max="300"
                        value={config.startup?.game_launch_timeout || 50}
                        onChange={(e) => handleGameLaunchTimeoutChange(parseInt(e.target.value))}
                        className="rounded-xl border border-white/5 bg-[#121214] px-4 py-3 text-xs font-semibold text-white outline-none focus:border-[#bcb1e7]"
                      />
                    </div>

                    <div className="flex flex-col gap-2">
                      <label className="text-[10px] font-semibold text-neutral-400 uppercase">Presence Timeout (sec)</label>
                      <input
                        type="number"
                        min="10"
                        max="300"
                        value={config.startup?.presence_timeout || 60}
                        onChange={(e) => handlePresenceTimeoutChange(parseInt(e.target.value))}
                        className="rounded-xl border border-white/5 bg-[#121214] px-4 py-3 text-xs font-semibold text-white outline-none focus:border-[#bcb1e7]"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="m-0 mb-3 text-sm font-semibold tracking-wide text-white uppercase">Advanced Client Settings</h3>
                  <div className="flex flex-col gap-3">
                    <div className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/1 px-5 py-4 transition hover:bg-white/3">
                      <div className="flex flex-col gap-0.5">
                        <h4 className="m-0 text-xs font-semibold text-white">Auto Launch skin-cli</h4>
                        <p className="m-0 text-[10px] text-neutral-400">Launches Valorant Skin CLI automatically when RPC starts.</p>
                      </div>
                      <label className="switch">
                        <input
                          type="checkbox"
                          checked={!!config.startup?.auto_launch_skincli}
                          onChange={(e) => handleToggleAutoLaunchSkincli(e.target.checked)}
                        />
                        <span className="switch-slider" />
                      </label>
                    </div>

                    <div className="flex items-center justify-between rounded-2xl border border-white/5 bg-white/1 px-5 py-4 transition hover:bg-white/3">
                      <div className="flex flex-col gap-0.5">
                        <h4 className="m-0 text-xs font-semibold text-white">Show Github Link</h4>
                        <p className="m-0 text-[10px] text-neutral-400">Add a button on your Discord status directing to the RPC source code.</p>
                      </div>
                      <label className="switch">
                        <input
                          type="checkbox"
                          checked={!!config.startup?.show_github_link}
                          onChange={(e) => handleToggleShowGithubLink(e.target.checked)}
                        />
                        <span className="switch-slider" />
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'logs' && (
              <div className="animate-[pageEnter_0.4s_ease-out_forwards] flex flex-1 flex-col gap-3 h-full min-h-0">
                <div className="flex items-center justify-between border-b border-white/5 pb-3">
                  <h3 className="m-0 text-sm font-semibold tracking-wide text-white uppercase">Application rpc.log</h3>
                  <button
                    onClick={() => setLogs([])}
                    className="rounded-lg border border-white/5 bg-white/5 px-3 py-1.5 text-[10px] font-bold text-white hover:bg-white/10"
                  >
                    Clear Console View
                  </button>
                </div>
                <div ref={logConsoleRef} className="flex-1 rounded-xl border border-white/5 bg-black/60 p-4 font-mono text-[10px] leading-relaxed overflow-y-auto shadow-inner min-h-0">
                  {logs.length === 0 ? (
                    <div className="text-neutral-500 italic">[SYSTEM] Log is empty or loading...</div>
                  ) : (
                    logs.map((line, idx) => {
                      let color = 'text-neutral-300';
                      if (line.includes('DEBUG') || line.includes('debug')) color = 'text-neutral-500';
                      else if (line.includes('WARNING') || line.includes('warn')) color = 'text-yellow-400';
                      else if (line.includes('ERROR') || line.includes('fail')) color = 'text-red-400';
                      else if (line.includes('SYSTEM') || line.includes('system')) color = 'text-[#bcb1e7]';

                      return (
                        <div key={idx} className={`${color} whitespace-pre-wrap break-all py-0.5`}>
                          {line}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            )}
          </section>

          <section className="lg:col-span-5 flex flex-col gap-4">
            <h3 className="m-0 text-sm font-bold tracking-tight text-white uppercase">Live Discord Preview</h3>
            <p className="m-0 -mt-2 text-xs text-neutral-400">See your Rich Presence exactly how it looks in Discord.</p>

            <div className="w-full max-w-[360px] overflow-hidden rounded-2xl border border-white/5 bg-[#111214] shadow-2xl transition-all duration-300 hover:scale-[1.01] hover:border-white/10">

              <div
                className="h-16 w-full relative"
                style={{
                  backgroundImage: status?.discord_user?.banner_url
                    ? `url('${status.discord_user.banner_url}')`
                    : 'none',
                  backgroundColor: status?.discord_user?.banner_color || '#bcb1e7',
                  backgroundSize: 'cover',
                  backgroundPosition: 'center'
                }}
              />

              <div className="p-4 relative">
                <div className="absolute -top-12 left-4 h-[76px] w-[76px] rounded-full border-6 border-[#111214] bg-[#2f3136] overflow-hidden">
                  {status?.discord_user?.avatar_url ? (
                    <img
                      src={status.discord_user.avatar_url}
                      className="h-full w-full object-cover"
                      alt="avatar"
                    />
                  ) : (
                    <svg className="h-full w-full text-white p-2" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect width="100" height="100" rx="50" fill="#5865F2" />
                      <path d="M72.3 32.6C66.8 30.1 60.9 28.3 54.7 27.5C53.9 28.8 53 30.7 52.4 32.3C45.8 31.3 39.2 31.3 32.7 32.3C32.1 30.7 31.1 28.8 30.3 27.5C24.1 28.3 18.2 30.1 12.7 32.6C1.6 49.2 -1.4 65.3 0.4 81.1C7.8 86.6 15 89.9 22 92.1C23.8 89.7 25.3 87.1 26.6 84.4C24.1 83.4 21.6 82.2 19.3 80.8C19.9 80.3 20.5 79.9 21.1 79.4C35.2 85.9 50.4 85.9 64.3 79.4C64.9 79.9 65.5 80.3 66.1 80.8C63.8 82.2 61.3 83.4 58.8 84.4C60.1 87.1 61.6 89.7 63.4 92.1C70.4 89.9 77.6 86.6 85 81.1C87.2 62.4 81.5 46.5 72.3 32.6ZM28.5 67.2C24.3 67.2 20.8 63.3 20.8 58.5C20.8 53.7 24.2 49.8 28.5 49.8C32.8 49.8 36.3 53.7 36.2 58.5C36.2 63.3 32.8 67.2 28.5 67.2ZM56.8 67.2C52.6 67.2 49.1 63.3 49.1 58.5C49.1 53.7 52.5 49.8 56.8 49.8C61.1 49.8 64.6 53.7 64.5 58.5C64.5 63.3 61.1 67.2 56.8 67.2Z" fill="white" />
                    </svg>
                  )}
                  <span className={`absolute bottom-0 right-0 h-4.5 w-4.5 rounded-full border-[3.5px] border-[#111214] ${status?.is_discord_running ? 'bg-[#23a55a]' : 'bg-[#80848e]'}`} />
                </div>

                <div className="mt-8 flex flex-col gap-0.5">
                  <div className="text-[13px] font-bold text-white leading-tight">
                    {status?.discord_user?.username || status?.player_name || 'Agent_Baeowsky'}
                  </div>
                  <div className="text-[10px] text-neutral-400">
                    Playing Valorant
                  </div>
                </div>

                <div className="h-[1px] w-full bg-white/5 my-3.5" />

                <div className="flex flex-col gap-3">
                  <span className="text-[10px] font-extrabold text-neutral-300 uppercase tracking-wider">
                    Playing a Game
                  </span>

                  <div className="flex gap-4">
                    <div className="relative shrink-0 h-20 w-20">
                      <div
                        className="h-20 w-20 rounded-lg border border-white/5 bg-cover bg-center bg-no-repeat"
                        style={{ backgroundImage: getLargeImageBackground() }}
                      />
                      <div
                        className="absolute -bottom-1.5 -right-1.5 h-[26px] w-[26px] rounded-full border-[2.5px] border-[#111214] bg-cover bg-center bg-no-repeat bg-[#2f3136]"
                        style={{ backgroundImage: getSmallImageBackground() }}
                      />
                    </div>

                    <div className="flex flex-col justify-center gap-0.5">
                      <div className="text-xs font-bold text-white">VALORANT</div>
                      <div className="text-[11px] text-neutral-300">{status?.game_info?.details || 'In Lobby'}</div>
                      <div className="text-[11px] text-neutral-300">{status?.game_info?.state || 'Competitive (1/5)'}</div>
                      <div className="text-[11px] font-medium text-neutral-400 mt-0.5">05:24 elapsed</div>
                    </div>
                  </div>

                  {config.startup?.show_github_link && (
                    <a
                      href="https://github.com/baeowsky/valorant-rpc"
                      target="_blank"
                      className="mt-2 flex w-full items-center justify-center gap-1.5 rounded bg-[#4e5058] py-2 text-xs font-semibold text-white hover:bg-[#6d6f78]"
                    >
                      <svg className="h-3.5 w-3.5 fill-current" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12" />
                      </svg>
                      <span>GitHub Repository</span>
                    </a>
                  )}
                </div>

              </div>
            </div>
          </section>
        </div>
      </main>

      <div
        className={`toast transition-all duration-500 ease-out z-[99999] ${toast.show ? 'translate-y-0 opacity-100' : 'translate-y-[100px] opacity-0 pointer-events-none'
          }`}
        style={{
          background: toast.success ? 'rgba(188, 177, 231, 0.95)' : 'rgba(239, 68, 68, 0.95)',
          color: toast.success ? '#060608' : '#ffffff',
          boxShadow: toast.success ? '0 10px 30px rgba(188, 177, 231, 0.25)' : '0 10px 30px rgba(239, 68, 68, 0.25)',
        }}
      >
        <div className="toast-icon">
          {toast.success ? (
            <svg className="h-4 w-4 stroke-current stroke-[3] fill-none" viewBox="0 0 24 24">
              <polyline points="20 6 9 17 4 12" />
            </svg>
          ) : (
            <svg className="h-4 w-4 stroke-current stroke-[3] fill-none" viewBox="0 0 24 24">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          )}
        </div>
        <span className="toast-message text-xs font-semibold">{toast.msg}</span>
      </div>
    </div>
  );
}