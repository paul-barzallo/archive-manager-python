# Module Ideation Workflow

Use this workflow when the user wants to brainstorm or select a new module to implement, but hasn't fully decided on the details yet.

## 1. Context Analysis & Review
- [ ] **Read Project Core**:
  - Read `docs/DOMAIN_MAP.md` to see what modules already exist.
  - Read `docs/ARCHITECTURE.md` to understand the system boundaries.
- [ ] **Identify Gaps**:
  - Look for obvious missing functionality based on "Archive Manager" goals (e.g., Tasks, Notes, Calendar, Projects).
  - Check `docs/DOMAIN_MAP.md` for "Future Modules (Planned)".

## 2. Brainstorming & Proposal
- [ ] **Generate Options**:
  - Create a list of 3-5 potential modules to implement next.
  - For each option, briefly describe:
    - **Name**: (e.g., `tasks`)
    - **Purpose**: One sentence description.
    - **Key Entities**: Main data objects (e.g., `Task`, `Category`).
    - **Value**: Why this should be next.
- [ ] **Present to User**:
  - Show the list to the user.
  - Ask: "Which of these sounds most important for the next step? Or do you have another idea?"

## 3. Definition & Refinement
- [ ] **Refine Selection**:
  - Once the user selects a module (e.g., "Let's do Tasks"), ask clarification questions to define the MVP scope.
  - *Example Questions*:
    - "Should this be simple (title + done status) or complex (due dates, priorities, tags)?"
    - "Does it need to link to existing modules (e.g., assign a Task to a Contact)?"
- [ ] **Draft the Plan**:
  - Outline the proposed entities and fields.
  - Outline the basic usage commands (CLI).
  - **STOP** and ask for user confirmation before proceeding to implementation.

## 4. Transition to Implementation
- [ ] **Handoff**:
  - Once the user confirms the plan (Entities, Scope, Features).
  - Trigger the **Module Implementation Workflow** (`.agents/workflows/module_implementation_workflow.md`).
