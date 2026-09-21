import { useEffect, useRef, useState } from "react";

import NewsCard from "@/components/NewsCard";
import { fetchNews, isApiOffline } from "@/lib/api";

const PAGE_SIZE = 20;

function NewsList({ scrollRef }) {
  const [news, setNews] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);
  const sentinelRef = useRef(null);
  const loadingMoreRef = useRef(false);

  const hasMore = news.length < total;

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchNews({ limit: PAGE_SIZE, offset: 0 });
        if (active) {
          setNews(data.items);
          setTotal(data.total);
        }
      } catch (err) {
        if (active) {
          setError(
            isApiOffline(err)
              ? "A API está temporariamente indisponível. Tente novamente em instantes."
              : "Não foi possível carregar as notícias.",
          );
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

  async function loadMore() {
    if (loadingMoreRef.current || !hasMore) return;

    loadingMoreRef.current = true;
    setLoadingMore(true);
    try {
      const data = await fetchNews({ limit: PAGE_SIZE, offset: news.length });
      setNews((prev) => [...prev, ...data.items]);
      setTotal(data.total);
    } catch (err) {
      setError(
        isApiOffline(err)
          ? "A API está temporariamente indisponível. Tente novamente em instantes."
          : "Não foi possível carregar mais notícias.",
      );
    } finally {
      loadingMoreRef.current = false;
      setLoadingMore(false);
    }
  }

  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const desktop = window.matchMedia("(min-width: 1024px)");
    const getRoot = () =>
      desktop.matches && scrollRef?.current ? scrollRef.current : null;

    let observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMore();
        }
      },
      { root: getRoot(), rootMargin: "400px" },
    );

    const start = () => {
      observer.disconnect();
      observer = new IntersectionObserver(
        (entries) => {
          if (entries[0].isIntersecting) {
            loadMore();
          }
        },
        { root: getRoot(), rootMargin: "400px" },
      );
      observer.observe(sentinel);
    };

    start();
    desktop.addEventListener("change", start);

    return () => {
      observer.disconnect();
      desktop.removeEventListener("change", start);
    };
  }, [scrollRef, hasMore, news.length, loading]);

  if (loading) {
    return <p className="text-sm text-muted-foreground">Carregando notícias...</p>;
  }

  if (error && news.length === 0) {
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
    <>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {news.map((item) => (
          <NewsCard key={item.id} news={item} />
        ))}
      </div>

      {error && <p className="mt-4 text-sm text-destructive">{error}</p>}

      <div ref={sentinelRef} aria-hidden="true" />

      {loadingMore && (
        <p className="mt-4 text-sm text-muted-foreground">
          Carregando mais notícias...
        </p>
      )}

      {!hasMore && !loadingMore && (
        <p className="mt-4 text-sm text-muted-foreground">
          Você chegou ao fim das notícias da semana.
        </p>
      )}
    </>
  );
}

export default NewsList;
