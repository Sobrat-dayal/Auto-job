# AUTONOM Design Token Reference

This document catalogs all CSS custom properties and design tokens utilized across the AUTONOM desktop application shell and component library.

All tokens are defined in `apps/desktop/src/styles/tokens.css` and exposed as Tailwind CSS utility classes in `apps/desktop/tailwind.config.js`.

---

## 1. Palette Tokens

### Surface & Canvas Tokens

| CSS Variable                | Tailwind Class         | Value     | Description                                   |
| :-------------------------- | :--------------------- | :-------- | :-------------------------------------------- |
| `--color-background`        | `bg-background`        | `#0B1220` | Root desktop canvas background                |
| `--color-surface`           | `bg-surface`           | `#0F1828` | Main content cards & container panels         |
| `--color-surface-secondary` | `bg-surface-secondary` | `#121E30` | Sub-panels, sidebar canvas, input surfaces    |
| `--color-surface-elevated`  | `bg-surface-elevated`  | `#1B2B42` | Dialogs, popovers, dropdown menus, table rows |
| `--color-surface-hover`     | `bg-surface-hover`     | `#233652` | Interactive hover states                      |
| `--color-surface-selected`  | `bg-surface-selected`  | `#203859` | Selected navigation items & table rows        |
| `--color-surface-disabled`  | `bg-surface-disabled`  | `#162030` | Disabled inputs and control backgrounds       |

---

### Border & Divider Tokens

| CSS Variable             | Tailwind Class          | Value     | Description                           |
| :----------------------- | :---------------------- | :-------- | :------------------------------------ |
| `--color-border`         | `border-border`         | `#2A3A52` | Default component and panel border    |
| `--color-border-subtle`  | `border-border-subtle`  | `#1E2B3E` | Card sub-dividers and inner borders   |
| `--color-border-focused` | `border-border-focused` | `#338BDF` | Keyboard focus ring and active border |

---

### Brand & Accent Tokens

| CSS Variable             | Tailwind Class               | Value     | Description                       |
| :----------------------- | :--------------------------- | :-------- | :-------------------------------- |
| `--color-primary`        | `bg-primary`, `text-primary` | `#338BDF` | Core action blue                  |
| `--color-primary-hover`  | `hover:bg-primary-hover`     | `#4A9AED` | Primary interactive hover         |
| `--color-primary-active` | `active:bg-primary-active`   | `#2473BF` | Primary button pressed state      |
| `--color-cyan`           | `bg-cyan`, `text-cyan`       | `#51C8E8` | Secondary electric cyan highlight |
| `--color-cyan-hover`     | `hover:bg-cyan-hover`        | `#6BD3F0` | Cyan interactive hover            |

---

### Text & Foreground Tokens

| CSS Variable                   | Tailwind Class              | Value     | Description                             |
| :----------------------------- | :-------------------------- | :-------- | :-------------------------------------- |
| `--color-foreground`           | `text-foreground`           | `#F0F5FC` | High-contrast primary text and headers  |
| `--color-foreground-secondary` | `text-foreground-secondary` | `#A7B6CB` | Secondary descriptions and labels       |
| `--color-foreground-muted`     | `text-foreground-muted`     | `#8495AC` | Metadata, timestamps, inactive elements |
| `--color-foreground-disabled`  | `text-foreground-disabled`  | `#4F6078` | Disabled text content                   |

---

### Status Indicators

| CSS Variable              | Tailwind Class                               | Value     | Description                          |
| :------------------------ | :------------------------------------------- | :-------- | :----------------------------------- |
| `--color-status-success`  | `text-status-success`, `bg-status-success`   | `#37B89A` | Online, healthy, completed, verified |
| `--color-status-warning`  | `text-status-warning`, `bg-status-warning`   | `#E3AA54` | Awaiting approval, degraded, queued  |
| `--color-status-error`    | `text-status-error`, `bg-status-error`       | `#E36E78` | Failure, abort, disconnected, error  |
| `--color-status-inactive` | `text-status-inactive`, `bg-status-inactive` | `#64748B` | Idle, offline, disabled              |

---

## 2. Density & Sizing Tokens

AUTONOM adapts sizing via CSS variables switched on the root `[data-density]` attribute:

| Token Name                   | Comfortable (`[data-density="comfortable"]`) | Compact (`[data-density="compact"]`) |
| :--------------------------- | :------------------------------------------- | :----------------------------------- |
| `--density-page-padding`     | `1.5rem` (24px)                              | `1.0rem` (16px)                      |
| `--density-section-gap`      | `1.5rem` (24px)                              | `1.0rem` (16px)                      |
| `--density-input-height`     | `2.25rem` (36px)                             | `1.75rem` (28px)                     |
| `--density-btn-height`       | `2.25rem` (36px)                             | `1.75rem` (28px)                     |
| `--density-card-padding`     | `1.0rem` (16px)                              | `0.75rem` (12px)                     |
| `--density-table-row-height` | `2.5rem` (40px)                              | `2.0rem` (32px)                      |

---

## 3. Radii & Shadow Tokens

| Token Name          | Value                             | Purpose                                   |
| :------------------ | :-------------------------------- | :---------------------------------------- |
| `--radius-sm`       | `0.25rem` (4px)                   | Inputs, buttons, badges                   |
| `--radius-md`       | `0.375rem` (6px)                  | Cards, modals, containers                 |
| `--radius-lg`       | `0.5rem` (8px)                    | Application root dialogs and panels       |
| `--shadow-subtle`   | `0 1px 2px 0 rgba(0, 0, 0, 0.4)`  | Card and input elevation                  |
| `--shadow-elevated` | `0 4px 12px 0 rgba(0, 0, 0, 0.6)` | Modals, dropdown menus, floating tooltips |
