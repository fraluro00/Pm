# Frontend Codebase

NextJS 16 app (React 19, TypeScript, Tailwind CSS v4). Pure client-side Kanban demo — no backend calls yet.

## Stack

- **NextJS 16** with App Router, static export target
- **React 19** with `"use client"` components
- **Tailwind CSS v4** via PostCSS, configured in `globals.css` with CSS custom properties
- **@dnd-kit** for drag-and-drop (core, sortable, utilities)
- **Vitest** for unit tests, **Playwright** for e2e tests
- **Fonts:** Space Grotesk (`--font-display`) + Manrope (`--font-body`) from next/font/google

## Color Tokens (CSS custom properties in globals.css)

| Token | Value | Usage |
|---|---|---|
| `--accent-yellow` | `#ecad0a` | Column accent bars, highlights |
| `--primary-blue` | `#209dd7` | Links, key sections |
| `--secondary-purple` | `#753991` | Submit buttons, important actions |
| `--navy-dark` | `#032147` | Main headings |
| `--gray-text` | `#888888` | Supporting text, labels |
| `--surface` | `#f7f8fb` | Page background |
| `--surface-strong` | `#ffffff` | Card/column backgrounds |
| `--stroke` | `rgba(3,33,71,0.08)` | Borders |
| `--shadow` | `0 18px 40px rgba(3,33,71,0.12)` | Shadows |

## File Structure

```
src/
  app/
    layout.tsx        — root layout, font loading, metadata
    page.tsx          — renders <KanbanBoard />
    globals.css       — Tailwind import + CSS custom properties
  components/
    KanbanBoard.tsx   — top-level board; owns all state
    KanbanColumn.tsx  — single column; droppable zone + sortable list
    KanbanCard.tsx    — single card; sortable, has delete button
    KanbanCardPreview.tsx — drag overlay preview (no delete button)
    NewCardForm.tsx   — inline form toggled per column
  lib/
    kanban.ts         — types, initialData, moveCard, createId
    kanban.test.ts    — unit tests for moveCard
  test/
    setup.ts          — vitest/jsdom setup with @testing-library/jest-dom
    vitest.d.ts       — type augmentation for jest-dom matchers
tests/
  kanban.spec.ts      — Playwright e2e tests
```

## Data Model (lib/kanban.ts)

```typescript
type Card = { id: string; title: string; details: string }
type Column = { id: string; title: string; cardIds: string[] }
type BoardData = { columns: Column[]; cards: Record<string, Card> }
```

- `initialData` — hardcoded seed: 5 columns (Backlog, Discovery, In Progress, Review, Done), 8 cards
- `moveCard(columns, activeId, overId)` — pure function; handles same-column reorder and cross-column move
- `createId(prefix)` — generates `prefix-<random><timestamp>` IDs

## State Management (KanbanBoard.tsx)

All state lives in `KanbanBoard` as a single `BoardData` object via `useState`. Handlers passed down as props:

- `handleRenameColumn(columnId, title)` — updates column title in place
- `handleAddCard(columnId, title, details)` — creates card, appends to column
- `handleDeleteCard(columnId, cardId)` — removes card from map and from column
- `handleDragEnd` — calls `moveCard`, updates `columns` array

## Drag and Drop

Uses `DndContext` (closestCorners strategy) wrapping all columns. Each `KanbanColumn` is a `useDroppable` zone. Each `KanbanCard` is `useSortable`. `DragOverlay` renders `KanbanCardPreview` during drag. Activation requires 6px pointer movement to avoid accidental drags.

## What Does NOT Exist Yet

- No backend API calls (all state is in-memory, resets on refresh)
- No authentication / login page
- No AI sidebar
- No persistence
