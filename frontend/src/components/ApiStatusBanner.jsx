import { useEffect, useState } from "react";
import { CloudOff } from "lucide-react";

import { checkHealth } from "@/lib/api";

const RETRY_INTERVAL_MS = 30000;

function ApiStatusBanner() {
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    let active = true;

    async function probe() {
      try {
        await checkHealth();
        if (active) setOffline(false);
      } catch {
        if (active) setOffline(true);
      }
    }

    probe();
    const timer = setInterval(probe, RETRY_INTERVAL_MS);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, []);

  if (!offline) return null;

  return (
    <div
      role="status"
      className="flex items-start gap-3 border-b bg-destructive/10 px-6 py-3 text-sm text-foreground"
    >
      <CloudOff className="mt-0.5 size-4 shrink-0 text-destructive" />
      <p>
        <span className="font-medium">API temporariamente indisponível.</span>{" "}
        O backend roda em um servidor pessoal e pode estar fora do ar por
        manutenção. A página tenta reconectar sozinha a cada 30 segundos.
      </p>
    </div>
  );
}

export default ApiStatusBanner;
