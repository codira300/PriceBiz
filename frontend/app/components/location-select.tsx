
import {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";
import { ChevronDown, MapPin, X } from "lucide-react";

import { useCachedAsync } from "../hooks/use-async";
import { locationsApi } from "../lib/api/services";
import { cn } from "../lib/utils";
import type { LocationNode } from "../lib/types";
import { inputCls } from "./layout";

const levelOrder: Record<LocationNode["level"], number> = {
  COUNTRY: 0,
  STATE: 1,
  LGA: 2,
  AREA: 3,
  MARKET: 4,
};

type LocationSelectProps = {
  value: string;
  onChange: (value: string) => void;
  required?: boolean;
  label?: string;
  inputId?: string;
  inputClassName?: string;
};

// Returns the given parts in order, dropping blanks and duplicates.
function uniquePresent(parts: (string | null | undefined)[]): string[] {
  const seen = new Set<string>();
  const result: string[] = [];

  for (const part of parts) {
    if (part && !seen.has(part)) {
      seen.add(part);
      result.push(part);
    }
  }

  return result;
}

type EnrichedLocation = {
  location: LocationNode;
  state: string;
  lga: string;
  area: string;
  path: string[];
};

export function LocationSelect({
  value,
  onChange,
  required = false,
  label,
  inputId,
  inputClassName,
}: LocationSelectProps) {
  const generatedId = useId();
  const resolvedInputId = inputId ?? generatedId;

  const { data } = useCachedAsync<LocationNode[]>(
    "locations:list",
    () => locationsApi.list(),
  );

  const [query, setQuery] = useState("");
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  /*
   * The existing selector uses a flat list with hierarchy levels.
   * Reconstruct the ancestry from that order so suggestions can
   * display a market together with its LGA and state.
   */
  const enrichedLocations = useMemo<EnrichedLocation[]>(() => {
    const ancestors: Array<{
      location: LocationNode;
      rank: number;
    }> = [];

    const result: EnrichedLocation[] = [];

    for (const location of data ?? []) {
      const rank = levelOrder[location.level];

      while (
        ancestors.length > 0 &&
        ancestors[ancestors.length - 1].rank >= rank
      ) {
        ancestors.pop();
      }

      const path = [
        ...ancestors.map((item) => item.location.name),
        location.name,
      ];

      const findAncestor = (level: LocationNode["level"]) =>
        [...ancestors]
          .reverse()
          .find((item) => item.location.level === level)
          ?.location.name ?? "";

      result.push({
        location,
        state:
          location.level === "STATE"
            ? location.name
            : findAncestor("STATE"),
        lga:
          location.level === "LGA"
            ? location.name
            : findAncestor("LGA"),
        area:
          location.level === "AREA"
            ? location.name
            : findAncestor("AREA"),
        path,
      });

      ancestors.push({ location, rank });
    }

    return result;
  }, [data]);

  const selectedLocation = enrichedLocations.find(
    (item) => item.location._id === value,
  );

  const selectedLabel = selectedLocation
    ? selectedLocation.path.join(", ")
    : "";

  /*
   * Keep the visible input synchronized with the selected ID.
   * Typing a new query clears the old selection.
   */
  useEffect(() => {
    if (!open) {
      setQuery(selectedLabel);
    }
  }, [selectedLabel, open]);

  useEffect(() => {
    function handleOutsideClick(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
        setActiveIndex(-1);
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick,
      );
    };
  }, []);

  const suggestions = useMemo(() => {
    const term = query.trim().toLocaleLowerCase();

    if (!term) return [];

    return enrichedLocations
      .filter((item) =>
        item.path.some((part) =>
          part.toLocaleLowerCase().includes(term),
        ),
      )
      .sort((a, b) => {
        const aExact = a.location.name
          .toLocaleLowerCase()
          .startsWith(term)
          ? 0
          : 1;

        const bExact = b.location.name
          .toLocaleLowerCase()
          .startsWith(term)
          ? 0
          : 1;

        return (
          aExact - bExact ||
          a.location.name.localeCompare(b.location.name) ||
          a.path.join(", ").localeCompare(b.path.join(", "))
        );
      })
      .slice(0, 15);
  }, [enrichedLocations, query]);

  const groupedSuggestions = useMemo(() => {
    const groups = new Map<string, EnrichedLocation[]>();

    for (const item of suggestions) {
      const groupName = item.state || "Other locations";
      const group = groups.get(groupName) ?? [];

      group.push(item);
      groups.set(groupName, group);
    }

    return Array.from(groups.entries());
  }, [suggestions]);

  function selectLocation(item: EnrichedLocation) {
    onChange(item.location._id);
    setQuery(item.path.join(", "));
    setOpen(false);
    setActiveIndex(-1);
  }

  function handleQueryChange(nextQuery: string) {
    setQuery(nextQuery);
    setOpen(true);
    setActiveIndex(-1);

    if (value) {
      onChange("");
    }
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLInputElement>,
  ) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setOpen(true);

      setActiveIndex((current) =>
        Math.min(current + 1, suggestions.length - 1),
      );
    } else if (event.key === "ArrowUp") {
      event.preventDefault();

      setActiveIndex((current) =>
        Math.max(current - 1, 0),
      );
    } else if (event.key === "Enter") {
      if (open && activeIndex >= 0) {
        event.preventDefault();

        const item = suggestions[activeIndex];

        if (item) selectLocation(item);
      }
    } else if (event.key === "Escape") {
      setOpen(false);
      setActiveIndex(-1);
    }
  }

  return (
    <div ref={containerRef} className="relative w-full">
      {label && (
        <label
          htmlFor={resolvedInputId}
          className="mb-1.5 block text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground"
        >
          {label}
        </label>
      )}

      <div className="relative">
        <MapPin
          aria-hidden="true"
          className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-primary"
        />

        <input
          ref={inputRef}
          id={resolvedInputId}
          type="text"
          role="combobox"
          aria-label={label ?? "Location"}
          aria-autocomplete="list"
          aria-expanded={open}
          aria-controls="location-suggestions"
          aria-activedescendant={
            activeIndex >= 0
              ? `location-option-${activeIndex}`
              : undefined
          }
          autoComplete="off"
          required={required}
          value={open ? query : selectedLabel}
          placeholder={
            required
              ? "Search for a market or location"
              : "Any location"
          }
          onFocus={() => {
            setQuery(selectedLabel);
            setOpen(true);
          }}
          onChange={(event) =>
            handleQueryChange(event.target.value)
          }
          onKeyDown={handleKeyDown}
          onInvalid={(event) => {
            if (required && !value) {
              event.currentTarget.setCustomValidity(
                "Please select a location from the suggestions.",
              );
            }
          }}
          onInput={(event) => {
            event.currentTarget.setCustomValidity("");
          }}
          className={cn(inputCls, "w-full pl-9 pr-10", inputClassName)}
        />

        {query || value ? (
          <button
            type="button"
            aria-label="Clear location"
            onClick={() => {
              setQuery("");
              onChange("");
              setActiveIndex(-1);
              setOpen(true);
              inputRef.current?.focus();
            }}
            className="absolute right-2 top-1/2 grid h-8 w-8 -translate-y-1/2 place-items-center rounded-[3px] text-muted-foreground transition-colors duration-150 ease-out hover:bg-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ring"
          >
            <X className="h-4 w-4" />
          </button>
        ) : (
          <ChevronDown
            aria-hidden="true"
            className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground"
          />
        )}
      </div>

      {open && (
        <div
          id="location-suggestions"
          role="listbox"
          aria-label="Location suggestions"
          className="absolute z-50 mt-1 max-h-80 w-full overflow-y-auto border border-border bg-background py-1"
        >
          {!data ? (
            <p className="px-4 py-3 text-sm text-muted-foreground">
              Loading locations...
            </p>
          ) : !query.trim() ? (
            <p className="px-4 py-3 text-sm text-muted-foreground">
              Type a market, LGA, area or state to search.
            </p>
          ) : suggestions.length === 0 ? (
            <p className="px-4 py-3 text-sm text-muted-foreground">
              No matching locations found.
            </p>
          ) : (
            groupedSuggestions.map(([state, items]) => (
              <div key={state}>
                <p className="sticky top-0 bg-muted px-4 py-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                  {state}
                </p>

                {items.map((item) => {
                  const index = suggestions.indexOf(item);
                  const isMarket =
                    item.location.level === "MARKET";

                  const primaryLabel = item.location.name;

                  const secondaryLabel = uniquePresent([
                    item.lga,
                    item.state,
                  ])
                    .filter((part) => part !== primaryLabel)
                    .join(", ");

                  return (
                    <button
                      key={item.location._id}
                      id={`location-option-${index}`}
                      type="button"
                      role="option"
                      aria-selected={
                        item.location._id === value
                      }
                      onMouseEnter={() =>
                        setActiveIndex(index)
                      }
                      onMouseDown={(event) =>
                        event.preventDefault()
                      }
                      onClick={() => selectLocation(item)}
                      className={[
                        "flex min-h-11 w-full items-start gap-3 px-4 py-3 text-left transition-colors duration-150 ease-out focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-ring",
                        activeIndex === index
                          ? "bg-accent"
                          : "hover:bg-muted/60",
                      ].join(" ")}
                    >
                      <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />

                      <span className="min-w-0 flex-1">
                        <span className="block text-sm font-medium">
                          {primaryLabel}
                        </span>

                        {secondaryLabel && (
                          <span className="mt-0.5 block text-xs text-muted-foreground">
                            {secondaryLabel}
                          </span>
                        )}
                      </span>

                      {isMarket && (
                        <span className="shrink-0 rounded bg-muted px-2 py-1 text-xs text-muted-foreground">
                          Market
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>
      )}

      {required && (
        <input
          type="text"
          tabIndex={-1}
          aria-hidden="true"
          value={value}
          required
          readOnly
          onChange={() => undefined}
          className="pointer-events-none absolute h-px w-px opacity-0"
        />
      )}
    </div>
  );
}
