import { useState } from "react";
import { ExternalLink, Loader2, MessageCircleQuestion } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { askQuestion } from "@/lib/api";

function AskPanel() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const questionValue = question.trim();
    if (!questionValue || loading) return;
    setLoading(true);
    setError("");
    setAnswer("");
    setSources([]);
    try {
      const result = await askQuestion(questionValue);
      setAnswer(result.answer);
      setSources(result.sources || []);
    } catch {
      setError("Não foi possível processar a pergunta. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <MessageCircleQuestion />
          Perguntar
        </CardTitle>
        <CardDescription>Faça uma pergunta sobre as notícias recentes.</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <Textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ex.: O que a OpenAI anunciou recentemente?"
            rows={4}
          />
          <Button type="submit" disabled={loading || !question.trim()}>
            {loading ? (
              <>
                <Loader2 className="animate-spin" />
                Perguntando...
              </>
            ) : (
              "Perguntar"
            )}
          </Button>
        </form>

        {error && <p className="mt-4 text-sm text-destructive">{error}</p>}

        {answer && (
          <div className="mt-4 flex flex-col gap-2">
            <p className="text-sm leading-relaxed text-foreground">{answer}</p>
            {sources.length > 0 && (
              <div className="mt-2 flex flex-col gap-2">
                <p className="text-xs font-medium text-muted-foreground">Fontes:</p>
                <ul className="flex flex-col gap-1">
                  {sources.map((source) => (
                    <li key={source.url}>
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noreferrer"
                        className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
                      >
                        {source.title}
                        <ExternalLink className="size-3" />
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export default AskPanel;
