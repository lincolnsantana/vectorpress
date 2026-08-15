import { ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";

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
    <Card className="gap-0 overflow-hidden py-0">
      {news.image_url ? (
        <img
          src={news.image_url}
          alt={news.title}
          className="aspect-video w-full bg-muted object-cover"
        />
      ) : (
        <div className="flex aspect-video w-full items-center justify-center bg-muted" />
      )}

      <CardContent className="flex flex-col gap-2 px-4 pt-4 pb-2">
        <div className="flex items-center justify-between gap-2">
          <Badge variant="secondary">{news.source}</Badge>
          <span className="text-xs text-muted-foreground">
            {formatDate(news.published_at)}
          </span>
        </div>
        <h2 className="font-semibold leading-snug text-foreground">
          {news.title}
        </h2>
        {news.summary && (
          <p className="line-clamp-3 text-sm text-muted-foreground">
            {news.summary}
          </p>
        )}
      </CardContent>

      <CardFooter className="px-4 pt-0 pb-4">
        <Button asChild size="sm" variant="outline">
          <a href={news.url} target="_blank" rel="noreferrer">
            Ler notícia
            <ExternalLink />
          </a>
        </Button>
      </CardFooter>
    </Card>
  );
}

export default NewsCard;
