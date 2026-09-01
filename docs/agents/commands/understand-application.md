# understand-application

Use the shared Phase-2 CLI only after an approved KG exists. Run:

```powershell
python -m polaris_modernization.cli understand-application --kg-root artifacts/knowledge-graph/latest --output artifacts/application-understanding --provider auto
```

`auto` selects a configured enterprise provider or records `WAITING_FOR_PROVIDER_CONFIGURATION` without fabricating AI conclusions. Never bypass KG readiness or invent backend API mappings.
