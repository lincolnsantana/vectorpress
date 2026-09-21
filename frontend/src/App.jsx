import { Laptop, Moon, Sun } from "lucide-react";
import { useRef } from "react";

import AskPanel from "@/components/AskPanel";
import NewsList from "@/components/NewsList";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useTheme } from "@/lib/useTheme";

function App() {
  const { theme, toggleTheme } = useTheme();
  const newsScrollRef = useRef(null);

  return (
    <div className="flex min-h-screen flex-col bg-background lg:h-screen lg:overflow-hidden">
      <header className="border-b">
        <div className="flex w-full items-center justify-between px-6 py-4">
          <div>
            <h1 className="flex items-center gap-2 text-xl font-semibold text-foreground">
              📰
              Vectorpress
            </h1>
            <p className="text-sm text-muted-foreground">
              Notícias de IA com consultas baseadas em RAG
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={theme === "dark" ? "Ativar modo claro" : "Ativar modo escuro"}
            title={theme === "dark" ? "Ativar modo claro" : "Ativar modo escuro"}
          >
            {theme === "dark" ? <Sun /> : <Moon />}
          </Button>
        </div>
      </header>

      <main className="flex w-full flex-1 flex-col gap-6 px-6 py-8 lg:flex-row lg:overflow-hidden">
        <section ref={newsScrollRef} className="w-full lg:w-[70%] lg:overflow-y-auto">
          <Card>
            <CardHeader>
              <CardTitle>Últimas notícias</CardTitle>
              <CardDescription>Listagem das notícias mais recentes.</CardDescription>
            </CardHeader>
            <CardContent>
              <NewsList scrollRef={newsScrollRef} />
            </CardContent>
          </Card>
        </section>

        <aside className="w-full lg:w-[30%] lg:overflow-hidden">
          <AskPanel />
        </aside>
      </main>
    </div>
  );
}

export default App;
