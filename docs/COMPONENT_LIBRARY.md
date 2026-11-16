# AUTONOM Component Library Reference

This document serves as the developer catalog and API contract reference for all UI components implemented in Phase 2 (Stage 06).

All components are implemented in React 19 + TypeScript, styled via Tailwind CSS and CSS custom properties, and constructed upon accessible Radix UI primitives.

---

## 1. Core Primitives (`components/ui`)

### `Button`

Standardized interactive trigger with support for variants, sizes, icon slots, and async loading spinners.

- **Props**:
  - `variant`: `'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'cyan' | 'link'` (default: `'secondary'`)
  - `size`: `'sm' | 'md' | 'lg' | 'icon' | 'icon-sm'` (default: `'md'`)
  - `isLoading`: `boolean` (renders an inline spinner and disables button)
  - `loadingText`: `string` (replaces button text during loading)
  - `leftIcon`: `React.ReactNode`
  - `rightIcon`: `React.ReactNode`
  - All standard `React.ButtonHTMLAttributes<HTMLButtonElement>`
- **Example**:
  ```tsx
  import { Button } from '@/components/ui';

  <Button variant="primary" size="sm" onClick={handleSubmit}>
    Deploy Agent
  </Button>;
  ```

---

### `Input`

Single-line text input with left/right icon injection, error boundaries, and accessible state communication.

- **Props**:
  - `leftIcon`: `React.ReactNode`
  - `rightIcon`: `React.ReactNode`
  - `hasError`: `boolean` (sets `aria-invalid="true"` and applies error border)
  - All standard `React.InputHTMLAttributes<HTMLInputElement>`
- **Example**:
  ```tsx
  import { Input } from '@/components/ui';
  import { Search } from 'lucide-react';

  <Input
    placeholder="Search active jobs..."
    leftIcon={<Search className="w-4 h-4" />}
    hasError={isInvalidToken}
  />;
  ```

---

### `Textarea`

Multi-line text area styled to match surface inputs.

- **Props**:
  - `hasError`: `boolean`
  - All standard `React.TextareaHTMLAttributes<HTMLTextAreaElement>`
- **Example**:
  ```tsx
  import { Textarea } from '@/components/ui';

  <Textarea placeholder="Enter custom agent instructions..." rows={4} />;
  ```

---

### `Badge`

Compact status and category label with optional dot indicator and live pulse animation.

- **Props**:
  - `variant`: `'default' | 'neutral' | 'primary' | 'cyan' | 'success' | 'warning' | 'error' | 'inactive'` (default: `'default'`)
  - `size`: `'sm' | 'md'` (default: `'md'`)
  - `dot`: `boolean` (renders a colored circular status indicator)
  - `pulse`: `boolean` (enables CSS pulse animation on the dot)
- **Example**:
  ```tsx
  import { Badge } from '@/components/ui';

  <Badge variant="success" dot pulse>
    WAL Active / 8765
  </Badge>;
  ```

---

### `Progress`

Linear progress meter supporting deterministic percentage values or indeterminate animations for open-ended background syntheses.

- **Props**:
  - `value`: `number` (0 to 100)
  - `isIndeterminate`: `boolean`
  - `variant`: `'primary' | 'cyan' | 'success' | 'warning' | 'error'` (default: `'primary'`)
  - `size`: `'sm' | 'md' | 'lg'` (default: `'md'`)
- **Example**:
  ```tsx
  import { Progress } from '@/components/ui';

  <Progress value={74} variant="cyan" />
  <Progress isIndeterminate variant="primary" size="sm" />
  ```

---

### `Dialog`

Modal overlay with backdrop blur, focus trap, escape key dismissal, and accessible header/footer structure.

- **Sub-components**: `Dialog`, `DialogTrigger`, `DialogContent`, `DialogHeader`, `DialogFooter`, `DialogTitle`, `DialogDescription`
- **Example**:
  ```tsx
  import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogDescription,
    DialogFooter,
    Button,
  } from '@/components/ui';

  <Dialog open={isOpen} onOpenChange={setIsOpen}>
    <DialogContent>
      <DialogHeader>
        <DialogTitle>Authorize Application</DialogTitle>
        <DialogDescription>Review submission details before dispatch.</DialogDescription>
      </DialogHeader>
      <div>Modal Content</div>
      <DialogFooter>
        <Button variant="outline" onClick={() => setIsOpen(false)}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleConfirm}>
          Authorize
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>;
  ```

