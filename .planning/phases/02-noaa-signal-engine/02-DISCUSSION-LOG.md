# Phase 2: NOAA Signal Engine - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-18
**Phase:** 02-NOAA Signal Engine
**Areas discussed:** Forecast mapping, Probability derivation, Missing or fuzzy NOAA data, Signal evidence retention

---

## Forecast Mapping

| Option | Description | Selected |
|--------|-------------|----------|
| Configured city mapping only | Use a maintained mapping table from supported market locations to NOAA grid metadata. Most reliable for a narrow weather-only MVP. | ✓ |
| Dynamic lookup from location text | Resolve market locations on the fly from the parsed city name each time. More flexible, but adds lookup and ambiguity risk. | |
| Hybrid | Use a curated mapping table first, then fall back to dynamic lookup for unknown cities. More coverage, but more moving parts. | |
| You decide | Leave the final choice to the agent. | |

**User's choice:** Configured city mapping only
**Notes:** Start with a curated mapping table for supported cities.

---

## Probability Derivation

| Option | Description | Selected |
|--------|-------------|----------|
| Contract-family-specific rules | Use different derivation rules for temperature and precipitation markets, matching how each market actually resolves. | ✓ |
| One shared probability rule for all weather markets | Simpler implementation, but more likely to blur important differences between rain and temperature contracts. | |
| Start with precipitation only, defer temperature probability math | Safer and narrower, but reduces Phase 2 coverage. | |
| You decide | Leave the final choice to the agent. | |

**User's choice:** Contract-family-specific rules
**Notes:** User raised the idea of averaging across multiple weather sources. That was treated as a deferred idea because Phase 2 stays NOAA-only.

---

## Missing or Fuzzy NOAA Data

| Option | Description | Selected |
|--------|-------------|----------|
| Hard reject the signal and log why | Most conservative. Keeps bad mappings or weak data from leaking into paper-trading decisions. | ✓ |
| Mark it for review but do not produce a tradable signal | Slightly softer, but still blocks execution while preserving it for analysis. | |
| Use a fallback estimate when possible | More coverage, but adds judgment and weakens reproducibility. | |
| You decide | Leave the final choice to the agent. | |

**User's choice:** Hard reject the signal and log why
**Notes:** Weak or mismatched NOAA inputs must not produce tradable signals.

---

## Signal Evidence Retention

| Option | Description | Selected |
|--------|-------------|----------|
| Structured evaluation record | Store the key forecast inputs, mapping used, derived probability, market price, edge result, and rejection or acceptance reason. | ✓ |
| Full NOAA payload snapshot for every signal | Maximum audit detail, but more storage and schema complexity this early. | |
| Minimal final result only | Store just accept or reject and edge. Too thin for later inspection. | |
| You decide | Leave the final choice to the agent. | |

**User's choice:** Structured evaluation record
**Notes:** Auditability matters, but full raw NOAA snapshots are out of scope for this phase.

---

## the agent's Discretion

- Exact structured record schema
- Exact rejection code taxonomy
- Exact contract-family formulas within the locked decision to keep them family-specific and reproducible

## Deferred Ideas

- Multi-source weather consensus or averaging NOAA with another weather provider
