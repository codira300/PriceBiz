
"use client";

import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent,
} from "react";

const API =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000";
  
export type Location = {
  _id: string;
  country: string;
  state?: string | null;
  lga?: string | null;
  area?: string | null;
  market?: string | null;
};

type Props = {
  value: Location | null;
  onChange: (location: Location | null) => void;
  placeholder?: string;
  disabled?: boolean;
  id?: string;
  name?: string;
};

function getLocationLabel(location: Location): string {
  return [
    location.market,
    location.area,
    location.lga,
    location.state,
    location.country,
  ]
    .filter(Boolean)
    .filter(
      (value, index, values) =>
        values.indexOf(value) === index
    )
    .join(", ");
}

function getPrimaryLabel(location: Location): string {
  return (
    location.market ||
    location.area ||
    location.lga ||
    location.state ||
    location.country
  );
}

export default function LocationAutocomplete({
  value,
  onChange,
  placeholder = "Search state, LGA or market...",
  disabled = false,
  id = "location",
  name = "location_id",
}: Props) {
  const [locations, setLocations] = useState<Location[]>([]);
  const [input, setInput] = useState(
    value ? getLocationLabel(value) : ""
  );
  const [open, setOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadLocations() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(`${API}/locations/`);

        if (!response.ok) {
          throw new Error("Unable to load locations.");
        }

        const result: Location[] = await response.json();

        if (!Array.isArray(result)) {
          throw new Error("Invalid locations response.");
        }

        if (!cancelled) {
          setLocations(result);
        }
      } catch {
        if (!cancelled) {
          setError(
            "Could not load locations. Please try again."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadLocations();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    setInput(value ? getLocationLabel(value) : "");
  }, [value]);

  useEffect(() => {
    function handleOutsideClick(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setOpen(false);
        setActiveIndex(-1);

        // Restore the selected value if the user typed
        // something but did not choose a suggestion.
        if (value) {
          setInput(getLocationLabel(value));
        } else {
          setInput("");
        }
      }
    }

    document.addEventListener("mousedown", handleOutsideClick);

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, [value]);

  const suggestions = useMemo(() => {
    const query = input.trim().toLocaleLowerCase();

    if (!query) {
      return [];
    }

    return locations
      .filter((location) => {
        const searchableText = [
          location.market,
          location.area,
          location.lga,
          location.state,
          location.country,
        ]
          .filter(Boolean)
          .join(" ")
          .toLocaleLowerCase();

        return searchableText.includes(query);
      })
      .sort((a, b) => {
        const aLabel = getPrimaryLabel(a).toLowerCase();
        const bLabel = getPrimaryLabel(b).toLowerCase();

        // Prefer results whose market name starts with
        // the search term.
        const aStarts = aLabel.startsWith(query) ? 0 : 1;
        const bStarts = bLabel.startsWith(query) ? 0 : 1;

        return (
          aStarts - bStarts ||
          aLabel.localeCompare(bLabel) ||
          (a.lga ?? "").localeCompare(b.lga ?? "")
        );
      })
      .slice(0, 12);
  }, [input, locations]);

  const groupedSuggestions = useMemo(() => {
    const groups = new Map<string, Location[]>();

    for (const location of suggestions) {
      const groupName = location.state || "Other locations";
      const group = groups.get(groupName) ?? [];

      group.push(location);
      groups.set(groupName, group);
    }

    return Array.from(groups.entries());
  }, [suggestions]);

  function selectLocation(location: Location) {
    onChange(location);
    setInput(getLocationLabel(location));
    setOpen(false);
    setActiveIndex(-1);
  }

  function handleInputChange(nextValue: string) {
    setInput(nextValue);
    setOpen(true);
    setActiveIndex(-1);

    // Typing after selecting a location invalidates
    // the previous selection until another result is chosen.
    if (value) {
      onChange(null);
    }
  }

  function handleKeyDown(
    event: KeyboardEvent<HTMLInputElement>
  ) {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setOpen(true);

      setActiveIndex((current) =>
        Math.min(current + 1, suggestions.length - 1)
      );
    } else if (event.key === "ArrowUp") {
      event.preventDefault();

      setActiveIndex((current) =>
        Math.max(current - 1, 0)
      );
    } else if (event.key === "Enter") {
      if (open && activeIndex >= 0) {
        event.preventDefault();

        const location = suggestions[activeIndex];

        if (location) {
          selectLocation(location);
        }
      }
    } else if (event.key === "Escape") {
      setOpen(false);
      setActiveIndex(-1);
    }
  }

  return (
    <div ref={containerRef} className="relative w-full">
      <div
        className={[
          "flex items-center gap-3 rounded-xl border bg-white px-4",
          "transition focus-within:border-blue-500",
          "focus-within:ring-2 focus-within:ring-blue-100",
          disabled
            ? "cursor-not-allowed bg-gray-100 opacity-70"
            : "border-gray-300",
        ].join(" ")}
      >
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          className="h-5 w-5 shrink-0 text-gray-500"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"
          />
          <circle cx="12" cy="10" r="2.5" />
        </svg>

        <input
          ref={inputRef}
          id={id}
          type="text"
          role="combobox"
          aria-autocomplete="list"
          aria-expanded={open}
          aria-controls={`${id}-suggestions`}
          aria-activedescendant={
            activeIndex >= 0
              ? `${id}-option-${activeIndex}`
              : undefined
          }
          autoComplete="off"
          disabled={disabled || loading}
          value={input}
          placeholder={
            loading ? "Loading locations..." : placeholder
          }
          onFocus={() => setOpen(true)}
          onChange={(event) =>
            handleInputChange(event.target.value)
          }
          onKeyDown={handleKeyDown}
          className="min-w-0 flex-1 bg-transparent py-3.5 text-sm text-gray-900 outline-none placeholder:text-gray-400"
        />

        {input && !disabled && (
          <button
            type="button"
            aria-label="Clear location"
            onClick={() => {
              setInput("");
              onChange(null);
              setActiveIndex(-1);
              setOpen(true);
              inputRef.current?.focus();
            }}
            className="shrink-0 rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-700"
          >
            <svg
              aria-hidden="true"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="h-4 w-4"
            >
              <path
                strokeLinecap="round"
                d="m6 6 12 12M18 6 6 18"
              />
            </svg>
          </button>
        )}
      </div>

      {open && !disabled && (
        <div
          id={`${id}-suggestions`}
          role="listbox"
          aria-label="Location suggestions"
          className="absolute z-50 mt-2 max-h-80 w-full overflow-y-auto rounded-xl border border-gray-200 bg-white py-2 shadow-lg"
        >
          {error ? (
            <p className="px-4 py-3 text-sm text-red-600">
              {error}
            </p>
          ) : !input.trim() ? (
            <p className="px-4 py-3 text-sm text-gray-500">
              Start typing a market, LGA or state.
            </p>
          ) : suggestions.length === 0 ? (
            <p className="px-4 py-3 text-sm text-gray-500">
              No matching locations found.
            </p>
          ) : (
            groupedSuggestions.map(([state, items]) => (
              <div key={state}>
                <p className="sticky top-0 bg-gray-50 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-gray-500">
                  {state}
                </p>

                {items.map((location) => {
                  const index = suggestions.findIndex(
                    (item) => item._id === location._id
                  );

                  return (
                    <button
                      key={location._id}
                      id={`${id}-option-${index}`}
                      type="button"
                      role="option"
                      aria-selected={activeIndex === index}
                      onMouseEnter={() => setActiveIndex(index)}
                      onMouseDown={(event) =>
                        event.preventDefault()
                      }
                      onClick={() => selectLocation(location)}
                      className={[
                        "flex w-full items-start gap-3 px-4 py-3 text-left",
                        activeIndex === index
                          ? "bg-blue-50"
                          : "hover:bg-gray-50",
                      ].join(" ")}
                    >
                      <svg
                        aria-hidden="true"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.7"
                        className="mt-0.5 h-4 w-4 shrink-0 text-gray-400"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M20 10c0 5-8 11-8 11S4 15 4 10a8 8 0 1 1 16 0Z"
                        />
                        <circle cx="12" cy="10" r="2.5" />
                      </svg>

                      <span className="min-w-0 flex-1">
                        <span className="block text-sm font-medium text-gray-900">
                          {getPrimaryLabel(location)}
                        </span>

                        <span className="mt-0.5 block text-xs text-gray-500">
                          {[
                            location.area,
                            location.lga,
                            location.state,
                          ]
                            .filter(Boolean)
                            .filter(
                              (part) =>
                                part !== getPrimaryLabel(location)
                            )
                            .filter(
                              (part, index, parts) =>
                                parts.indexOf(part) === index
                            )
                            .join(", ")}
                        </span>
                      </span>
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>
      )}

      <input
        type="hidden"
        name={name}
        value={value?._id ?? ""}
      />

      {value && (
        <p className="mt-2 text-xs text-gray-500">
          Selected: {getLocationLabel(value)}
        </p>
      )}
    </div>
  );
}
