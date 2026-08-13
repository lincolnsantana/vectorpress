import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function App() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="border-b">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold text-foreground">AI Pulse</h1>
            <p className="text-sm text-muted-foreground">
              Notícias de IA com consultas baseadas em RAG
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col gap-6 px-6 py-8 lg:flex-row">
        <section className="w-full lg:w-[70%]">
          <Card>
            <CardHeader>
              <CardTitle>Últimas notícias</CardTitle>
              <CardDescription>Listagem das notícias mais recentes.</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                As notícias serão exibidas aqui.
              </p>
            </CardContent>
          </Card>
        </section>

        <aside className="w-full lg:w-[30%] lg:sticky lg:top-6 lg:self-start">
          <Card>
            <CardHeader>
              <CardTitle>Perguntar</CardTitle>
              <CardDescription>
                Faça uma pergunta sobre as notícias recentes.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                A caixa de perguntas será exibida aqui.
              </p>
            </CardContent>
          </Card>
        </aside>
      </main>
    </div>
  );
}

export default App;
