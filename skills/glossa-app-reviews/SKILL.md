---
name: glossa-app-reviews
description: Store an app's App Store and Google Play reviews in Glossa per language and use them as context when writing or translating store listings, release notes and marketing copy — import_app_reviews from App Store Connect, the Google Play Developer API or a store export, get_app_review_stats to see which languages have reviews, list_app_reviews to read how users in one language describe the app. Use for "import our app reviews", "what do Japanese users say about us", "rewrite the German store description using our reviews"; do not use for translating app strings without marketing context (glossa-fill-translations) or for Glossa's own product reviews (submit_review, list_reviews).
---

# App reviews as translation context

Store reviews are how users describe the app in their own words, in their own
language: the names they give features, what they praise, what they complain
about. Glossa keeps them per project (one project per app) and per language so
that an agent writing a store listing, release notes or marketing page in a
language can read them first. They are context only: Glossa never translates
them and never sends them to its AI translator on its own.

## Import

1. Pick the project: `list_projects`. Reviews belong to the app's project.
2. Fetch reviews with the person's own store access (never ask for their
   credentials in chat):
   - **App Store Connect API**: `GET /v1/apps/{id}/customerReviews` gives
     `id`, `rating`, `title`, `body`, `reviewerNickname`, `createdDate` and
     `territory` (a 3-letter storefront such as `DEU`), but **no language**.
     Set each review's `locale` to the language the text is written in (read
     it; do not assume the storefront's language: many reviews in `USA` are in
     Spanish). The response (`customerReviewResponses`) is the `reply`.
   - **Google Play Developer API**: `reviews.list` gives `reviewId` and, in
     `comments[0].userComment`, `text`, `starRating`, `reviewerLanguage`,
     `appVersionName` and `lastModified`; `developerComment` is the reply.
     Play keeps only the last week of reviews in this API; older ones come
     from the Play Console's monthly review exports (CSV).
   - **A CSV or export** the person gives you: map its columns the same way.
3. `import_app_reviews` with `project`, an optional default `locale`, and up to
   500 `reviews` per call: `store` (`app_store` or `play_store`),
   `external_id` (the store's review id), `locale`, `country`, `rating` (1–5),
   `title`, `body`, `author`, `app_version`, `reviewed_at` (ISO 8601),
   `reply`, `replied_at`. Importing the same `external_id` again updates the
   review, so re-running an import is safe. Without an `external_id` Glossa
   derives one from the content. The result counts what was stored per
   locale.

CLI: `npx @meterapp/glossa import_app_reviews --json @reviews.json` with the
same input. Over REST: `POST /api/v1/import_app_reviews`.

## Use them when writing or translating marketing copy

1. `get_app_review_stats` with the project: reviews per locale and store,
   average rating, how many are 1–2 stars, the newest date. A language with a
   handful of reviews tells you little; say so rather than generalizing.
2. `list_app_reviews` with `project` and `locales` (`pt` also matches
   `pt-BR`); narrow with `min_rating`/`max_rating`, `store`, `query` (text
   contained in the title or body) or `since`. Page with `offset` until it
   reaches `total`.
3. Read for **vocabulary** (the words users in that language use for the
   app's features: use them in the copy when they match the glossary), for
   **what they value** (4–5 stars: lead with it) and for **what they miss or
   dislike** (1–2 stars: do not promise it; tell the person, it may be a
   product issue rather than a copy issue).
4. Write or translate the copy. Glossary terms and rules (`list_glossary`,
   `list_rules`) still win over review wording. When the copy lives in a
   Glossa project, `list_missing_translations` for that project reports
   `context.app_reviews` (reviews per locale) so you know they are there;
   write translations with `submit_translations`.
5. Never paste a user's review text into published copy, and never name a
   reviewer, without the person approving that exact use.

## Cleaning up

`delete_app_reviews` with `project` and review ids (from `list_app_reviews`),
a `store`, or `all: true`. Ask the person before deleting more than the
reviews they named.
