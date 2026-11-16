# AUTONOM Design System Specification

## 1. Vision & Architectural Philosophy

AUTONOM is a Windows 11 desktop application engineered for human oversight and control of autonomous AI agent swarms, computer automation, background job discovery, and application pipelines.

The user of AUTONOM is not browsing a marketing landing page; they are an operator supervising complex, asynchronous, mission-critical autonomous agents. Therefore, the design language prioritizes:

- **Information Density**: Maximum utility per screen pixel without visual clutter or cramped aesthetics.
- **Visual Restraint**: A disciplined dark palette inspired by modern Windows 11 system utilities, Bloomberg-style density, and professional developer workstations.
- **Absolute Elimination of Consumer Tropes**: Strict avoidance of neon gradients, purple/pink/gold iridescent glows, oversized pill buttons, exaggerated drop shadows, and consumer SaaS landing page layouts.
- **Predictable Hierarchy**: Consistent typographic scale, unified status semantics, and standardized layout wrappers across all views.
- **Accessibility by Default**: Strict adherence to WCAG 2.2 AA standards, ensuring full keyboard navigation, high contrast ratios, non-color-dependent state signaling, and motion reduction compliance.

---

## 2. Color System & Semantic Palette

The color system is defined via CSS custom properties in `tokens.css` and mapped to Tailwind utility classes in `tailwind.config.js`.

```
Surface Layering Model:
+--------------------------------------------------------------+
| Background Base (#0B1220)                                    |
|   +--------------------------------------------------------+ |
|   | Surface Secondary (#121E30)                            | |
|   |   +--------------------------------------------------+ | |
|   |   | Surface Default (#0F1828)                        | | |
|   |   |   +--------------------------------------------+ | | |
|   |   |   | Surface Elevated (#1B2B42)                 | | | |
|   |   |   | (Modals, Dropdowns, Cards, Popovers)       | | | |
|   |   |   +--------------------------------------------+ | | |
|   |   +--------------------------------------------------+ | |
|   +--------------------------------------------------------+ |
+--------------------------------------------------------------+
```

### Core Palette Values

| Token Name             | Hex Code  | Semantic Role                                               |
| :--------------------- | :-------- | :---------------------------------------------------------- |
| `background`           | `#0B1220` | Root canvas / deep dark navy base                           |
| `surface`              | `#0F1828` | Primary container & operational panel background            |
| `surface-secondary`    | `#121E30` | Sub-panels, sidebar canvas, input backgrounds               |
| `surface-elevated`     | `#1B2B42` | Dialogs, dropdown menus, floating tooltips, table rows      |
| `surface-hover`        | `#233652` | Interactive element hover states                            |
| `surface-selected`     | `#203859` | Selected rows, active navigation tabs                       |
| `border`               | `#2A3A52` | Structural borders, dividers, subtle outlines               |
| `border-focused`       | `#338BDF` | Keyboard focus rings & active input boundaries              |
| `primary`              | `#338BDF` | Core action blue, primary buttons, active highlights        |
| `primary-hover`        | `#4A9AED` | Primary interactive hover state                             |
| `primary-active`       | `#2473BF` | Primary button pressed state                                |
| `cyan`                 | `#51C8E8` | Secondary accent, technical IDs, active telemetry, progress |
| `foreground`           | `#F0F5FC` | High-contrast body text, headings, prominent numbers        |
| `foreground-secondary` | `#A7B6CB` | Secondary labels, descriptions, sub-headings                |
| `foreground-muted`     | `#8495AC` | Metadata, timestamps, inactive icons                        |
| `status-success`       | `#37B89A` | Online status, completed tasks, integrity verified          |
| `status-warning`       | `#E3AA54` | User intervention required, rate limits, alerts             |
| `status-error`         | `#E36E78` | Sidecar disconnects, task failures, critical aborts         |
| `status-inactive`      | `#64748B` | Idle workers, stopped background services                   |

---

## 3. Typography & Numerical Representation

AUTONOM employs Segoe UI Variable for native Windows 11 interface typography, with specialized font features for technical telemetry:

