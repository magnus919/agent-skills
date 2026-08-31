# External IDs, Details, and Compound Responses

## Start with an IMDb ID

`GET /3/find/{external_id}?external_source=imdb_id` maps a foreign identifier to TMDb objects. The `external_source` value is chosen from exactly eight supported enum entries: `imdb_id`, `facebook_id`, `instagram_id`, `tvdb_id`, `tiktok_id`, `twitter_id`, `wikidata_id`, and `youtube_id`. Freebase lookups are not supported: the retired `freebase_mid` and `freebase_id` sources have been removed from the API and must not be used or documented as valid values. The response has `movie_results`, `person_results`, `tv_results`, `tv_episode_results`, and `tv_season_results` arrays. Unmatched categories are empty arrays. For an IMDb movie, extract `.movie_results[0].id` before calling the movie details endpoint.

```bash
curl -s -H "Authorization: Bearer $TMDB_ACCESS_TOKEN" \
  'https://api.themoviedb.org/3/find/tt0111161?external_source=imdb_id' \
  | jq -r '.movie_results[0].id'
```

## Details and append_to_response

Movie details expose fields such as `title`, `overview`, `genres`, `runtime`, `release_date`, `vote_average`, `vote_count`, `budget`, `revenue`, `imdb_id`, and production companies. TV details use `name`, `first_air_date`, `number_of_seasons`, `number_of_episodes`, `created_by`, `networks`, and `genres`.

Details endpoints accept `append_to_response`, a comma-separated list of sub-endpoints within the same namespace, with a maximum of 20 appended calls. Common movie tokens include `credits`, `images`, `videos`, `recommendations`, `similar`, `reviews`, `release_dates`, `watch/providers`, `external_ids`, `alternative_titles`, and `translations`; TV adds `aggregate_credits` and `content_ratings`. Encode the slash when needed (`watch%2Fproviders`). Returned keys mirror the requested token, so jq accesses the provider object as `."watch/providers"`.

```bash
curl -s -H "Authorization: Bearer $TMDB_ACCESS_TOKEN" \
  'https://api.themoviedb.org/3/movie/550?append_to_response=credits,videos,watch%2Fproviders' \
  | jq '{title, runtime, director: [.credits.crew[] | select(.job == "Director") | .name], cast: [.credits.cast[0:5][].name], us: .["watch/providers"].results.US}'
```

Credits contain `cast[]` (including `id`, `name`, `character`, `order`) and `crew[]` (including `department`, `job`). Watch-provider regions contain `link`, `flatrate`, `rent`, and `buy` arrays. Release dates nest under `results[].release_dates[]`; content ratings nest under `results[]`. TMDb requires attribution and a link to JustWatch when displaying provider data.

## Sources

- https://developer.themoviedb.org/reference/find-by-id
- https://developer.themoviedb.org/reference/movie-details
- https://developer.themoviedb.org/reference/movie-credits
- https://developer.themoviedb.org/reference/movie-watch-providers
- https://developer.themoviedb.org/reference/movie-release-dates
- https://developer.themoviedb.org/reference/tv-content-ratings