---

### `Select`

Custom accessible select menu built on `@radix-ui/react-select`.

- **Sub-components**: `Select`, `SelectTrigger`, `SelectValue`, `SelectContent`, `SelectItem`
- **Example**:
  ```tsx
  import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui';

  <Select value={priority} onValueChange={setPriority}>
    <SelectTrigger>
      <SelectValue placeholder="Select Priority" />
    </SelectTrigger>
    <SelectContent>
      <SelectItem value="normal">Normal</SelectItem>
      <SelectItem value="high">High</SelectItem>
    </SelectContent>
  </Select>;
  ```

---

### `Checkbox` & `Switch`

Accessible boolean toggle controls.

- **Example**:
  ```tsx
  import { Checkbox, Switch } from '@/components/ui';

  <Checkbox id="c1" checked={checked} onCheckedChange={setChecked} />
  <Switch checked={enabled} onCheckedChange={setEnabled} />
  ```

---

## 2. Layout Primitives (`components/layout`)

### `PageContainer`

Standard page canvas enforcing responsive padding, density scaling, header layout, and title actions.

- **Props**:
  - `title`: `string`
  - `subtitle`?: `string`
  - `badge`?: `React.ReactNode`
  - `actions`?: `React.ReactNode`
  - `children`: `React.ReactNode`

### `SectionHeader`

Sub-section heading container with icon, description, and action slots.

- **Props**:
  - `title`: `string`
  - `subtitle`?: `string`
  - `icon`?: `React.ReactNode`
  - `badge`?: `React.ReactNode`
  - `actions`?: `React.ReactNode`

### `SplitPanel`

Responsive master-detail container for dual-pane workstation layouts.

- **Props**:
  - `left`: `React.ReactNode`
  - `right`: `React.ReactNode`
  - `leftWidthClass`?: `string` (default: `'w-full lg:w-1/2'`)

---

## 3. Data Display (`components/data-display`)

### `MetricCard`

Key metric card with tabular figures, trend indicator, and restrained color variants.

- **Props**:
  - `title`: `string`
  - `value`: `React.ReactNode`
  - `subtitle`?: `React.ReactNode`
  - `icon`?: `React.ReactNode`
  - `variant`?: `'default' | 'primary' | 'cyan' | 'success'`
  - `trend`?: `{ value: number; isPositive: boolean; label?: string }`

### `StatusCard`

Subsystem operational card displaying live status badges and key-value metadata properties.

- **Props**:
  - `title`: `string`
  - `icon`?: `React.ReactNode`
  - `statusBadge`: `{ label: string; variant?: BadgeVariant; pulse?: boolean }`
  - `properties`: `Array<{ label: string; value: React.ReactNode; mono?: boolean }>`
  - `footerActions`?: `React.ReactNode`

### `DataTable`

High-performance TanStack Table v8 implementation with search filtering, multi-column sorting, and pagination.

- **Props**:
  - `columns`: `ColumnDef<TData, TValue>[]`
  - `data`: `TData[]`
  - `searchPlaceholder`?: `string`
  - `pageSize`?: `number` (default: 10)
  - `emptyMessage`?: `string`
  - `isLoading`?: `boolean`

---

## 4. Analytics Visualizations (`components/charts`)

### `LineChart`, `BarChart`, `DonutChart`

Theme-integrated Recharts components customized for the dark Windows dashboard aesthetic, featuring responsive containers, custom SVG tooltips, and non-clashing series colors.

- **Example**:
  ```tsx
  import { LineChart } from '@/components/charts';

  <LineChart
    title="Job Scout Volume"
    data={chartData}
    series={[
      { dataKey: 'discovered', name: 'Jobs Discovered', color: '#51C8E8' },
      { dataKey: 'applied', name: 'Applications Sent', color: '#338BDF' },
    ]}
    height={220}
  />;
  ```

---

## 5. Feedback States (`components/feedback`)

### `ErrorState`

Formatted error alert with contextual diagnostic message and retry callback.

### `LoadingState`

Centralized loading indicator with technical status messages.

### `Toast` & `useToast()`

Global notification provider with automatic dismissal and custom actions:

```tsx
const toast = useToast();
toast.success('Database snapshot verified.');
toast.error('Local sidecar connection timed out.');
```
