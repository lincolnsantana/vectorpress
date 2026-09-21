import { useEffect, useRef, useState } from "react";
import { Loader2, MessageCircleQuestion, Send, Trash2 } from "lucide-react";

import MessageBubble from "@/components/MessageBubble";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { askQuestion, isApiOffline } from "@/lib/api";

function AskPanel() {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function handleSubmit(event) {
    event.preventDefault();
    const questionValue = question.trim();
    if (!questionValue || loading) return;
    setQuestion("");
    setMessages((prev) => [...prev, { role: "user", content: questionValue }]);
    setLoading(true);
    try {
      const result = await askQuestion(questionValue);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer, sources: result.sources || [] },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: isApiOffline(err)
            ? "A API está temporariamente indisponível. Ela roda em um servidor pessoal e pode estar fora do ar por manutenção. Tente novamente em instantes."
            : "Não foi possível processar a pergunta. Tente novamente.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card className="flex h-full flex-col gap-0 py-0">
      <CardHeader className="flex flex-row items-center justify-between gap-2 border-b p-3 [.border-b]:pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <MessageCircleQuestion />
          Perguntar
        </CardTitle>
        {messages.length > 0 && (
          <Button
            variant="ghost"
            size="icon"
            className="size-8"
            onClick={() => setMessages([])}
            aria-label="Limpar conversa"
            title="Limpar conversa"
          >
            <Trash2 />
          </Button>
        )}
      </CardHeader>

      <CardContent className="flex min-h-0 flex-1 flex-col gap-0 p-0">
        <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-4 py-4">
          {messages.length === 0 && (
            <p className="mt-auto text-sm text-muted-foreground">
              Pergunte sobre as notícias recentes de IA.
            </p>
          )}
          {messages.map((message, index) => (
            <MessageBubble key={index} message={message} />
          ))}
          {loading && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="animate-spin" />
              Buscando resposta...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form
          onSubmit={handleSubmit}
          className="mt-auto flex shrink-0 items-center gap-2 border-t p-3"
        >
          <Textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                handleSubmit(event);
              }
            }}
            placeholder="Pergunte sobre as notícias..."
            rows={1}
            className="max-h-32 min-h-9 flex-1"
          />
          <Button
            type="submit"
            size="icon"
            disabled={loading || !question.trim()}
            aria-label="Enviar pergunta"
          >
            <Send />
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

export default AskPanel;
