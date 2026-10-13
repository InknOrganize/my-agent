# my-agent

Jarvis agent boot folder. Contains CLAUDE.md (boot config), tool configs, and the Etsy upload assets.

## New machine setup

1. Clone this repo into `C:\Users\<yourname>\my-agent`
2. Clone the vault: `git clone https://github.com/InknOrganize/Brain-Vault "C:\Users\<yourname>\Jarvis"`
3. Clone the subtools into the my-agent folder:
   ```
   git clone https://github.com/jaredrhod/backtalk my-agent/backtalk
   git clone https://github.com/jaredrhod/ai-visualizer my-agent/ai-visualizer
   git clone https://github.com/jaredrhod/ai-marketing-skills my-agent/ai-marketing-skills
   git clone https://github.com/jaredrhod/ai-memory-vault my-agent/ai-memory-vault
   git clone https://github.com/jaredrhod/fullstack-agent my-agent/fullstack-agent
   ```
4. Update the absolute paths in `backtalk/backtalk.json` and `ai-visualizer/ai-visualizer.json` to match the new machine's username.
5. Open Claude Code from inside the `my-agent` folder -- CLAUDE.md loads automatically.

## Tool configs

- `backtalk/backtalk.json` -- voice line config (paths are machine-specific, update after clone)
- `ai-visualizer/ai-visualizer.json` -- face display config (paths are machine-specific, update after clone)
