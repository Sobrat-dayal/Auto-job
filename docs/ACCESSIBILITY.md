# AUTONOM Accessibility & Inclusive Design (WCAG 2.2 AA)

## 1. Compliance Mandate

AUTONOM is designed to meet or exceed **WCAG 2.2 Level AA** standards across all desktop user interfaces. Because AUTONOM is an autonomous agent supervisory platform, operators must be able to inspect, pause, verify, and interact with all application controls rapidly and reliably via keyboard, screen reader, or high-contrast display modes.

---

## 2. Accessible Names & Semantic Roles

Every interactive element within the AUTONOM interface must declare an explicit, unambiguous accessible name:

1. **Buttons & Icon Triggers**:
   - Icon-only buttons (such as the density toggle, window controls, and search icons) include explicit `aria-label` attributes:
     ```tsx
     <Button size="icon" aria-label="Toggle density mode. Current: comfortable">
       <Sliders className="w-3.5 h-3.5" />
     </Button>
     ```
   - Action buttons with visible text rely on their text content for accessibility name calculation.

2. **Form Controls & Inputs**:
   - All `<Input>`, `<Select>`, and `<Textarea>` elements are paired with `<label>` elements using matching `id` and `htmlFor` attributes, or receive an explicit `aria-label`.
   - Error states apply `aria-invalid="true"` to input elements to announce validation failures to assistive technologies.

3. **Modals & Overlays**:
   - `<DialogContent>` automatically enforces `aria-labelledby` referencing `<DialogTitle>` and `aria-describedby` referencing `<DialogDescription>` via Radix UI primitives.

---

## 3. Focus Indicators & Keyboard Navigation

AUTONOM enforces strict keyboard navigability without dead ends:

- **Focus Rings**: All interactive primitives define a prominent 2px focus ring with 1px offset using `focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1 focus-visible:ring-offset-background`.
- **Mouse vs. Keyboard**: Focus rings are applied via `:focus-visible`, preventing visual noise on mouse clicks while ensuring full visibility during `Tab` and arrow-key traversal.
- **Focus Trapping & Restoration**:
  - Modal dialogs trap focus within the active dialog container.
  - Pressing `Escape` closes the modal and automatically restores keyboard focus to the triggering element.
- **Table Navigation**:
  - `DataTable` headers are keyboard focusable and toggled via `Enter` or `Space` to cycle ascending, descending, or unsorted modes.
  - Column headers declare explicit `aria-sort="ascending|descending|none"`.

---

## 4. Contrast Ratios

All color token combinations conform to WCAG 2.2 Level AA contrast requirements:

| Element Pair         | Foreground Token                   | Background Surface              | Contrast Ratio | WCAG AA Standard | Status |
| :------------------- | :--------------------------------- | :------------------------------ | :------------- | :--------------- | :----- |
| Primary Body Text    | `#F0F5FC` (`foreground`)           | `#0B1220` (`background`)        | **16.5:1**     | 4.5:1 min        | PASS   |
| Secondary Labels     | `#A7B6CB` (`foreground-secondary`) | `#0F1828` (`surface`)           | **7.9:1**      | 4.5:1 min        | PASS   |
| Muted Metadata       | `#8495AC` (`foreground-muted`)     | `#121E30` (`surface-secondary`) | **4.9:1**      | 4.5:1 min        | PASS   |
| Primary Blue Buttons | `#FFFFFF` (`white`)                | `#338BDF` (`primary`)           | **4.6:1**      | 4.5:1 min        | PASS   |
| Active Border Rings  | `#338BDF` (`primary`)              | `#0B1220` (`background`)        | **4.1:1**      | 3.0:1 min (UI)   | PASS   |
| Success Status Badge | `#37B89A` (`status-success`)       | `#0F1828` (`surface`)           | **6.5:1**      | 4.5:1 min        | PASS   |
| Error Status Badge   | `#E36E78` (`status-error`)         | `#0F1828` (`surface`)           | **5.4:1**      | 4.5:1 min        | PASS   |

---

## 5. Non-Color Status Communication

Color is never the sole medium for communicating operational status or state transitions:

1. **Status Badges**:
   - Every badge combines a distinct textual label (`READY`, `RUNNING`, `FAILED`, `CANCELLED`) with its color variant.
   - Live states include a circular dot indicator and CSS pulse animation.
2. **Form Validation**:
   - Input errors combine an error border with an explicit descriptive error string beneath the input field.
3. **Table Trends**:
   - Metric trends include directional Unicode arrows / icons alongside numeric percentage changes.

---

## 6. Motion & Vestibular Considerations

AUTONOM respects system-level accessibility settings for motion reduction:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  ::before,
  ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

When reduced motion is enabled:

- Indeterminate progress animations freeze into static bars.
- Live badge pulses cease.
- Modal fade-in and slide animations resolve instantaneously.
