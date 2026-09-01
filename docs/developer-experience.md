# Developer Capabilities

Both developer interfaces call the shared `python -m polaris_modernization.cli` implementation; no KG or Phase-2 logic is duplicated.

## Codex

Codex uses the repository `AGENTS.md` and command guides under `docs/agents/commands/`. This surface does not expose repository-defined slash-command discovery, so use a natural-language request such as: `Run the repository capability: create-knowledge-graph` or `Run the repository capability: understand-application`. The agent invokes the documented CLI entry point.

## GitHub Copilot

In VS Code, use the Copilot Chat prompt-file picker and select `.github/prompts/create-knowledge-graph.prompt.md` or `.github/prompts/understand-application.prompt.md`. These are supported reusable prompt files, not a replacement engine. Repository-wide `.github/copilot-instructions.md` supplies the shared safety boundary.

`create-knowledge-graph` is deterministic and uses effectively zero LLM tokens for core extraction. `understand-application` retrieves compact KG evidence packages, records token usage, and requires a configured real provider for AI-derived conclusions.

## Provider Configuration

`create-knowledge-graph` remains deterministic and does not require an LLM or an API key. `understand-application` supports provider-independent LangChain structured reasoning only after the approved KG gate passes.

### Local OpenAI Demo

Install the optional local provider once:

```powershell
python -m pip install -e ".[openai]"
```

Set secrets only in the current PowerShell session, then run the shared capability. Do not put the key in a repository file, artifact, cache, or command history intended for sharing.

```powershell
$env:POLARIS_LLM_PROVIDER = 'openai'
$env:OPENAI_API_KEY = '<local secret>'
$env:POLARIS_OPENAI_MODEL = 'gpt-4o-mini' # optional default
python -m polaris_modernization.cli understand-application --kg-root artifacts/knowledge-graph/latest --output artifacts/application-understanding --provider auto
```

If `POLARIS_LLM_PROVIDER=openai` is selected without `OPENAI_API_KEY`, the workflow records `WAITING_FOR_PROVIDER_CONFIGURATION` and makes no model call. Each deterministic evidence package is reasoned over separately, with no source text or complete KG sent to the provider; stable package hashes prevent repeat calls for unchanged packages. Exact provider usage metadata is recorded when returned.

### Enterprise Providers

Azure OpenAI requires `POLARIS_LLM_PROVIDER=azure`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_DEPLOYMENT`; `AZURE_OPENAI_API_VERSION` is optional. AWS Bedrock requires `POLARIS_LLM_PROVIDER=bedrock`, `AWS_REGION`, and `POLARIS_BEDROCK_MODEL_ID`, with credentials supplied through the standard AWS credential chain. Do not commit any credential.
