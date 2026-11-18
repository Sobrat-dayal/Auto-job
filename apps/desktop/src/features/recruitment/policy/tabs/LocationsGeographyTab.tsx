import * as React from 'react';
import {
  Compass,
  MapPin,
  Globe,
  CheckCircle2,
  XCircle,
} from 'lucide-react';
import { Card, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type {
  CareerStrategy,
  WorkArrangement,
  RelocationPreference,
  CareerStrategyUpdateRequest,
} from '@autonom/shared-types';

interface LocationsGeographyTabProps {
  strategy: CareerStrategy | null;
  onUpdateStrategy: (id: string, req: CareerStrategyUpdateRequest) => Promise<void>;
}

export const LocationsGeographyTab: React.FC<LocationsGeographyTabProps> = ({
  strategy,
  onUpdateStrategy,
}) => {
  const [arrangements, setArrangements] = React.useState<WorkArrangement[]>(
    strategy?.work_arrangement.allowed_arrangements || ['remote']
  );
  const [countries, setCountries] = React.useState(
    strategy?.geography.preferred_countries.join(', ') || 'United States'
  );
  const [cities, setCities] = React.useState(
    strategy?.geography.preferred_cities.join(', ') || ''
  );
  const [excludedCities, setExcludedCities] = React.useState(
    strategy?.geography.excluded_cities.join(', ') || ''
  );
  const [relocation, setRelocation] = React.useState<RelocationPreference>(
    strategy?.geography.relocation || 'not_willing'
  );
  const [maxOffsetHours, setMaxOffsetHours] = React.useState(
    strategy?.geography.max_timezone_offset_hours || 3
  );

  React.useEffect(() => {
    if (strategy) {
      setArrangements(strategy.work_arrangement.allowed_arrangements);
      setCountries(strategy.geography.preferred_countries.join(', '));
      setCities(strategy.geography.preferred_cities.join(', '));
      setExcludedCities(strategy.geography.excluded_cities.join(', '));
      setRelocation(strategy.geography.relocation);
      setMaxOffsetHours(strategy.geography.max_timezone_offset_hours || 3);
    }
  }, [strategy]);

  const toggleArrangement = (arr: WorkArrangement) => {
    if (arrangements.includes(arr)) {
      if (arrangements.length > 1) {
        setArrangements(arrangements.filter((a) => a !== arr));
      }
    } else {
      setArrangements([...arrangements, arr]);
    }
  };

  const handleSave = async () => {
    if (!strategy) return;
    await onUpdateStrategy(strategy.id, {
      work_arrangement: {
        ...strategy.work_arrangement,
        allowed_arrangements: arrangements,
      },
      geography: {
        ...strategy.geography,
        preferred_countries: countries.split(',').map((c) => c.trim()).filter(Boolean),
        preferred_cities: cities.split(',').map((c) => c.trim()).filter(Boolean),
        excluded_cities: excludedCities.split(',').map((c) => c.trim()).filter(Boolean),
        relocation,
        max_timezone_offset_hours: Number(maxOffsetHours),
      },
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-semibold text-slate-200">Location, Remote Work & Time Zone Policies</h3>
        <p className="text-xs text-slate-400">
          Configure work arrangement permissions (remote, hybrid, onsite), geographic inclusions and hard exclusions, relocation willingness, and IANA timezone boundaries.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Work Arrangement Selector */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
          <CardTitle className="text-xs font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
            <Compass className="w-4 h-4" />
            Allowed Work Arrangements
          </CardTitle>
          <div className="grid grid-cols-2 gap-2 text-xs">
            {(['remote', 'hybrid', 'onsite', 'flexible'] as WorkArrangement[]).map((arr) => {
              const active = arrangements.includes(arr);
              return (
                <button
                  key={arr}
                  type="button"
                  onClick={() => toggleArrangement(arr)}
                  className={`p-3 rounded border text-left font-medium transition-all ${
                    active
                      ? 'bg-cyan-950/60 border-cyan-500 text-cyan-200'
                      : 'bg-slate-950/40 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="capitalize">{arr}</span>
                    {active ? (
                      <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                    ) : (
                      <XCircle className="w-3.5 h-3.5 text-slate-600" />
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </Card>

        {/* Relocation & Timezone */}
        <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-3">
          <CardTitle className="text-xs font-semibold text-purple-400 uppercase tracking-wider flex items-center gap-2">
            <Globe className="w-4 h-4" />
            Relocation & Time Zones
          </CardTitle>
          <div className="space-y-3 text-xs">
            <div>
              <label className="text-xs text-slate-300 font-medium block mb-1">Relocation Willingness</label>
              <select
                value={relocation}
                onChange={(e) => setRelocation(e.target.value as RelocationPreference)}
                className="w-full bg-slate-950 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-200"
              >
                <option value="not_willing">Not Willing to Relocate</option>
                <option value="willing_domestic">Willing (Domestic Only)</option>
                <option value="willing_international">Willing (International)</option>
                <option value="remote_only">Remote Only</option>
                <option value="open">Open to Discussion</option>
              </select>
            </div>

            <div>
              <label className="text-xs text-slate-300 font-medium block mb-1">
                Max Timezone Offset (Hours)
              </label>
              <Input
                type="number"
                value={maxOffsetHours}
                onChange={(e) => setMaxOffsetHours(Number(e.target.value))}
                className="bg-slate-950 border-slate-700 text-xs"
                min={0}
                max={12}
              />
            </div>
          </div>
        </Card>
      </div>

      {/* Geographic Filters */}
      <Card className="bg-slate-900/60 border-slate-800 p-4 space-y-4">
        <CardTitle className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
          <MapPin className="w-4 h-4 text-emerald-400" />
          Geographic Target List & Hard Exclusions
        </CardTitle>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">
              Target Countries (comma-separated)
            </label>
            <Input
              value={countries}
              onChange={(e) => setCountries(e.target.value)}
              placeholder="e.g. United States, Canada, Remote"
              className="bg-slate-950 border-slate-700 text-xs"
            />
          </div>

          <div>
            <label className="text-xs text-slate-300 font-medium block mb-1">
              Target Cities / Metro Areas
            </label>
            <Input
              value={cities}
              onChange={(e) => setCities(e.target.value)}
              placeholder="e.g. San Francisco, Seattle, New York"
              className="bg-slate-950 border-slate-700 text-xs"
            />
          </div>

          <div>
            <label className="text-xs text-rose-400 font-medium block mb-1">
              Hard Excluded Cities / Regions
            </label>
            <Input
              value={excludedCities}
              onChange={(e) => setExcludedCities(e.target.value)}
              placeholder="e.g. Dallas, Miami"
              className="bg-slate-950 border-rose-900/80 text-xs"
            />
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <Button
            size="sm"
            className="bg-cyan-600 hover:bg-cyan-500 text-white text-xs"
            onClick={handleSave}
          >
            Save Location Rules
          </Button>
        </div>
      </Card>
    </div>
  );
};
