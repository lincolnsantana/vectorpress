import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

function formatDate(value) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function NewsCard({ news }) {
  return (
    <a
      href={news.url}
      target="_blank"
      rel="noreferrer"
      className="block focus-visible:outline-none"
    >
      <Card className="gap-2 py-4 transition-colors hover:bg-accent/50 focus-visible:ring-2 focus-visible:ring-ring">
        <CardContent className="flex flex-col gap-2 px-4">
          <div className="flex items-center justify-between gap-2">
            <Badge variant="secondary">{news.source}</Badge>
            <span className="text-xs text-muted-foreground">
              {formatDate(news.published_at)}
            </span>
          </div>
          <h2 className="font-semibold leading-snug text-foreground">
            {news.title}
          </h2>
        </CardContent>
      </Card>
    </a>
  );
}

export default NewsCard;
