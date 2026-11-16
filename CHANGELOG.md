# Changelog

## Unreleased

### Features

* **offers:** `kraty.offers` (`OffersClient`): `list(external_player_id, limit=, level=)` and `trigger(external_player_id, trigger, player_context=, idempotency_key=)` for real-money offers (docs/26).
* **offers:** free chain tiers. `kraty.offers.claim(external_player_id, instance_id, tier, idempotency_key=None)` claims the current free step of a chain offer (`{"claim", "offer"}`; a refusal raises `KratyServerError` with `code == "conflict"` and `details["reason"]` `tier_changed` / `tier_not_free` / `offer_closed`). Offer tiers carry `type` (`"paid"` / `"free"`); a free tier has `storeProductKey: None`, `skus: {}` and `referencePriceMinor: 0`.
* **offers:** Revision 4 (additive). Offer dicts carry `variantKey` (the A/B variant the player sees, already applied to the tiers and presentation) and `linkedEventKey` (the linked event's key, or `None`); the `offer` of a tracked purchase and a claim carry `variantKey`. `offers.list` already applies the game-wide offer caps. Always present, `None` when unused.
* **offers:** delivery default, no API change. New offers default to Kraty delivering their contents (`delivery.grantContents: true`): Kraty grants them (`offer.granted`, `grant.created`; `offer.pendingVerification` until your server reports the purchase verified, test players on test keys at once) and `offer.studioFulfils` is false, so the game must not grant them too. Deliver `offer.contents` / `claim.contents` yourself only when `studioFulfils` is true (offers switched to "Game delivers"). Existing offers keep their setting.
* **purchases:** `kraty.purchases.track(external_player_id, transaction_id=, store=, product_id=, amount_minor=, currency=, …, validation_status=, offer_instance_id=)` (`PurchasesClient`), the server-authoritative purchase ingest; `offer_instance_id` is the verified door for an offer purchase, and the result carries `offer`.
* **events:** new server-side gate reasons, no API change. Events and offers can gate on in-game currency the player spent (`currency_spent_at_least`) and on days since install (`days_since_install_at_least`); a refused `start` carries `unlock_condition_failed` / `entry_requirement_failed` as before, with a message like `spent 12,500 / 1,000,000 diamonds` or `installed 12 / 100 days ago`. The rules are evaluated by Kraty only; nothing to send from the client.

## [0.18.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.17.3...sdk-server-python-v0.18.0) (2026-10-25)


### Features

* **offers:** monetization offers next to events ([edf6743](https://github.com/Kraty-Org/Kraty/commit/edf67439317ae0435bd38adc7015450558b3be0d))
* **offers:** monetization offers next to events ([f6206e6](https://github.com/Kraty-Org/Kraty/commit/f6206e6e31fcd973b93f3ee591175d9e8c3b1e16))

## [0.17.3](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.17.2...sdk-server-python-v0.17.3) (2026-10-16)


### Documentation

* **sdks:** bump install snippets — clients v0.29.1, server-ts v0.18.2, server-py v0.17.2 ([#89](https://github.com/Kraty-Org/Kraty/issues/89)) ([3942f3b](https://github.com/Kraty-Org/Kraty/commit/3942f3b0618fd1fd12c5c9bb5d1508f77f136365))

## [0.17.2](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.17.1...sdk-server-python-v0.17.2) (2026-09-14)


### Documentation

* **sdks:** bump install snippets — clients v0.29.0, server-ts v0.18.1, server-py v0.17.1 ([#77](https://github.com/Kraty-Org/Kraty/issues/77)) ([a6a4ff1](https://github.com/Kraty-Org/Kraty/commit/a6a4ff118d6b37afe55e07fb0811c03ad4e5b7ab))

## [0.17.1](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.17.0...sdk-server-python-v0.17.1) (2026-08-27)


### Documentation

* **sdks:** bump install snippets — clients v0.28.0, server-ts v0.18.0, server-py v0.17.0 ([#69](https://github.com/Kraty-Org/Kraty/issues/69)) ([8974116](https://github.com/Kraty-Org/Kraty/commit/8974116334ff7c2c303bf1e0ddbe16f214fece60))

## [0.17.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.16.0...sdk-server-python-v0.17.0) (2026-08-26)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **friends:** player social graph — friend codes, requests, presence, blocking ([4430123](https://github.com/Kraty-Org/Kraty/commit/4430123e34264b40910f538f32d431453d15a042))
* **friends:** social graph + matchmade-session score fix + Sessions tab ([f347a22](https://github.com/Kraty-Org/Kraty/commit/f347a220ec65fd38b5db7eed2b7dfb324405479d))
* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))
* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
* **sdks:** bump install snippets — clients v0.24.0, server-ts v0.14.0 ([c9e9d83](https://github.com/Kraty-Org/Kraty/commit/c9e9d83c402d8af1d285093d5faec415cdf4e500))
* **sdks:** bump install snippets — clients v0.25.0, server-ts v0.15.0, server-py v0.14.0 ([5c114d8](https://github.com/Kraty-Org/Kraty/commit/5c114d83e2c611ba6267cbb00bce5435decdc0cd))
* **sdks:** bump install snippets — clients v0.26.0, server-ts v0.16.0, server-py v0.15.0 ([e1581ce](https://github.com/Kraty-Org/Kraty/commit/e1581ceee55c65a4ee07cfa81587c221bcd1060d))
* **sdks:** bump install snippets — clients v0.27.0, server-ts v0.17.0, server-py v0.16.0 ([88b32d8](https://github.com/Kraty-Org/Kraty/commit/88b32d802616f4302f9d16d010e7fbfdfcc8acda))
* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs for the v0.13.0 / v0.9.0 release ([79ee827](https://github.com/Kraty-Org/Kraty/commit/79ee8271b43a8b5d299bcb94aa91ccea21459820))
* **sdks:** bump install snippets + READMEs for the v0.14.0 / v0.10.0 release ([87797b6](https://github.com/Kraty-Org/Kraty/commit/87797b602f0bbbdca10f8ca6d34b4309d51be06b))
* **sdks:** bump install snippets + READMEs for v0.15.0 / v0.11.0 release ([53ca1be](https://github.com/Kraty-Org/Kraty/commit/53ca1beae10f1fcab38c2c3c94c6b75aaad0757a))
* **sdks:** bump install snippets + READMEs for v0.16.0 / v0.12.0 release ([9bcb424](https://github.com/Kraty-Org/Kraty/commit/9bcb42492e71114205f58d9a193e6d17554abde7))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))
* **sdks:** correct python server-SDK install snippet to v0.13.1 ([e77f1c0](https://github.com/Kraty-Org/Kraty/commit/e77f1c0de6a36422c452e92d4d3f0da1ca73a55f))

## [0.16.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.15.0...sdk-server-python-v0.16.0) (2026-08-25)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **friends:** player social graph — friend codes, requests, presence, blocking ([4430123](https://github.com/Kraty-Org/Kraty/commit/4430123e34264b40910f538f32d431453d15a042))
* **friends:** social graph + matchmade-session score fix + Sessions tab ([f347a22](https://github.com/Kraty-Org/Kraty/commit/f347a220ec65fd38b5db7eed2b7dfb324405479d))
* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))
* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
* **sdks:** bump install snippets — clients v0.24.0, server-ts v0.14.0 ([c9e9d83](https://github.com/Kraty-Org/Kraty/commit/c9e9d83c402d8af1d285093d5faec415cdf4e500))
* **sdks:** bump install snippets — clients v0.25.0, server-ts v0.15.0, server-py v0.14.0 ([5c114d8](https://github.com/Kraty-Org/Kraty/commit/5c114d83e2c611ba6267cbb00bce5435decdc0cd))
* **sdks:** bump install snippets — clients v0.26.0, server-ts v0.16.0, server-py v0.15.0 ([e1581ce](https://github.com/Kraty-Org/Kraty/commit/e1581ceee55c65a4ee07cfa81587c221bcd1060d))
* **sdks:** bump install snippets — clients v0.27.0, server-ts v0.17.0, server-py v0.16.0 ([88b32d8](https://github.com/Kraty-Org/Kraty/commit/88b32d802616f4302f9d16d010e7fbfdfcc8acda))
* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs for the v0.13.0 / v0.9.0 release ([79ee827](https://github.com/Kraty-Org/Kraty/commit/79ee8271b43a8b5d299bcb94aa91ccea21459820))
* **sdks:** bump install snippets + READMEs for the v0.14.0 / v0.10.0 release ([87797b6](https://github.com/Kraty-Org/Kraty/commit/87797b602f0bbbdca10f8ca6d34b4309d51be06b))
* **sdks:** bump install snippets + READMEs for v0.15.0 / v0.11.0 release ([53ca1be](https://github.com/Kraty-Org/Kraty/commit/53ca1beae10f1fcab38c2c3c94c6b75aaad0757a))
* **sdks:** bump install snippets + READMEs for v0.16.0 / v0.12.0 release ([9bcb424](https://github.com/Kraty-Org/Kraty/commit/9bcb42492e71114205f58d9a193e6d17554abde7))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))
* **sdks:** correct python server-SDK install snippet to v0.13.1 ([e77f1c0](https://github.com/Kraty-Org/Kraty/commit/e77f1c0de6a36422c452e92d4d3f0da1ca73a55f))

## [0.15.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.14.0...sdk-server-python-v0.15.0) (2026-08-24)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **friends:** player social graph — friend codes, requests, presence, blocking ([4430123](https://github.com/Kraty-Org/Kraty/commit/4430123e34264b40910f538f32d431453d15a042))
* **friends:** social graph + matchmade-session score fix + Sessions tab ([f347a22](https://github.com/Kraty-Org/Kraty/commit/f347a220ec65fd38b5db7eed2b7dfb324405479d))
* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))
* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
* **sdks:** bump install snippets — clients v0.24.0, server-ts v0.14.0 ([c9e9d83](https://github.com/Kraty-Org/Kraty/commit/c9e9d83c402d8af1d285093d5faec415cdf4e500))
* **sdks:** bump install snippets — clients v0.25.0, server-ts v0.15.0, server-py v0.14.0 ([5c114d8](https://github.com/Kraty-Org/Kraty/commit/5c114d83e2c611ba6267cbb00bce5435decdc0cd))
* **sdks:** bump install snippets — clients v0.26.0, server-ts v0.16.0, server-py v0.15.0 ([e1581ce](https://github.com/Kraty-Org/Kraty/commit/e1581ceee55c65a4ee07cfa81587c221bcd1060d))
* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs for the v0.13.0 / v0.9.0 release ([79ee827](https://github.com/Kraty-Org/Kraty/commit/79ee8271b43a8b5d299bcb94aa91ccea21459820))
* **sdks:** bump install snippets + READMEs for the v0.14.0 / v0.10.0 release ([87797b6](https://github.com/Kraty-Org/Kraty/commit/87797b602f0bbbdca10f8ca6d34b4309d51be06b))
* **sdks:** bump install snippets + READMEs for v0.15.0 / v0.11.0 release ([53ca1be](https://github.com/Kraty-Org/Kraty/commit/53ca1beae10f1fcab38c2c3c94c6b75aaad0757a))
* **sdks:** bump install snippets + READMEs for v0.16.0 / v0.12.0 release ([9bcb424](https://github.com/Kraty-Org/Kraty/commit/9bcb42492e71114205f58d9a193e6d17554abde7))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))
* **sdks:** correct python server-SDK install snippet to v0.13.1 ([e77f1c0](https://github.com/Kraty-Org/Kraty/commit/e77f1c0de6a36422c452e92d4d3f0da1ca73a55f))

## [0.14.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.13.1...sdk-server-python-v0.14.0) (2026-08-21)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **friends:** player social graph — friend codes, requests, presence, blocking ([4430123](https://github.com/Kraty-Org/Kraty/commit/4430123e34264b40910f538f32d431453d15a042))
* **friends:** social graph + matchmade-session score fix + Sessions tab ([f347a22](https://github.com/Kraty-Org/Kraty/commit/f347a220ec65fd38b5db7eed2b7dfb324405479d))
* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))
* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
* **sdks:** bump install snippets — clients v0.24.0, server-ts v0.14.0 ([c9e9d83](https://github.com/Kraty-Org/Kraty/commit/c9e9d83c402d8af1d285093d5faec415cdf4e500))
* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs for the v0.13.0 / v0.9.0 release ([79ee827](https://github.com/Kraty-Org/Kraty/commit/79ee8271b43a8b5d299bcb94aa91ccea21459820))
* **sdks:** bump install snippets + READMEs for the v0.14.0 / v0.10.0 release ([87797b6](https://github.com/Kraty-Org/Kraty/commit/87797b602f0bbbdca10f8ca6d34b4309d51be06b))
* **sdks:** bump install snippets + READMEs for v0.15.0 / v0.11.0 release ([53ca1be](https://github.com/Kraty-Org/Kraty/commit/53ca1beae10f1fcab38c2c3c94c6b75aaad0757a))
* **sdks:** bump install snippets + READMEs for v0.16.0 / v0.12.0 release ([9bcb424](https://github.com/Kraty-Org/Kraty/commit/9bcb42492e71114205f58d9a193e6d17554abde7))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))
* **sdks:** correct python server-SDK install snippet to v0.13.1 ([e77f1c0](https://github.com/Kraty-Org/Kraty/commit/e77f1c0de6a36422c452e92d4d3f0da1ca73a55f))

## [0.13.1](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.13.0...sdk-server-python-v0.13.1) (2026-08-17)


### Documentation

* **sdks:** bump install snippets — clients v0.24.0, server-ts v0.14.0 ([c9e9d83](https://github.com/Kraty-Org/Kraty/commit/c9e9d83c402d8af1d285093d5faec415cdf4e500))

## [0.13.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.12.0...sdk-server-python-v0.13.0) (2026-07-17)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **friends:** player social graph — friend codes, requests, presence, blocking ([4430123](https://github.com/Kraty-Org/Kraty/commit/4430123e34264b40910f538f32d431453d15a042))
* **friends:** social graph + matchmade-session score fix + Sessions tab ([f347a22](https://github.com/Kraty-Org/Kraty/commit/f347a220ec65fd38b5db7eed2b7dfb324405479d))
* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))
* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs for the v0.13.0 / v0.9.0 release ([79ee827](https://github.com/Kraty-Org/Kraty/commit/79ee8271b43a8b5d299bcb94aa91ccea21459820))
* **sdks:** bump install snippets + READMEs for the v0.14.0 / v0.10.0 release ([87797b6](https://github.com/Kraty-Org/Kraty/commit/87797b602f0bbbdca10f8ca6d34b4309d51be06b))
* **sdks:** bump install snippets + READMEs for v0.15.0 / v0.11.0 release ([53ca1be](https://github.com/Kraty-Org/Kraty/commit/53ca1beae10f1fcab38c2c3c94c6b75aaad0757a))
* **sdks:** bump install snippets + READMEs for v0.16.0 / v0.12.0 release ([9bcb424](https://github.com/Kraty-Org/Kraty/commit/9bcb42492e71114205f58d9a193e6d17554abde7))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))

## [0.12.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.11.0...sdk-server-python-v0.12.0) (2026-07-17)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))
* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs for the v0.13.0 / v0.9.0 release ([79ee827](https://github.com/Kraty-Org/Kraty/commit/79ee8271b43a8b5d299bcb94aa91ccea21459820))
* **sdks:** bump install snippets + READMEs for the v0.14.0 / v0.10.0 release ([87797b6](https://github.com/Kraty-Org/Kraty/commit/87797b602f0bbbdca10f8ca6d34b4309d51be06b))
* **sdks:** bump install snippets + READMEs for v0.15.0 / v0.11.0 release ([53ca1be](https://github.com/Kraty-Org/Kraty/commit/53ca1beae10f1fcab38c2c3c94c6b75aaad0757a))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))

## [0.11.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.10.0...sdk-server-python-v0.11.0) (2026-07-16)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))
* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs for the v0.13.0 / v0.9.0 release ([79ee827](https://github.com/Kraty-Org/Kraty/commit/79ee8271b43a8b5d299bcb94aa91ccea21459820))
* **sdks:** bump install snippets + READMEs for the v0.14.0 / v0.10.0 release ([87797b6](https://github.com/Kraty-Org/Kraty/commit/87797b602f0bbbdca10f8ca6d34b4309d51be06b))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))

## [0.10.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.9.0...sdk-server-python-v0.10.0) (2026-07-16)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))
* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs for the v0.13.0 / v0.9.0 release ([79ee827](https://github.com/Kraty-Org/Kraty/commit/79ee8271b43a8b5d299bcb94aa91ccea21459820))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))

## [0.9.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.8.0...sdk-server-python-v0.9.0) (2026-07-16)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))
* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))

## [0.8.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.7.0...sdk-server-python-v0.8.0) (2026-07-15)


### Features

* **players:** per-player synthetic-identity override (server SDK + admin + portal + docs) ([906fd8c](https://github.com/Kraty-Org/Kraty/commit/906fd8c74cab043b5c5fcca5150dbf594a341e79))


### Bug Fixes

* **leaderboards:** merge server-derived country on direct-score paths ([72ff4a7](https://github.com/Kraty-Org/Kraty/commit/72ff4a75428f4f9ac952ccfc65b7649d75d3193f))


### Documentation

* **sdks:** bump install snippets + READMEs for the v0.11.0 / v0.8.0 release ([8cafc26](https://github.com/Kraty-Org/Kraty/commit/8cafc26a6d7618c700b9177bedb6471d29efcfc7))
* **sdks:** bump install snippets + READMEs to match the release-please tag versions ([c66ffaf](https://github.com/Kraty-Org/Kraty/commit/c66ffaf27e1ac495957067003a411df8857a1c53))

## [0.7.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.6.0...sdk-server-python-v0.7.0) (2026-07-12)


### Features

* finish an attempt now (player "end my run") across API + all SDKs ([f1ba2a0](https://github.com/Kraty-Org/Kraty/commit/f1ba2a0fa56a51a513bdbc865dd4ea9d854a8a65))
* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))
* **sdk:** surface synthetic identity + align progress verb across SDKs ([6e346f7](https://github.com/Kraty-Org/Kraty/commit/6e346f7328a3f58dd08d51f5f7d15c93e013aba6))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))

## [0.5.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.4.0...sdk-server-python-v0.5.0) (2026-07-09)


### Features

* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))

## [0.4.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.3.0...sdk-server-python-v0.4.0) (2026-07-06)


### Features

* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))

## [0.3.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.2.0...sdk-server-python-v0.3.0) (2026-07-02)


### Features

* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))

## [0.2.0](https://github.com/Kraty-Org/Kraty/compare/sdk-server-python-v0.1.0...sdk-server-python-v0.2.0) (2026-06-29)


### Features

* **sdks:** leaderboard submitScore (client TS/Unity/Flutter) + server scoring/progress ([02f4e69](https://github.com/Kraty-Org/Kraty/commit/02f4e6944813639ca19349ff1a9c28c92e6aa62f))


### Bug Fixes

* **ci:** alphabetise kraty_server_sdk import in test_client ([989e4e8](https://github.com/Kraty-Org/Kraty/commit/989e4e817ca3b34119c9cb0b2eeba70808e4734a))


### Documentation

* rewrite root README + point every SDK README at kraty.io/docs ([0bb9b13](https://github.com/Kraty-Org/Kraty/commit/0bb9b1385ef8803aaf2f67a3a63ea746ca4b6e12))
