# my-agent

Jarvis agent boot folder. Contains CLAUDE.md (boot config), launcher, and Etsy upload assets.

## New machine setup

Open PowerShell and run these in order:

```powershell
# 1. Install Claude Code
winget install Anthropic.ClaudeCode

# 2. Install Git (if not already there)
winget install Git.Git

# 3. Install Obsidian
winget install Obsidian.Obsidian

# 4. Clone the vault and this repo
git clone https://github.com/InknOrganize/Brain-Vault "C:\Users\Ryan Eckalook\Jarvis"
git clone https://github.com/InknOrganize/my-agent "C:\Users\Ryan Eckalook\my-agent"

# 5. Clone the subtools into my-agent
git clone https://github.com/jaredrhod/backtalk "C:\Users\Ryan Eckalook\my-agent\backtalk"
git clone https://github.com/jaredrhod/ai-visualizer "C:\Users\Ryan Eckalook\my-agent\ai-visualizer"
git clone https://github.com/jaredrhod/ai-marketing-skills "C:\Users\Ryan Eckalook\my-agent\ai-marketing-skills"
git clone https://github.com/jaredrhod/ai-memory-vault "C:\Users\Ryan Eckalook\my-agent\ai-memory-vault"
git clone https://github.com/jaredrhod/fullstack-agent "C:\Users\Ryan Eckalook\my-agent\fullstack-agent"
```

## After cloning -- update the two config files

These files have hardcoded paths that need updating for this machine.

**backtalk/backtalk.json** -- change both path values:
```json
{
  "agent_dir": "C:/Users/Ryan Eckalook/my-agent",
  "name": "Jarvis",
  "extra_dirs": ["C:/Users/Ryan Eckalook/Jarvis"],
  "ptt_key": "home",
  "mic_mode": "ptt",
  "voice": "bm_lewis",
  "stt_model": "small.en",
  "greeting": "All systems online, sir. What are we working on today?"
}
```

**ai-visualizer/ai-visualizer.json** -- change the bus_dir value:
```json
{
  "name": "Jarvis",
  "badge": "",
  "face": "board",
  "port": 8790,
  "bus_dir": "C:/Users/Ryan Eckalook/my-agent/backtalk",
  "thinking_sound": true
}
```

## Launch

Double-click `launch-jarvis.bat` -- it cds into my-agent and opens Claude Code automatically.
