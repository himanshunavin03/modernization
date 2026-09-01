# Developer Capabilities

Both developer interfaces call the shared `python -m polaris_modernization.cli` implementation. Deterministic Knowledge Graph extraction never uses an LLM.

## Interactive Agent Mode

`understand-application` is an interactive agent workflow, not a hosted-model runtime. Codex Chat or GitHub Copilot Chat first invokes Polaris to verify KG readiness and write compact evidence packages. The active chat agent reasons only over those packages, writes a structured `AgentReasoningSubmission`, and invokes Polaris again to validate evidence, API safety, and schema before artifacts are published.

No `OPENAI_API_KEY`, `POLARIS_LLM_PROVIDER`, or separately billed API connection is required. Polaris never reads, exposes, or reuses Codex/Copilot authentication.

## Codex

Codex uses repository `AGENTS.md` and the guide at `docs/agents/commands/understand-application.md`. This surface does not claim repository-defined slash-command autocomplete. Use the natural-language request: `Run the repository capability: understand-application`.

The agent runs the preparation command, reads only the resulting evidence packages/schema/instructions, creates the evidence-backed submission, and runs the validator command. It must not scan the full repository or canonical graph independently during the reasoning step.

## GitHub Copilot

In VS Code, use the Copilot Chat prompt-file picker and select `.github/prompts/understand-application.prompt.md`. The prompt is a thin interface over the same preparation and validation CLI. Repository-wide `.github/copilot-instructions.md` supplies the same evidence and API-safety boundary.

## Headless Enterprise Mode

Azure OpenAI and AWS Bedrock remain optional future server-side/headless provider adapters. They are intentionally separate from interactive agent mode and require their own enterprise credentials and optional dependencies. They are not invoked by Codex or Copilot interactive application understanding.
