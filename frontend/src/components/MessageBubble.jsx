import { ExternalLink } from "lucide-react";

function MessageBubble({ message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
          isUser ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.sources?.length > 0 && (
          <div className="mt-2 border-t border-foreground/10 pt-2">
            <p className="text-xs font-medium opacity-70">Fontes</p>
            <ul className="mt-1 flex flex-col gap-1">
              {message.sources.map((source) => (
                <li key={source.url}>
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    className={`inline-flex items-center gap-1 text-xs hover:underline ${
                      isUser ? "text-primary-foreground/90" : "text-primary"
                    }`}
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
    </div>
  );
}

export default MessageBubble;
