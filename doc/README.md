# WikiOracle Docs
Updated: 2026-03-06

This directory is the design, governance, and research documentation for WikiOracle.

Recommended reading order:
1. `Constitution.md` (project invariants)
2. `WhatIsTruth.md` (plural truth, POVs, and certainty semantics)
3. `HierarchicalMixtureOfExperts.md` (HME logic, distributed truth vs consensus, conceptual spaces)
4. `Authority.md` (transitive trust and the authority import format)
5. `Logic.md` (logical operators: and/or/not/non under Strong Kleene semantics)
   - `Non.md` (non-affirming negation: Buddhist motivation, fuzzy interpretation, expressive necessity)
6. `Voting.md` (voting protocol: dom steering, sub fan-out, cycle prevention, truth-only output)
7. `FreedomEmpathyTruth.md` (Freedom, Empathy, and Truth — safety principles)
8. `Architecture.md` (current local-first software architecture)
9. `Config.md` (configuration format, settings reference, online training behavior)
10. `State.md` (state file format, conversation tree, truth table)
11. `Training.md` (DegreeOfTruth, Sensation preprocessing, online training pipeline, Hopfield dynamics)
12. `Entanglement.md` (worldline entanglement policy, spatiotemporal persistence, three-channel separation)
13. `Ethics.md` (ethical AI through truth architecture, symmetry constraints, LFGC)
14. `Security.md` (concrete security considerations)
15. `ProposedLicense.md` (licensing architecture)
16. `Installation.md` (build, deploy, and runtime instructions)
17. `FutureWork.md` (roadmap)
18. `WikiOracle.md` (consistency-first framing; document starts with "OpenMind")
19. `BuddhistLogic.md` (pramana theory, tetralemma, Kleene logic mapping)

## Core Documents (doc/)

- [`README.md`](./README.md): this index.
- [`Constitution.md`](./Constitution.md): the non-negotiable invariants for WikiOracle's truth system and governance.
- [`WhatIsTruth.md`](./WhatIsTruth.md): plural truth model, POVs, empathy as procedural constraint, HME fan-out, Kleene-style certainty.
- [`HierarchicalMixtureOfExperts.md`](./HierarchicalMixtureOfExperts.md): HME logic, Wikipedia-inspired distributed truth framing, conceptual spaces model.
- [`Authority.md`](./Authority.md): authority blocks (`<authority>`), transitive trust, certainty scaling, namespacing, and fetch/security constraints.
- [`Logic.md`](./Logic.md): logical operators (and/or/not/non); Strong Kleene evaluation; derived truth engine.
- [`Non.md`](./Non.md): non-affirming negation — Buddhist philosophical motivation (prasajya-pratisedha), fuzzy logic interpretation, and proof of expressive necessity.
- [`Voting.md`](./Voting.md): voting protocol — dom steering, sub fan-out, cycle prevention, `<feeling>` as truth type, truth-only output.
- [`FreedomEmpathyTruth.md`](./FreedomEmpathyTruth.md): Freedom, Empathy, and Truth — safety principles and architectural commitments.
- [`Security.md`](./Security.md): local-first security considerations (keys, CSP/XSS, CORS, filesystem, scraping/capture).
- [`Architecture.md`](./Architecture.md): implementation architecture (Flask shim + UI + `state.xml` state model).
- [`Config.md`](./Config.md): configuration format (`config.xml`), settings reference, environment variables, online training behavior.
- [`State.md`](./State.md): state file format (`state.xml`), conversation tree, truth table, serialization, merge.
- [`Training.md`](./Training.md): DegreeOfTruth (−1..+1), Korzybski IS detection (Sensation preprocessing), online training pipeline, checkpoint backup/restore, Hopfield network dynamics.
- [`Entanglement.md`](./Entanglement.md): worldline entanglement policy, spatiotemporal persistence, three-channel separation (knowing/learning/valuing).
- [`Ethics.md`](./Ethics.md): ethical AI through truth architecture, symmetry constraints, LFGC, and entanglement-resistant policy.
- [`ProposedLicense.md`](./ProposedLicense.md): licensing architecture — GPL-3.0 for code, CC BY-SA 4.0 for content, Apache-2.0 for weights.
- [`Installation.md`](./Installation.md): build, deploy, and runtime instructions.
- [`FutureWork.md`](./FutureWork.md): future directions (trust network, sentence-level prediction, conceptual-space operations, MCP integration).
- [`WikiOracle.md`](./WikiOracle.md): a consistency-first design note (historically labeled "OpenMind" in the text).
- [`BuddhistLogic.md`](./BuddhistLogic.md): Buddhist pramana theory, tetralemma interpretation, Kleene logic mapping.

Build, deploy, and runtime details are in [`Installation.md`](./Installation.md).
