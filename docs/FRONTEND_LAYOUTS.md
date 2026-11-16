# AUTONOM Frontend Layout Architecture

## 1. Desktop Shell Layout Architecture

AUTONOM implements a native desktop application shell designed to run in a fixed-viewport Windows 11 window managed by Tauri 2.

```
+------------------------------------------------------------------------------------+
| Header (48px / h-12)                                                               |
| [App Name + Stage]            [Native Win32 Telemetry]      [Uptime + Status Badge]|
+------------------------------------------------------------------------------------+
| Sidebar (56px-224px) | Main Viewport (flex-1 overflow-y-auto)                      |
|                      |                                                             |
| - Navigation Items   | PageContainer                                               |
| - Collapse Toggle    | +---------------------------------------------------------+ |
| - Stage Notice       | | Header: Title + Subtitle + Actions                      | |
|                      | +---------------------------------------------------------+ |
|                      | | Metric Cards Row (grid-cols-4)                          | |
|                      | +---------------------------------------------------------+ |
|                      | | Subsystem Status / Operational Workstation              | |
|                      | | (SplitPanel / DataTable / Analytics)                    | |
|                      | +---------------------------------------------------------+ |
+------------------------------------------------------------------------------------+
```

---

## 2. Core Layout Elements

### Application Header (`components/Header.tsx`)

- Fixed height: 48px (`h-12`).
- Boundaries: Bottom border with `--color-border`.
- Contents:
  - Left: AUTONOM branding logo, version chip, native OS platform (`Windows 11 x64`).
  - Right: Stage status badge, live service uptime counter, connection state badge, quick density toggle button, and global task shortcut helper (`Ctrl+Shift+Esc`).

### Sidebar Navigation (`components/Sidebar.tsx`)

- Width: Expandable from 56px (`w-14` collapsed icon mode) to 224px (`w-56` full text mode).
- Features: Active navigation highlighting with primary border, development phase flags (`v2` badges for future stage modules), and bottom footer with stage progression metadata.

### Page Container (`components/layout/PageContainer.tsx`)

- Centered, density-aware responsive container (`max-w-7xl mx-auto`).
- Standardized header containing page title, subtitle, stage badge, and top-right primary actions.
- Automatically adjusts vertical and horizontal padding based on `data-density="comfortable"` or `"compact"`.

### Split Panel (`components/layout/SplitPanel.tsx`)

- Supports responsive side-by-side or stacked master-detail views.
- Allows dedicating a fixed column ratio (e.g. 35% master list / 65% detail editor) for agent task monitoring, computer-control inspection, and workflow orchestration.

---

## 3. High-DPI & Windows 11 Scaling

AUTONOM is optimized for Windows 11 desktop display scaling (100%, 125%, 150%, 200%):

- All layout dimensions use relative `rem` units mapped to root font size.
- Scrollbars are customized to match native Windows 11 dark scrollbars (`scrollbar-thin`, `scrollbar-thumb-border`, `scrollbar-track-transparent`).
- Viewport boundaries prevent horizontal body overflow (`overflow-hidden` on root shell).
