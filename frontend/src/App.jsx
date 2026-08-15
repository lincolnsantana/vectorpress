import AskPanel from "@/components/AskPanel";
import NewsList from "@/components/NewsList";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function App() {
  return (
    <div className="flex min-h-screen flex-col bg-background lg:h-screen lg:overflow-hidden">
      <header className="border-b">
        <div className="flex w-full items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold text-foreground">AI Pulse</h1>
            <p className="text-sm text-muted-foreground">
              Notícias de IA com consultas baseadas em RAG
            </p>
          </div>
        </div>
      </header>

      <main className="flex w-full flex-1 flex-col gap-6 px-6 py-8 lg:flex-row lg:overflow-hidden">
        <section className="w-full lg:w-[70%] lg:overflow-y-auto">
          <Card>
            <CardHeader>
              <CardTitle>Últimas notícias</CardTitle>
              <CardDescription>Listagem das notícias mais recentes.</CardDescription>
            </CardHeader>
            <CardContent>
              <NewsList />
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
