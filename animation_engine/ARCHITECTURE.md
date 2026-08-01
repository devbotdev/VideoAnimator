# VideoAnimator Architecture

VideoAnimator is a modular, pipeline-based system designed to translate high-level creative ideas into executable animation plans using Large Language Models (LLMs).

## Pipeline Architecture

The system utilizes an orchestrator-based pipeline pattern to manage the transformation of an idea into a final animation plan.

### Core Components
- **`PipelineOrchestrator`**: The central controller that executes a sequence of stages.
- **`PipelineContext`**: A shared state container passed between stages. It holds intermediate data (`creative_brief`, `narrative_structure`, etc.) and handles debugging outputs.
- **`PipelineStage`**: A protocol defining the interface for all processing steps. Each stage must implement a `run(context: PipelineContext)` method.

### Adding a New Stage
To add a new stage to the pipeline:
1.  Define a new class that implements the `PipelineStage` protocol in `animation_engine/pipeline/` or `animation_engine/director/`.
2.  In the `run` method, retrieve required data from `context.get()` and store results using `context.set()`.
3.  Instantiate the class and add it to the `PipelineOrchestrator` instance using `add_stage()`.

## Agent Responsibilities

The system leverages AI agents to handle specific creative and technical tasks. The `AIConnection` class acts as the interface to these agents.

| Agent Role | Responsibility |
| :--- | :--- |
| **Director** | Handles creative strategy (Idea -> Creative Brief -> Narrative Structure -> Visual Concept -> Storyboard -> Animation Plan -> Review) |
| **Engineer** | Handles technical translation (Animation Plan -> Engine Plan) and plan repair |

## Prompt Management

Prompts are managed as markdown files located in `animation_engine/ai/`. 
- They are automatically loaded by the `AIConnection` class upon initialization.
- To update a prompt, modify the corresponding `.md` file in the `animation_engine/ai/` directory.

## Model Configuration

Model selection is configurable via `config/models.json`.

```json
{
  "google": {
    "director": "gemini-3.1-flash-lite",
    "engineer": "gemini-3.1-flash-lite"
  },
  "local": {
    "director": "Qwen/Qwen2.5-7B-Instruct-GGUF:Q4_K_M",
    "engineer": "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M"
  }
}
```

- Models are mapped by **role** (director, engineer) and **provider** (google, local).
- `AIConnection` loads this file to determine which model to use for a given role based on the configured `provider_type`.

## Debugging

Debugging is integrated into the `PipelineContext`.
- When `debug_enabled` is set to `True` in `PipelineContext`, stages can call `context.save_debug_data(stage_name, data)`.
- This automatically serializes the data and saves it as a JSON file in the designated debug directory, providing visibility into the pipeline state at each stage.
