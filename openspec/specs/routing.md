# Routing Specification

## Overview
The MCP server routes user requests across a Gemini model pool to optimize cost, latency, and capability. Routing is driven by a Triage Engine that produces a structured `RouteDecision` used by a Dynamic Dispatcher.

## Model Pool
- gemini-2.5-pro: complex reasoning, code/STEM, long context
- gemini-2.5-flash: balanced performance, function calling
- gemini-2.5-flash-lite: fastest/cost-efficient, triage, classification
- gemini-2.0-flash: legacy fallback

## Triage Engine
- Model: gemini-2.5-flash-lite
- Output schema (Pydantic):
  - task_type: CODE_GEN | COMPLEX_ANALYSIS | SIMPLE_QUERY | etc.
  - model_preference: target Gemini model id
  - confidence_score: 0.0..1.0

## Dispatcher Policy
- CODE_GEN/COMPLEX_ANALYSIS → gemini-2.5-pro (if available)
- GENERAL/TOOLS/QA → gemini-2.5-flash
- SIMPLE_QUERY/CLASSIFY → gemini-2.5-flash-lite
- Fallback hierarchy: pro → flash → flash-lite → 2.0-flash

## Implementation Notes
- Enforce Pydantic schemas as single source of truth for:
  - MCP `tools/list` JSON Schemas
  - Gemini Function Declarations
  - Internal triage/dispatch DTOs
- Keep routing decisions fast; avoid expensive models for triage.
- Consider real-time signals in future (model load, tail latency).
