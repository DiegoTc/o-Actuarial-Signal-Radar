# Canonical workflow schemas

Use [investigation_signal.schema.json](../../schemas/investigation_signal.schema.json) for the immutable handoff and [investigation_response.schema.json](../../schemas/investigation_response.schema.json) for the response. These are the single schema sources; copies here would drift.

The workflow result object contains `investigation`, `knowledge_citations` (registered ID plus excerpt SHA-256), and `model_execution` (`provider=amd_vllm`, exact configured model). This is the application-defined result contract; the native execution wrapper must be inspected in the Evolus workspace. `EVOLUS_RESULT_POINTER` selects that object. See the [workflow plan](../workflow/actuarial_signal_investigation.json).
