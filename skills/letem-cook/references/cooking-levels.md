# Cooking level and instruction detail

Use six independent dimensions. Store each as `unknown` or an integer from 1 through 10 in `profile.md`.

## Dimensions

- **Knife and prep:** safe cutting, ingredient preparation, organization, and tool setup.
- **Heat control:** burner and oven control, preheating, browning, doneness, and recovery from temperature changes.
- **Timing and multitasking:** sequencing components, parallel work, resting, holding, and finishing together.
- **Seasoning and tasting:** salting, balancing acid/sweetness/bitterness/umami, tasting, and correcting.
- **Technique range:** familiarity with cooking methods, doughs, sauces, proteins, grains, and cuisine-specific processes.
- **Recipe independence:** ability to work from ratios and sensory targets, substitute ingredients, troubleshoot, and cook without exhaustive steps.

Prefer the user's explicit self-rating. Treat one successful or unsuccessful dish as evidence, not a permanent score. After repeated evidence, propose a score change and explain why instead of silently changing it.

## Ten instruction levels

| Level | Instruction style |
| --- | --- |
| 1 | Define every term, list every tool, front-load all prep, give one action per numbered step, and include exact time, temperature, sensory cues, and safety warnings. |
| 2 | Keep fully guided steps and exact settings, but combine trivial setup actions; explain how to recognize each transition. |
| 3 | Give detailed beginner steps with times, temperatures, visual cues, and the most likely mistake at each critical stage. |
| 4 | Explain core techniques and decision points; omit definitions of common tools and basic actions unless safety depends on them. |
| 5 | Use standard recipe detail with quantities, sequence, timing ranges, and sensory doneness cues; call out only meaningful pitfalls. |
| 6 | Compress routine prep and focus on targets, coordination, substitutions, and recovery when timing or texture drifts. |
| 7 | Use concise steps with ratios, key temperatures, control points, and finishing order; assume routine techniques are familiar. |
| 8 | Provide an advanced outline centered on ratios, sequencing, sensory targets, and optional refinements. |
| 9 | Use terse expert notes: yield, ratios, critical temperatures, unusual hazards, and non-obvious control points. |
| 10 | Use professional shorthand and production sequencing; state only constraints, targets, yields, and deliberate variations unless more detail is requested. |

## Choose detail for a task

Use the most relevant known dimensions, not a single average for every recipe. A knife-heavy salad should follow `Knife and prep`; a steak should emphasize `Heat control`; a multi-dish dinner should emphasize `Timing and multitasking`. Use the lowest relevant score as the baseline, then compress portions governed by higher scores.

If every relevant score is `unknown`, ask once how much guidance the user wants. When the user needs an immediate answer, default to level 3 and say that the profile is not calibrated yet. Always honor an explicit request for more or less detail without changing the stored score automatically.