- **Tabular Figures (`tnum`)**: All counters, latency indicators, execution progress values, and table figures utilize tabular numbers to prevent horizontal layout jitter during real-time streaming updates.
- **Technical Monospace**: Monospace fonts (`Consolas`, `Cascadia Code`, `ui-monospace`) are dedicated to process IDs, hash digests, endpoints, memory addresses, and file paths.

```
Type Scale Hierarchy:
- Display Metric:   24px / 32px (font-semibold, font-tabular)
- Page Title:       20px / 28px (font-bold, tracking-tight)
- Section Title:    14px / 20px (font-semibold, text-foreground)
- Standard Body:    13px / 18px (font-normal, text-foreground)
- Compact Body:     12px / 16px (font-normal, text-foreground-secondary)
- Technical / Mono: 11px / 14px (font-mono-tech, text-foreground-muted)
```

---

## 4. Density Modes & Workstation Adaptability

Desktop operators frequently manage multi-monitor, high-DPI setups with differing information density preferences. AUTONOM supports dynamic density switching via CSS tokens and `ThemeContext`:

1. **Comfortable Density (`data-density="comfortable"`)**:
   - Standard 36px inputs and buttons.
   - 16px to 24px container padding.
   - Ideal for standard laptop and 1080p desktop viewing.

2. **Compact Density (`data-density="compact"`)**:
   - 28px dense inputs and buttons.
   - 8px to 12px container padding.
   - 32px table row height.
   - Maximizes data throughput for 4K / ultrawide multi-window oversight.

The operator's density choice is instantly persisted to `localStorage` and toggled via the header quick-action pill or API.

---

## 5. Architectural Directory Layout

The component library is organized into discrete domain packages within `apps/desktop/src/components`:

```
apps/desktop/src/
├── components/
│   ├── ui/               # Core accessible primitives (Radix UI + CVA)
│   │   ├── button.tsx, input.tsx, textarea.tsx, checkbox.tsx
│   │   ├── switch.tsx, select.tsx, badge.tsx, progress.tsx
│   │   ├── skeleton.tsx, separator.tsx, tooltip.tsx, dialog.tsx
│   │   ├── dropdown-menu.tsx, tabs.tsx
│   │   └── index.ts
│   ├── layout/           # Desktop viewport scaffolding
│   │   ├── PageContainer.tsx
│   │   ├── SectionHeader.tsx
│   │   ├── SplitPanel.tsx
│   │   └── index.ts
│   ├── data-display/     # Structured telemetry displays
│   │   ├── MetricCard.tsx
│   │   ├── StatusCard.tsx
│   │   ├── DataTable.tsx
│   │   ├── EmptyState.tsx
│   │   └── index.ts
│   ├── charts/           # Dark responsive visualizers (Recharts)
│   │   ├── ChartContainer.tsx
│   │   ├── LineChart.tsx
│   │   ├── BarChart.tsx
│   │   ├── DonutChart.tsx
│   │   └── index.ts
│   └── feedback/         # Operational state signaling
│       ├── ErrorState.tsx
│       ├── LoadingState.tsx
│       ├── Toast.tsx
│       └── index.ts
├── design-system/
│   ├── tokens.ts         # TypeScript palette constants
│   ├── ThemeContext.tsx  # React density provider & persistence
│   └── index.ts
└── styles/
    ├── tokens.css        # CSS Custom Properties (:root & [data-density])
    ├── typography.css    # Font utilities, tabular figures, monospace
    └── globals.css       # Global reset & Tailwind directives
```

---

## 6. Accessibility & Compliance (WCAG 2.2 AA)

1. **Contrast Ratios**: All text tokens against their respective surface backgrounds exceed 4.5:1. Border outlines and active indicators exceed 3:1 against adjacent surfaces.
2. **Keyboard Navigation**: Full focus trap within modals, escape dismissal, arrow key tab navigation, and clear 2px primary focus rings (`focus-visible:ring-primary`).
3. **Non-Color Signals**: All statuses couple color indicators with textual labels and explicit iconography (e.g., checkmarks for success, warning triangles for alerts).
4. **Motion Preferences**: `@media (prefers-reduced-motion: reduce)` automatically disables transition and pulse animations.
