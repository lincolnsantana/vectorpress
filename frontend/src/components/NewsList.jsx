import { useEffect, useState } from "react";

import NewsCard from "@/components/NewsCard";
import { fetchNews } from "@/lib/api";

function NewsList() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchNews({ limit: 20, offset: 0 });
        if (active) {
          setNews(data.items);
        }
      } catch (err) {
        if (active) {
          setError("Não foi possível carregar as notícias.");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    load();
    return () => {
      active = false;
    };
  }, []);

  if (loading) {
    return <p className="text-sm text-muted-foreground">Carregando notícias...</p>;
  }

  if (error) {
    return <p className="text-sm text-destructive">{error}</p>;
  }

  if (news.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Nenhuma notícia disponível no momento.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {news.map((item) => (
        <NewsCard key={item.id} news={item} />
      ))}
    </div>
  );
}

export default NewsList;
