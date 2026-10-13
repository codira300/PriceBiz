
import { useEffect, useRef, useState } from "react";

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential: string }) => void;
          }) => void;
          renderButton: (
            element: HTMLElement,
            options: {
              theme: string;
              size: string;
              shape: string;
              text: string;
              width: number;
            },
          ) => void;
        };
      };
    };
  }
}

type Props = {
  onCredential: (credential: string) => Promise<void>;
  onError: (message: string) => void;
  disabled?: boolean;
};

export function GoogleSignInButton({
  onCredential,
  onError,
  disabled = false,
}: Props) {
  const buttonRef = useRef<HTMLDivElement>(null);
  const callbackRef = useRef({ onCredential, onError });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    callbackRef.current = { onCredential, onError };
  }, [onCredential, onError]);

  useEffect(() => {
    let cancelled = false;

    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as
      | string
      | undefined;

    if (!clientId) {
      setLoading(false);
      onError("Google Sign-In is not configured for this frontend.");
      return;
    }

    function initialize() {
      if (cancelled || !window.google || !buttonRef.current) {
        return;
      }

      window.google.accounts.id.initialize({
        client_id: clientId!,
        callback: async (response) => {
          try {
            if (!response.credential) {
              throw new Error("Google did not return a credential.");
            }

            await callbackRef.current.onCredential(
              response.credential,
            );
          } catch (error) {
            callbackRef.current.onError(
              error instanceof Error
                ? error.message
                : "Google Sign-In failed.",
            );
          }
        },
      });

      buttonRef.current.replaceChildren();

      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: "outline",
        size: "large",
        shape: "rectangular",
        text: "continue_with",
        width: Math.max(
          220,
          Math.floor(buttonRef.current.clientWidth || 320),
        ),
      });

      setLoading(false);
    }

    const existingScript = document.querySelector<HTMLScriptElement>(
      'script[src="https://accounts.google.com/gsi/client"]',
    );

    if (window.google) {
      initialize();
    } else if (existingScript) {
      existingScript.addEventListener("load", initialize);
      existingScript.addEventListener("error", () => {
        if (!cancelled) {
          setLoading(false);
          onError("Could not load Google Sign-In. Please try again.");
        }
      });
    } else {
      const script = document.createElement("script");
      script.src = "https://accounts.google.com/gsi/client";
      script.async = true;
      script.defer = true;
      script.onload = initialize;
      script.onerror = () => {
        if (!cancelled) {
          setLoading(false);
          onError("Could not load Google Sign-In. Please try again.");
        }
      };

      document.head.appendChild(script);
    }

    return () => {
      cancelled = true;
    };
  }, [onError]);

  return (
    <div className={disabled ? "pointer-events-none opacity-50" : ""}>
      {loading && (
        <p className="mb-2 text-center text-sm text-muted-foreground">
          Loading Google Sign-In…
        </p>
      )}
      <div ref={buttonRef} className="flex justify-center" />
    </div>
  );
}
