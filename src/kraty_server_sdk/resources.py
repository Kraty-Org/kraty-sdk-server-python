"""Resource clients for the Kraty server SDK.

Each class corresponds to one slice of the ``/server/v1`` surface
and accepts pre-validated kwargs that get JSON-serialised onto the
wire. Keys in the request body are camelCase (matching the API
contract); the Python parameters are snake_case for ergonomics, and
the methods translate.
"""

from __future__ import annotations

import builtins
import urllib.parse
from typing import Any

from kraty_server_sdk.client import KratyAdminClient


class GrantsClient:
    """``/server/v1/players/:externalId/grants``: manual grant minting.

    Used for IAP fulfilment, make-goods, manual operator rewards, and
    any other server-issued payout.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def create(
        self,
        external_player_id: str,
        *,
        idempotency_key: str,
        entries: list[dict[str, Any]],
        kind: str = "reward",
        expires_at: str | None = None,
        source_kind: str = "api",
        source_ref_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/grants``: mint a new grant.

        Args:
            external_player_id: Stable player identifier.
            idempotency_key: Required, usually the IAP receipt id.
                Replays with the same body return the original grant;
                replays with a DIFFERENT body return 409
                ``idempotency_conflict``.
            entries: At least one. Each entry is one of:

                * ``{"type": "currency", "currencyKey": str, "amount": int}``
                * ``{"type": "item",     "itemKey": str, "quantity": int, "parameters"?: dict}``
                * ``{"type": "crate",    "crateItemKey": str, "quantity": int}``
            kind: ``"reward"`` (default) or ``"crate"``. Crates need to
                be ``/open``\\ ed by the player to roll their contents.
            expires_at: Optional ISO datetime; the grant becomes
                unclaimable after this.
            source_kind: ``"api"`` (default) or ``"admin"``.
            source_ref_id: Tracing id (usually the IAP receipt).
            metadata: Free-form blob persisted on the grant row.

        Returns: The grant row (camelCase dict matching the wire shape).
        """
        body: dict[str, Any] = {
            "idempotencyKey": idempotency_key,
            "kind": kind,
            "entries": entries,
            "sourceKind": source_kind,
        }
        if expires_at is not None:
            body["expiresAt"] = expires_at
        if source_ref_id is not None:
            body["sourceRefId"] = source_ref_id
        if metadata is not None:
            body["metadata"] = metadata
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/grants",
            body=body,
        )
        return _data(env)

    def ack(
        self,
        external_player_id: str,
        grant_id: str,
        *,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/grants/:grantId/ack``: server-side claim.

        Use this when your backend wants to flip a grant to ``claimed``
        without the player's client SDK having to round-trip (e.g.
        consumable that's already applied server-side). Records
        ``ackedBy='server_api'`` on the audit row. Idempotent on
        ``grantId``.
        """
        body: dict[str, Any] = {}
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/grants/{_enc(grant_id)}/ack",
            body=body,
        )
        return _data(env)


class InventoryClient:
    """``/server/v1/players/:p/inventory(/...)``: platform-managed inventory grant + revoke.

    Only meaningful when the game has
    ``settings.inventoryManagement === 'platform'``. For studio-managed
    games these calls are inert.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def grant(
        self,
        external_player_id: str,
        item_key: str,
        *,
        quantity: int,
        reason: str | None = None,
        source_ref_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:p/inventory/:itemKey/grant``: atomic increment.

        Used for IAP item delivery, make-goods, or operator-issued
        items. Supply the IAP receipt id as ``idempotency_key`` so
        retries don't double-grant.
        """
        body = self._adjust_body(quantity, reason, source_ref_id, idempotency_key)
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/inventory/{_enc(item_key)}/grant",
            body=body,
        )
        return _data(env)

    def revoke(
        self,
        external_player_id: str,
        item_key: str,
        *,
        quantity: int,
        reason: str | None = None,
        source_ref_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:p/inventory/:itemKey/revoke``: atomic decrement.

        Used for chargebacks and admin corrections. 409 on insufficient
        quantity, because the audit ledger never goes negative.
        """
        body = self._adjust_body(quantity, reason, source_ref_id, idempotency_key)
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/inventory/{_enc(item_key)}/revoke",
            body=body,
        )
        return _data(env)

    @staticmethod
    def _adjust_body(
        quantity: int,
        reason: str | None,
        source_ref_id: str | None,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"quantity": quantity}
        if reason is not None:
            body["reason"] = reason
        if source_ref_id is not None:
            body["sourceRefId"] = source_ref_id
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        return body


class WalletClient:
    """``/server/v1/players/:p/wallet(/...)``: server-side currency mint + burn.

    Counterpart to the client SDK's ``wallet.debit``: only the server
    surface can credit balance, which is why this server SDK is a
    separate package.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def credit(
        self,
        external_player_id: str,
        economy_key: str,
        *,
        amount: int,
        reason: str | None = None,
        source_ref_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:p/wallet/:economyKey/credit``: atomic increment.

        Used for IAP currency fulfilment, support reissues, and prize
        distribution. Pass the receipt id as ``idempotency_key``.
        """
        body = self._adjust_body(amount, reason, source_ref_id, idempotency_key)
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/wallet/{_enc(economy_key)}/credit",
            body=body,
        )
        return _data(env)

    def debit(
        self,
        external_player_id: str,
        economy_key: str,
        *,
        amount: int,
        reason: str | None = None,
        source_ref_id: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:p/wallet/:economyKey/debit``: atomic decrement.

        Used for refunds and admin corrections. 409 on insufficient
        balance.
        """
        body = self._adjust_body(amount, reason, source_ref_id, idempotency_key)
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/wallet/{_enc(economy_key)}/debit",
            body=body,
        )
        return _data(env)

    @staticmethod
    def _adjust_body(
        amount: int,
        reason: str | None,
        source_ref_id: str | None,
        idempotency_key: str | None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"amount": amount}
        if reason is not None:
            body["reason"] = reason
        if source_ref_id is not None:
            body["sourceRefId"] = source_ref_id
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        return body


class LobbiesClient:
    """``/server/v1/games/:gameId/.../lobbies``: push pre-matched lobbies.

    Use when your studio's own matchmaker (Steam, GameLift, Photon)
    already chose a roster and you want Kraty to host the event
    window + scoring.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def push(
        self,
        game_id: str,
        event_key: str,
        *,
        key: str,
        external_player_ids: list[str],
        capacity: int | None = None,
        fill_bots: bool | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/games/:gameId/events/:eventKey/lobbies``: create a pre-matched lobby.

        Idempotent on ``key`` (your studio's lobby id). Requires the
        event's ``leaderboardMode`` to be ``'lobby_matched'``.
        """
        body: dict[str, Any] = {
            "key": key,
            "externalPlayerIds": external_player_ids,
        }
        if capacity is not None:
            body["capacity"] = capacity
        if fill_bots is not None:
            body["fillBots"] = fill_bots
        if metadata is not None:
            body["metadata"] = metadata
        env = self._client.request(
            "POST",
            f"/server/v1/games/{_enc(game_id)}/events/{_enc(event_key)}/lobbies",
            body=body,
        )
        return _data(env)

    def read(self, game_id: str, lobby_id: str) -> dict[str, Any]:
        """GET ``/server/v1/games/:gameId/lobbies/:lobbyId``: server-side lobby read."""
        env = self._client.request(
            "GET",
            f"/server/v1/games/{_enc(game_id)}/lobbies/{_enc(lobby_id)}",
        )
        return _data(env)


class LeaderboardsClient:
    """``/server/v1/leaderboards/:key/score``: server-authoritative scoring.

    Unlike the client SDK's score path, this surface is NOT subject to
    the game's ``acceptClientScores`` gate: the ``server_integration``
    key is trusted, so studios that keep scoring server-side (anti-cheat,
    simulation results) write here.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def submit_score(
        self,
        external_player_id: str,
        key: str,
        value: float,
        *,
        segment: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/leaderboards/:key/score``: submit a score
        for a player on a score-ranked board.

        Segmentation: on ``context`` boards pass ``segment`` as the
        bucket value; on ``progression`` boards omit it (the server
        derives the bucket from the player's progression state); on
        unsegmented boards it's ignored. ``country`` is always resolved
        server-side from the player's stored country (server-authoritative),
        and on a **combined** board (multiple axes) every axis is derived
        server-side, so omit ``segment`` — one value can't address them all.

        Returns ``{"leaderboardId": str, "score": number, "rank": int | None}``.

        Raises ``KratyServerError`` with ``code='not_found'`` for an
        unknown player or board, and ``code='score_not_supported'`` (400)
        for progression-ranked boards (which don't accept raw scores;
        adjust the progression item instead).
        """
        body: dict[str, Any] = {
            "externalPlayerId": external_player_id,
            "value": value,
        }
        if segment is not None:
            body["segment"] = segment
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        env = self._client.request(
            "POST",
            f"/server/v1/leaderboards/{_enc(key)}/score",
            body=body,
        )
        return _data(env)


class EventsClient:
    """``/server/v1/players/:externalId/events/...``: server-authoritative
    event progress.

    Same shape as the client SDK's progress endpoint, but driven from
    your backend (trusted simulation, server-side match results) rather
    than the game client.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def report_progress(
        self,
        external_player_id: str,
        event_key: str,
        attempt_id: str,
        *,
        mode: str,
        metric_value: float | None = None,
        metrics: dict[str, float] | None = None,
        occurred_at: str | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST
        ``/server/v1/players/:externalId/events/:eventKey/attempts/:attemptId/progress``:
        push a metric update onto an in-flight attempt.

        ``mode`` is ``"set"`` (write the value as the new metric) or
        ``"increment"`` (add to the current). Returns
        ``{"attempt": {...}, "milestonesFired": [...]}``: the updated
        attempt plus any milestones that fired (and the grants they
        wrote) this call.
        """
        body: dict[str, Any] = {"mode": mode}
        if metric_value is not None:
            body["metricValue"] = metric_value
        if metrics is not None:
            body["metrics"] = metrics
        if occurred_at is not None:
            body["occurredAt"] = occurred_at
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}"
            f"/events/{_enc(event_key)}/attempts/{_enc(attempt_id)}/progress",
            body=body,
        )
        return _data(env)

    # Alias matching the client SDK's ``progress`` verb, so the same name
    # works when moving score submission to your server. ``report_progress``
    # stays the canonical server-SDK name.
    progress = report_progress

    def finish(
        self,
        external_player_id: str,
        event_key: str,
        attempt_id: str,
    ) -> dict[str, Any]:
        """POST
        ``/server/v1/players/:externalId/events/:eventKey/attempts/:attemptId/finish``:
        end an in-progress attempt now, finalizing with its current score
        (server-authoritative counterpart to the client SDK ``finish``).
        Returns ``{"attempt": {...}, "outcome": "completed" | "expired"}``:
        ``completed`` for a score-attack end / target met, ``expired`` for a
        target event ended early.
        """
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}"
            f"/events/{_enc(event_key)}/attempts/{_enc(attempt_id)}/finish",
        )
        return _data(env)


class PlayersClient:
    """``/server/v1/players/:externalId``: unified player snapshot,
    plus GDPR delete + export."""

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def get(self, external_player_id: str) -> dict[str, Any]:
        """GET ``/server/v1/players/:externalId``: returns ``{player, inventory, wallet, recentGrants}``."""
        env = self._client.request(
            "GET",
            f"/server/v1/players/{_enc(external_player_id)}",
        )
        return _data(env)

    def set_identity(
        self,
        external_player_id: str,
        *,
        name: str,
        avatar: str | None = None,
    ) -> dict[str, Any]:
        """PUT ``/server/v1/players/:externalId/identity``: override the
        player's synthetic identity (display ``name`` + optional ``avatar``).

        It's normally auto-generated from the game's pool on first contact;
        call this to set a custom one (e.g. the player's chosen handle) that
        shows on leaderboards and in the client SDK. The player must already
        be registered. Returns ``{externalPlayerId, syntheticIdentity}``.
        """
        body: dict[str, Any] = {"name": name}
        if avatar is not None:
            body["avatar"] = avatar
        env = self._client.request(
            "PUT",
            f"/server/v1/players/{_enc(external_player_id)}/identity",
            body=body,
        )
        return _data(env)

    def delete(
        self,
        external_player_id: str,
        *,
        reason: str = "gdpr_erasure",
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/delete``: GDPR
        Article 17 right of erasure.

        Anonymizes the player row in place and cascades through
        attempts, lobbies, and the Redis leaderboard meta. The
        financial ledger (grants, item / wallet ledgers) is retained
        per audit requirements; its ``playerId`` FK now points at an
        anonymized row.

        Returns the outcome::

            {
              "playerId": "<uuid|null>",
              "externalPlayerId": "<original>",
              "anonymizedExternalId": "__deleted_<uuid>__ | null",
              "deletedAt": "<iso>",
              "attemptsAnonymized": int,
              "lobbiesAnonymized": int,
              "leaderboardsScrubbed": int,
              "status": "erased" | "no_op_already_erased" | "no_op_never_existed"
            }

        ``reason`` is one of ``gdpr_erasure`` (default), ``studio_request``,
        ``test``. Recorded on the audit log.

        Emits one final ``player.deleted`` webhook with the original
        external id so your backend can mirror the deletion. Idempotent:
        erasure for a never-existed player succeeds with
        ``status: "no_op_never_existed"`` (GDPR semantics: nothing to erase).
        """
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/delete",
            body={"reason": reason},
        )
        return _data(env)

    def export(self, external_player_id: str) -> dict[str, Any]:
        """GET ``/server/v1/players/:externalId/export``: GDPR
        Article 15 right of access.

        Returns the full machine-readable bundle of everything Kraty
        stores about the player (profile, attempts, grants, inventory,
        wallet, lobbies). Each list is hard-capped at 1,000 rows.

        Raises ``KratyServerError`` with ``code='not_found'`` when the
        player is unknown to Kraty.
        """
        env = self._client.request(
            "GET",
            f"/server/v1/players/{_enc(external_player_id)}/export",
        )
        return _data(env)

    def ban(self, external_player_id: str, *, reason: str) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/ban``: soft-ban a
        player. Gates future SDK writes (events.start / progress /
        claim / open / debit / consume / register all return 403
        ``player_banned``) without touching existing scores or grants.

        Typical use case: studio's own anti-cheat pipeline detects an
        anomaly and bans the player automatically. The actor is
        recorded as ``api_key:<prefix>`` on the audit row.

        Idempotent: re-banning refreshes the reason but doesn't
        re-fire the webhook.
        """
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/ban",
            body={"reason": reason},
        )
        return _data(env)

    def unban(self, external_player_id: str) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/unban``: lift a
        soft-ban. Symmetric to :meth:`ban`. Idempotent: unbanning a
        non-banned player returns ``applied: False``.
        """
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/unban",
        )
        return _data(env)

    def merge(
        self,
        from_external_player_id: str,
        to_external_player_id: str,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:from/merge-into/:to``: fold the
        source player's record into the target.

        Reassigns attempts, grants, item + wallet ledgers; sums
        balances on key collision; dedupes lobby memberships; rewrites
        the source row to a ``__merged_<uuid>__`` placeholder so the
        original external id is available for re-registration.

        Typical use: guest player on a fresh device finishes
        onboarding, signs in via OAuth, and the studio backend folds
        the guest record into the authenticated player.

        Idempotent: replaying after the merge returns
        ``status='no_op_already_merged'`` with the existing target.

        Raises ``KratyServerError`` with ``code='not_found'`` on
        missing players, or ``code='conflict'`` (422) on invalid
        merges (same player, target banned/deleted).
        """
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(from_external_player_id)}"
            f"/merge-into/{_enc(to_external_player_id)}",
        )
        return _data(env)

    def friends(self, external_player_id: str) -> list[dict[str, Any]]:
        """GET ``/server/v1/players/:externalId/friends``: read ANY
        player's accepted friends (read-only support / moderation
        surface).

        Each friend is enriched with display identity and live presence::

            {
              "externalPlayerId": str,
              "displayIdentity": {"name": str, "avatar": str | None, "country": str | None} | None,
              "friendsSince": "<iso>",
              "online": bool,
              "lastActiveAt": "<iso>" | None,
              "status": str | None
            }

        The player's own add / accept / block actions live on the
        client SDK's ``friends`` client, not here. Raises
        ``KratyServerError`` with ``code='not_found'`` when the player
        is unknown to Kraty.
        """
        env = self._client.request(
            "GET",
            f"/server/v1/players/{_enc(external_player_id)}/friends",
        )
        friends = _data(env).get("friends", [])
        return friends if isinstance(friends, list) else []

    def friend_requests(self, external_player_id: str) -> dict[str, Any]:
        """GET ``/server/v1/players/:externalId/friends/requests``: the
        player's pending incoming + outgoing friend requests (read-only).

        Returns ``{"incoming": [FriendRequest], "outgoing": [FriendRequest]}``
        where each request is::

            {
              "requestId": str,
              "direction": "incoming" | "outgoing",
              "player": {"externalPlayerId": str, "displayIdentity": {...} | None},
              "createdAt": "<iso>"
            }

        Raises ``KratyServerError`` with ``code='not_found'`` when the
        player is unknown to Kraty.
        """
        env = self._client.request(
            "GET",
            f"/server/v1/players/{_enc(external_player_id)}/friends/requests",
        )
        return _data(env)

    def blocks(self, external_player_id: str) -> list[dict[str, Any]]:
        """GET ``/server/v1/players/:externalId/blocks``: the players this
        player has blocked (read-only).

        Each row is::

            {
              "externalPlayerId": str,
              "displayIdentity": {"name": str, "avatar": str | None, "country": str | None} | None,
              "blockedAt": "<iso>"
            }

        Raises ``KratyServerError`` with ``code='not_found'`` when the
        player is unknown to Kraty.
        """
        env = self._client.request(
            "GET",
            f"/server/v1/players/{_enc(external_player_id)}/blocks",
        )
        blocked = _data(env).get("blocked", [])
        return blocked if isinstance(blocked, list) else []


class GuildsClient:
    """``/server/v1/guilds*``: guild reads and studio-side moderation
    (docs/25).

    Pinned to the API key's environment: a guild of the other environment
    reads as ``not_found``. Every write is audited (``actorKind: api_key``)
    and fires the matching ``guild.*`` webhook.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def list(
        self,
        *,
        q: str | None = None,
        player: str | None = None,
        include_disbanded: bool = False,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """GET ``/server/v1/guilds``: newest first. ``q`` matches names,
        ``player`` finds the guilds a player is in or was in. Returns
        ``{"guilds": [GuildAdminSummary], "total": int}``.
        """
        params: dict[str, str] = {}
        if q:
            params["q"] = q
        if player:
            params["player"] = player
        if include_disbanded:
            params["includeDisbanded"] = "true"
        if limit is not None:
            params["limit"] = str(limit)
        if offset is not None:
            params["offset"] = str(offset)
        query = f"?{urllib.parse.urlencode(params)}" if params else ""
        return _data(self._client.request("GET", f"/server/v1/guilds{query}"))

    def get(self, guild_id: str) -> dict[str, Any]:
        """GET ``/server/v1/guilds/:guildId``: roster, pending join
        requests and membership history."""
        return _data(self._client.request("GET", f"/server/v1/guilds/{_enc(guild_id)}"))

    def for_player(self, external_player_id: str) -> dict[str, Any]:
        """GET ``/server/v1/players/:externalId/guild``: the player's
        current guild (or ``None``), their role and their stints."""
        return _data(
            self._client.request("GET", f"/server/v1/players/{_enc(external_player_id)}/guild")
        )

    def update(self, guild_id: str, **patch: Any) -> dict[str, Any]:
        """PATCH ``/server/v1/guilds/:guildId``: moderate the profile
        (``name``, ``description``, ``badge``, ``country``, ``joinType``,
        ``metadata``). Bypasses the studio's name filter."""
        return _data(
            self._client.request("PATCH", f"/server/v1/guilds/{_enc(guild_id)}", body=patch)
        )

    def remove_member(self, guild_id: str, external_player_id: str) -> dict[str, Any]:
        """POST ``/server/v1/guilds/:guildId/members/:externalId/remove``:
        moderation removal (no rejoin block, unlike a kick)."""
        return _data(
            self._client.request(
                "POST",
                f"/server/v1/guilds/{_enc(guild_id)}/members/{_enc(external_player_id)}/remove",
            )
        )

    def set_leader(self, guild_id: str, external_player_id: str) -> dict[str, Any]:
        """POST ``/server/v1/guilds/:guildId/leader``: the old leader
        becomes a co-leader."""
        return _data(
            self._client.request(
                "POST",
                f"/server/v1/guilds/{_enc(guild_id)}/leader",
                body={"externalPlayerId": external_player_id},
            )
        )

    def disband(self, guild_id: str) -> dict[str, Any]:
        """POST ``/server/v1/guilds/:guildId/disband``: every member
        leaves, then the guild closes. Irreversible."""
        return _data(self._client.request("POST", f"/server/v1/guilds/{_enc(guild_id)}/disband"))


class PurchasesClient:
    """``/server/v1/players/:externalId/purchases``: server-authoritative
    purchase ingest (docs/22).

    Report a purchase once your backend has validated the receipt, with
    ``validation_status="verified"``. Idempotent on ``transaction_id``: a
    replay returns the stored row with ``deduplicated: True``, and a
    verified replay of a client-reported purchase marks it verified.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def track(
        self,
        external_player_id: str,
        *,
        transaction_id: str,
        store: str,
        product_id: str,
        amount_minor: int,
        currency: str,
        product_type: str | None = None,
        receipt: str | None = None,
        purchased_at: str | None = None,
        metadata: dict[str, Any] | None = None,
        validation_status: str | None = None,
        offer_instance_id: str | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/purchases``: record a
        real-money purchase.

        Args:
            transaction_id: The store's canonical transaction id, the same
                one the client reports: the StoreKit 2 ``transactionId`` on
                the App Store (never ``originalTransactionId``), the
                ``orderId`` (``GPA.…``) on Google Play.
            store: ``app_store``, ``google_play``, ``steam``, ``epic``,
                ``amazon``, ``microsoft``, ``playstation``, ``nintendo``,
                ``web`` or ``other``.
            amount_minor: Minor units as charged (``499`` is $4.99).
            currency: ISO 4217, e.g. ``"USD"``.
            validation_status: ``"verified"`` once Apple/Google confirmed
                the receipt; otherwise leave it out.
            offer_instance_id: The player offer (``instanceId`` from
                ``offers.list`` or the client's list) the purchase was made
                from. Required for the offer to be delivered; without it the
                purchase only counts as that offer's revenue (docs/26).

        Returns: ``TrackPurchaseResult``. Its ``offer`` is the attribution
        (``None`` when none): when ``offer["studioFulfils"]`` is true,
        deliver ``offer["contents"]`` yourself.
        """
        body: dict[str, Any] = {
            "transactionId": transaction_id,
            "store": store,
            "productId": product_id,
            "amountMinor": amount_minor,
            "currency": currency,
        }
        if product_type is not None:
            body["productType"] = product_type
        if receipt is not None:
            body["receipt"] = receipt
        if purchased_at is not None:
            body["purchasedAt"] = purchased_at
        if metadata is not None:
            body["metadata"] = metadata
        if validation_status is not None:
            body["validationStatus"] = validation_status
        if offer_instance_id is not None:
            body["offerInstanceId"] = offer_instance_id
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/purchases",
            body=body,
        )
        return _data(env)


class OffersClient:
    """``/server/v1/players/:externalId/offers``: real-money offers for
    server-driven storefronts, and authoritative trigger reports (docs/26).

    Your backend is the verified door for an offer purchase: report it with
    ``purchases.track(..., validation_status="verified",
    offer_instance_id=offer["instanceId"])``.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def list(
        self,
        external_player_id: str,
        *,
        limit: int | None = None,
        level: int | None = None,
    ) -> builtins.list[dict[str, Any]]:
        """GET ``/server/v1/players/:externalId/offers``: the offers the
        player can be shown now, highest priority first (``limit`` ≤ 20,
        default 10). ``level`` is the player's current level, for offers
        that trigger on reaching one. Records no impression.

        Returns: a list of ``SdkOffer`` dicts (``instanceId``, ``offerKey``,
        ``current`` with ``skus`` and ``contents``, ``expiresAt``, …).
        ``variantKey`` is the A/B variant the player sees (the tiers and
        presentation already reflect it; ``None`` for the base config) and
        ``linkedEventKey`` the key of the event the offer is linked to
        (``None`` when it isn't). The list already applies the game-wide offer
        caps: at most "listed at once" offers, highest priority first.
        """
        params: dict[str, str] = {}
        if limit is not None:
            params["limit"] = str(limit)
        if level is not None:
            params["level"] = str(level)
        query = f"?{urllib.parse.urlencode(params)}" if params else ""
        env = self._client.request(
            "GET", f"/server/v1/players/{_enc(external_player_id)}/offers{query}"
        )
        data = env.get("data") if isinstance(env, dict) else None
        return [o for o in data if isinstance(o, dict)] if isinstance(data, builtins.list) else []

    def trigger(
        self,
        external_player_id: str,
        trigger: dict[str, Any],
        *,
        player_context: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/offers/triggers``: report
        what happened so the offers listening to it arm.

        Args:
            trigger: One of (camelCase, as on the wire):

                * ``{"type": "fail_event", "key": str, "consecutive"?: int}``
                * ``{"type": "resource_depleted", "resource": str, "required": int,
                  "available": int, "secondsToRegen"?: int}``
                * ``{"type": "level_reached", "level": int}``
            player_context: Feeds offer eligibility.
            idempotency_key: Stamped automatically when omitted.

        Returns: ``{"offers": [SdkOffer]}``, the newly armed offers that can
        be shown now (empty when none did).
        """
        body: dict[str, Any] = {"trigger": trigger}
        if player_context is not None:
            body["playerContext"] = player_context
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/offers/triggers",
            body=body,
        )
        return _data(env)

    def claim(
        self,
        external_player_id: str,
        instance_id: str,
        tier: int,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/offers/:instanceId/claim``:
        claim the current free tier of a chain offer
        (``offer["current"]["type"] == "free"``), for server-driven
        storefronts. No store and never revenue (docs/26 § 4.2.1).

        Args:
            instance_id: The offer's ``instanceId``.
            tier: The tier the player tapped (``offer["tier"]``); it must still
                be the current, free tier.
            idempotency_key: Stamped automatically when omitted. A retry with
                the same key replays the first answer.

        Returns: ``{"claim": OfferClaimResult, "offer": SdkOffer}``, the offer
        after the claim (the next tier, or ``completed``). When
        ``claim["studioFulfils"]`` is true (the offer is set to game delivers; by default Kraty delivers, so do not grant it too), deliver
        ``claim["contents"]`` yourself; when ``claim["granted"]``, Kraty
        granted them. Deliver each claim from one path only (this response
        or the ``offer.tier_claimed`` webhook), and de-duplicate on
        ``claim["claimId"]``.

        Raises: ``KratyServerError`` with ``code == "conflict"`` when refused;
        ``details["reason"]`` is ``tier_changed``, ``tier_not_free`` or
        ``offer_closed`` and ``details["offer"]`` is the offer now.
        """
        body: dict[str, Any] = {"tier": tier}
        if idempotency_key is not None:
            body["idempotencyKey"] = idempotency_key
        env = self._client.request(
            "POST",
            f"/server/v1/players/{_enc(external_player_id)}/offers/{_enc(instance_id)}/claim",
            body=body,
        )
        return _data(env)


class HealthClient:
    """``/server/v1/ping``: connectivity + key-info echo."""

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def ping(self) -> dict[str, Any]:
        """Useful for deploy-time smoke tests: confirms the env var is wired to the right key."""
        result = self._client.request("GET", "/server/v1/ping")
        return result if isinstance(result, dict) else {}


class MigrateClient:
    """``/server/v1/migrate/*``: bulk-import endpoints for studios moving
    existing players, wallets, and inventory into Kraty from another
    platform.

    Each method accepts up to 1,000 rows per call. Every row carries
    its own ``idempotency_key`` (typically the studio's stable id for
    that player / wallet entry / inventory holding) so retries are
    safe at the row level. Bad rows are captured in the response's
    ``failures`` list; the rest of the batch still applies.

    Studios with larger datasets loop client-side::

        for chunk in chunked(all_players, 1000):
            out = kraty.migrate.players(chunk)
            if out["failed"] > 0:
                collect_for_retry(out["failures"])

    Webhooks are NOT emitted during migration, because a 100k-player
    import would otherwise flood the studio's own backend.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def players(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        """POST ``/server/v1/migrate/players``: bulk-import players.

        Each row shape::

            {
                "externalPlayerId": str,
                "contextSnapshot": dict | None,
                "idempotencyKey": str,
            }

        Returns the migration outcome: ``{applied, skipped, failed, failures}``.
        """
        env = self._client.request("POST", "/server/v1/migrate/players", body={"rows": rows})
        return _data(env)

    def wallet(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        """POST ``/server/v1/migrate/wallet``: bulk-credit wallet balances.

        Each row shape::

            {
                "externalPlayerId": str,
                "economyKey": str,
                "amount": int,            # positive only
                "reason": str | None,
                "idempotencyKey": str,
            }
        """
        env = self._client.request("POST", "/server/v1/migrate/wallet", body={"rows": rows})
        return _data(env)

    def inventory(self, rows: list[dict[str, Any]]) -> dict[str, Any]:
        """POST ``/server/v1/migrate/inventory``: bulk-grant inventory rows.

        Each row shape::

            {
                "externalPlayerId": str,
                "itemKey": str,
                "quantity": int,
                "parameters": dict | None,
                "reason": str | None,
                "idempotencyKey": str,
            }
        """
        env = self._client.request("POST", "/server/v1/migrate/inventory", body={"rows": rows})
        return _data(env)


# ─── helpers ────────────────────────────────────────────────────────


def _enc(s: str) -> str:
    """Percent-encode a path segment."""
    return urllib.parse.quote(s, safe="")


def _data(env: Any) -> dict[str, Any]:
    """Unwrap the ``{"data": ...}`` envelope every resource endpoint returns."""
    if not isinstance(env, dict):
        return {}
    env_dict: dict[str, Any] = env
    data = env_dict.get("data")
    if isinstance(data, dict):
        data_dict: dict[str, Any] = data
        return data_dict
    # Defensive fallback: if the server ever drops the envelope, hand
    # back whatever's there so callers can still inspect it.
    return env_dict


def _query(params: dict[str, Any]) -> str:
    clean = {k: str(v) for k, v in params.items() if v is not None}
    return f"?{urllib.parse.urlencode(clean)}" if clean else ""


class ChatClient:
    """``/server/v1/chat*`` (docs/26): read conversations (original and
    filtered text, deleted messages included), post as the game, delete
    messages. Pinned to the API key's environment.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def conversations_for(
        self,
        external_player_id: str,
        *,
        kind: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> dict[str, Any]:
        """GET ``/server/v1/players/:externalId/chat/conversations``.
        Returns ``{"conversations": [...], "nextOffset": int | None}``."""
        q = _query({"kind": kind, "limit": limit, "offset": offset})
        return _data(
            self._client.request(
                "GET", f"/server/v1/players/{_enc(external_player_id)}/chat/conversations{q}"
            )
        )

    def conversation(self, conversation_id: str) -> dict[str, Any]:
        """GET ``/server/v1/chat/conversations/:id``."""
        return _data(self._client.request("GET", f"/server/v1/chat/conversations/{_enc(conversation_id)}"))

    def messages(
        self,
        conversation_id: str,
        *,
        before: int | None = None,
        after: int | None = None,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """GET ``/server/v1/chat/conversations/:id/messages``: oldest to
        newest; ``before`` / ``after`` are sequence cursors."""
        q = _query({"before": before, "after": after, "limit": limit})
        return _data(
            self._client.request("GET", f"/server/v1/chat/conversations/{_enc(conversation_id)}/messages{q}")
        )

    def post(
        self,
        conversation_id: str,
        *,
        text: str | None = None,
        custom_type: str | None = None,
        payload: Any = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/chat/conversations/:id/messages``: post as the
        game (``sender.kind: server``)."""
        return _data(
            self._client.request(
                "POST",
                f"/server/v1/chat/conversations/{_enc(conversation_id)}/messages",
                body=_message_body(text, custom_type, payload),
            )
        )

    def announce(
        self,
        channel_key: str,
        *,
        text: str | None = None,
        custom_type: str | None = None,
        payload: Any = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/chat/channels/:key/messages``: an announcement
        in a public channel."""
        return _data(
            self._client.request(
                "POST",
                f"/server/v1/chat/channels/{_enc(channel_key)}/messages",
                body=_message_body(text, custom_type, payload),
            )
        )

    def delete_message(self, message_id: str) -> dict[str, Any]:
        """DELETE ``/server/v1/chat/messages/:id`` (audited; fires
        ``chat.message_deleted``)."""
        return _data(self._client.request("DELETE", f"/server/v1/chat/messages/{_enc(message_id)}"))


def _message_body(text: str | None, custom_type: str | None, payload: Any) -> dict[str, Any]:
    body: dict[str, Any] = {}
    if text is not None:
        body["text"] = text
    if custom_type is not None:
        body["customType"] = custom_type
    if payload is not None:
        body["payload"] = payload
    return body


class ModerationClient:
    """``/server/v1/moderation*`` and player restrictions (docs/26): the
    report queue, review decisions, warnings / chat mutes / chat bans.
    Works in every game, chat or not.
    """

    def __init__(self, client: KratyAdminClient) -> None:
        self._client = client

    def reports(
        self, *, status: str | None = None, limit: int | None = None, offset: int | None = None
    ) -> list[dict[str, Any]]:
        """GET ``/server/v1/moderation/reports``: newest first."""
        q = _query({"status": status, "limit": limit, "offset": offset})
        return _data(self._client.request("GET", f"/server/v1/moderation/reports{q}"))["reports"]

    def player_case(self, external_player_id: str) -> dict[str, Any]:
        """GET ``/server/v1/players/:externalId/moderation``: reports with
        evidence, restrictions and recent messages."""
        return _data(
            self._client.request("GET", f"/server/v1/players/{_enc(external_player_id)}/moderation")
        )

    def resolve(self, external_player_id: str, *, decision: str, **fields: Any) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/moderation/resolve``.
        ``decision``: dismiss, no_action, warn, mute, chat_ban, ban. Optional
        ``note``, ``reason``, ``durationHours``, ``deleteMessageIds``,
        ``reportIds``."""
        return _data(
            self._client.request(
                "POST",
                f"/server/v1/players/{_enc(external_player_id)}/moderation/resolve",
                body={"decision": decision, **fields},
            )
        )

    def restrictions(self, external_player_id: str) -> list[dict[str, Any]]:
        """GET ``/server/v1/players/:externalId/restrictions``: history."""
        return _data(
            self._client.request("GET", f"/server/v1/players/{_enc(external_player_id)}/restrictions")
        )["restrictions"]

    def restrict(
        self,
        external_player_id: str,
        *,
        kind: str,
        reason: str | None = None,
        duration_hours: int | None = None,
    ) -> dict[str, Any]:
        """POST ``/server/v1/players/:externalId/restrictions``: a warning,
        chat_mute (needs ``duration_hours``) or chat_ban."""
        body: dict[str, Any] = {"kind": kind}
        if reason is not None:
            body["reason"] = reason
        if duration_hours is not None:
            body["durationHours"] = duration_hours
        return _data(
            self._client.request(
                "POST", f"/server/v1/players/{_enc(external_player_id)}/restrictions", body=body
            )
        )

    def lift(self, restriction_id: str) -> dict[str, Any]:
        """POST ``/server/v1/restrictions/:id/lift``."""
        return _data(self._client.request("POST", f"/server/v1/restrictions/{_enc(restriction_id)}/lift"))
