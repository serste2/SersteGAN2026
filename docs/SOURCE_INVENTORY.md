# Source inventory

## The Metropolitan Museum of Art

- Status: pilot completed locally on 2026-08-29.
- API: `https://collectionapi.metmuseum.org/public/collection/v1`
- Scope: 25 records returned by the `painting` query after public-domain, image, medium/classification, and conservative author filters.
- Local result: 25 downloaded JPEGs; 77,460,327 bytes; zero final validation rejections.
- Storage: `data/historical_vision/met/` (Git-ignored).

## DADA / SITM visual dialogue

- Public collector route: `https://dada.art/pa/<activity-id>`; no login required.
- Activity IDs form a global sequence; reply IDs render suffixes of an existing conversation.
- Current graph snapshot exceeded 1,500 turns, 336 conversations, and 1,189 ordered pairs with zero unresolved parent edges; the live crawl continues.
- Public-image records remain provenance-labelled and `training_eligible=false` pending the project rights decision.

## Smithsonian Open Access bulk release

- Official bulk source: `https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/index.txt`.
- Release shape: line-delimited JSON, partitioned by Smithsonian unit and two-character hash shards.
- Rights gate: metadata and each image asset must both state CC0.
- Art-unit route: SAAM, NPG, NMAfA, FSG, HMSG, CHNDM, NMAI, AAA, and EEPA.
- Pilot: 56 raw SAAM records yielded 38 accepted historical-art images; 15 rejected by type/rights and 3 by artist cutoff.
- Screen-source pilot: 38 images, 6,158,267 bytes, typically 1200 px.
- Normalized pilot on NAS: 38 WebP images at max 384 px, 487,564 bytes total, 12,831 bytes average, zero failures.
