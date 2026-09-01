# Developer Capabilities

Both developer interfaces call the shared `python -m polaris_modernization.cli` implementation; no KG or Phase-2 logic is duplicated.

## Codex

Codex uses the repository `AGENTS.md` and command guides under `docs/agents/commands/`. This surface does not expose repository-defined slash-command discovery, so use a natural-language request such as: `Run the repository capability: create-knowledge-graph` or `Run the repository capability: understand-application`. The agent invokes the documented CLI entry point.

## GitHub Copilot

In VS Code, use the Copilot Chat prompt-file picker and select `.github/prompts/create-knowledge-graph.prompt.md` or `.github/prompts/understand-application.prompt.md`. These are supported reusable prompt files, not a replacement engine. Repository-wide `.github/copilot-instructions.md` supplies the shared safety boundary.

`create-knowledge-graph` is deterministic and uses effectively zero LLM tokens for core extraction. `understand-application` retrieves compact KG evidence packages, records token usage, and requires a configured real provider for AI-derived conclusions.

## Provider Configuration

Azure OpenAI requires `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_DEPLOYMENT`; `AZURE_OPENAI_API_VERSION` is optional. AWS Bedrock requires `AWS_REGION` and `POLARIS_BEDROCK_MODEL_ID`, with credentials supplied through the standard AWS credential chain. Do not commit any credential.
