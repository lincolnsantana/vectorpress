import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

function App() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <header className="border-b">
        <div className="mx-auto flex w-full max-w-3xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold text-foreground">AI Pulse</h1>
            <p className="text-sm text-muted-foreground">
              Notícias de IA com consultas baseadas em RAG
            </p>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-3xl flex-1 px-6 py-8">
        <Tabs defaultValue="noticias">
          <TabsList>
            <TabsTrigger value="noticias">Notícias</TabsTrigger>
            <TabsTrigger value="perguntar">Perguntar</TabsTrigger>
          </TabsList>

          <TabsContent value="noticias">
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
          </TabsContent>

          <TabsContent value="perguntar">
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
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default App;
