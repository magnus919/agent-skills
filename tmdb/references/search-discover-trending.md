# Search, Discover, Trending, and Lists

## Search

Use `/search/movie` with required `query`; `include_adult` defaults to false. `/search/tv` supports `first_air_date_year`, while `/search/multi` combines movie, TV, and person results. Search responses expose `page`, `results`, `total_pages`, and `total_results`. Keep `language=en-US` explicit when scripts need stable output.

## Discover

`/discover/movie` and `/discover/tv` filter catalog metadata. Useful movie filters include `with_genres`, `vote_count.gte`, `vote_average.gte`, `primary_release_date.gte/lte`, and certification fields. TV uses `first_air_date.gte/lte`; discover TV does not expose movie certification filters. The current docs state that comma-separated genre IDs are an AND query and pipe-separated IDs are an OR query. Provider filters such as `with_watch_providers` require `watch_region`.

Avoid sorting only by `vote_average.desc`: require a meaningful `vote_count.gte` threshold or a tiny-vote title can dominate. Upcoming and now-playing lists are specialized release-date views; `region` controls the market.

## Trending and lists

Trending uses `/trending/{all|movie|tv|person}/{day|week}`. `all` results carry `media_type`, which lets a consumer branch to movie or TV detail calls. Genre lists return `{genres: [{id, name}]}`. Certification lists group entries under `certifications.US` (with certification, meaning, and order).

## Sources

- https://developer.themoviedb.org/reference/search-movie
- https://developer.themoviedb.org/reference/search-tv
- https://developer.themoviedb.org/reference/search-multi
- https://developer.themoviedb.org/reference/discover-movie
- https://developer.themoviedb.org/reference/discover-tv
- https://developer.themoviedb.org/reference/trending-all
- https://developer.themoviedb.org/reference/genre-movie-list
- https://developer.themoviedb.org/reference/certification-movie-list
- https://developer.themoviedb.org/docs/region-support
