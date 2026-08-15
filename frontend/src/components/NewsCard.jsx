import { useState } from "react";
import { ExternalLink, ImageIcon } from "lucide-react";

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

function NewsImage({ news }) {
  const [failed, setFailed] = useState(false);

  if (!news.image_url || failed) {
    return (
      <div className="flex h-40 w-full items-center justify-center bg-muted">
        <ImageIcon className="size-8 text-muted-foreground" />
      </div>
    );
  }

  return (
    <img
      src={news.image_url}
      alt={news.title}
      onError={() => setFailed(true)}
      className="h-40 w-full bg-muted object-cover"
    />
  );
}

function NewsCard({ news }) {
  return (
    <Card className="flex h-full flex-col gap-0 overflow-hidden py-0">
      <NewsImage news={news} />

      <CardContent className="flex flex-1 flex-col gap-2 px-4 pt-4 pb-2">
        <div className="flex items-center justify-between gap-2">
          <Badge variant="secondary">{news.source}</Badge>
          <span className="text-xs text-muted-foreground">
            {formatDate(news.published_at)}
          </span>
        </div>
        <h2 className="line-clamp-2 font-semibold leading-snug text-foreground">
          {news.title}
        </h2>
        {news.summary && (
          <p className="line-clamp-2 text-sm text-muted-foreground">
            {news.summary}
          </p>
        )}
      </CardContent>

      <CardFooter className="mt-auto px-4 pt-0 pb-4">
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
