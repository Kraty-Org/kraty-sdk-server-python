"""Resource-client tests: URL shapes, request bodies, typed errors."""

from __future__ import annotations

import json

import httpx
import pytest
from conftest import BASE_URL  # type: ignore[import-not-found]

from kraty_server_sdk import KratyServerError

# ─── GrantsClient ───────────────────────────────────────────────────


def test_grants_create_posts_to_right_url(respx_mock, make_kraty):
    route = respx_mock.post(f"{BASE_URL}/server/v1/players/player_42/grants").mock(
        return_value=httpx.Response(
            201,
            json={
                "data": {
                    "id": "g1",
                    "kind": "reward",
                    "contents": {},
                    "sourceKind": "api",
                    "sourceRefId": "rcpt",
                    "parentGrantId": None,
                    "status": "pending",
                    "rolledAt": None,
                    "claimedAt": None,
                    "expiresAt": None,
                    "createdAt": "2026-01-01",
                }
            },
        )
    )
    k = make_kraty()
    g = k.grants.create(
        "player_42",
        idempotency_key="apple_receipt_abc",
        entries=[{"type": "currency", "currencyKey": "gold", "amount": 500}],
        source_ref_id="rcpt",
    )
    assert g["id"] == "g1"
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "idempotencyKey": "apple_receipt_abc",
        "kind": "reward",
        "entries": [{"type": "currency", "currencyKey": "gold", "amount": 500}],
        "sourceKind": "api",
        "sourceRefId": "rcpt",
    }


def test_grants_create_surfaces_idempotency_conflict(respx_mock, make_kraty):
    respx_mock.post(f"{BASE_URL}/server/v1/players/p/grants").mock(
        return_value=httpx.Response(
            409,
            json={"error": {"code": "idempotency_conflict", "message": "same key, different body"}},
        )
    )
    k = make_kraty()
    with pytest.raises(KratyServerError) as exc_info:
        k.grants.create(
            "p",
            idempotency_key="rcpt",
            entries=[{"type": "currency", "currencyKey": "gold", "amount": 1}],
        )
    assert exc_info.value.is_idempotency_conflict is True


def test_grants_ack_posts_to_right_url(respx_mock, make_kraty):
    route = respx_mock.post(f"{BASE_URL}/server/v1/players/p/grants/g1/ack").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": "g1",
                    "kind": "reward",
                    "contents": {},
                    "sourceKind": "api",
                    "sourceRefId": None,
                    "parentGrantId": None,
                    "status": "claimed",
                    "rolledAt": None,
                    "claimedAt": "2026-01-01T00:00:00Z",
                    "expiresAt": None,
                    "createdAt": "2026-01-01",
                }
            },
        )
    )
    k = make_kraty()
    g = k.grants.ack("p", "g1")
    assert g["status"] == "claimed"
    assert route.call_count == 1


# ─── InventoryClient ────────────────────────────────────────────────


def test_inventory_grant_posts_to_inventory_grant(respx_mock, make_kraty):
    route = respx_mock.post(
        f"{BASE_URL}/server/v1/players/player_42/inventory/starter_chest/grant"
    ).mock(
        return_value=httpx.Response(
            200, json={"data": {"itemKey": "starter_chest", "quantity": 1, "applied": True}}
        )
    )
    k = make_kraty()
    res = k.inventory.grant(
        "player_42",
        "starter_chest",
        quantity=1,
        reason="iap",
        idempotency_key="rcpt",
    )
    assert res["applied"] is True
    body = json.loads(route.calls[0].request.content)
    assert body == {"quantity": 1, "reason": "iap", "idempotencyKey": "rcpt"}


def test_inventory_revoke_posts_to_inventory_revoke(respx_mock, make_kraty):
    route = respx_mock.post(
        f"{BASE_URL}/server/v1/players/p/inventory/sword/revoke"
    ).mock(
        return_value=httpx.Response(200, json={"data": {"itemKey": "sword", "quantity": 0, "applied": True}})
    )
    k = make_kraty()
    k.inventory.revoke("p", "sword", quantity=1, reason="chargeback")
    body = json.loads(route.calls[0].request.content)
    assert body["quantity"] == 1
    assert body["reason"] == "chargeback"
    assert body["idempotencyKey"] == "idem-1"  # auto-stamped


# ─── WalletClient ───────────────────────────────────────────────────


def test_wallet_credit_posts_amount(respx_mock, make_kraty):
    route = respx_mock.post(f"{BASE_URL}/server/v1/players/player_42/wallet/gold/credit").mock(
        return_value=httpx.Response(
            200, json={"data": {"economyKey": "gold", "balance": 600, "applied": True}}
        ),
    )
    k = make_kraty()
    res = k.wallet.credit(
        "player_42",
        "gold",
        amount=500,
        reason="iap",
        idempotency_key="rcpt_xyz",
    )
    assert res["balance"] == 600
    body = json.loads(route.calls[0].request.content)
    assert body == {"amount": 500, "reason": "iap", "idempotencyKey": "rcpt_xyz"}


def test_wallet_debit_posts_to_debit_url(respx_mock, make_kraty):
    route = respx_mock.post(f"{BASE_URL}/server/v1/players/player_42/wallet/gold/debit").mock(
        return_value=httpx.Response(
            200, json={"data": {"economyKey": "gold", "balance": 400, "applied": True}}
        ),
    )
    k = make_kraty()
    k.wallet.debit("player_42", "gold", amount=100, reason="refund")
    assert route.call_count == 1


# ─── LobbiesClient ──────────────────────────────────────────────────


def test_lobbies_push_creates_with_roster_and_key(respx_mock, make_kraty):
    route = respx_mock.post(
        f"{BASE_URL}/server/v1/games/game_1/events/quick_brawl/lobbies"
    ).mock(
        return_value=httpx.Response(
            201,
            json={
                "data": {
                    "id": "lob1",
                    "eventId": "e1",
                    "eventWindowId": "w1",
                    "leaderboardId": "lb1",
                    "mode": "lobby_matched",
                    "status": "active",
                    "capacity": 4,
                    "fillBy": None,
                    "participantCount": 2,
                    "botSlots": 0,
                    "startedAt": None,
                    "endsAt": None,
                }
            },
        )
    )
    k = make_kraty()
    lobby = k.lobbies.push(
        "game_1",
        "quick_brawl",
        key="matchmaker_lobby_123",
        external_player_ids=["alice", "bob"],
        capacity=4,
    )
    assert lobby["id"] == "lob1"
    body = json.loads(route.calls[0].request.content)
    assert body["key"] == "matchmaker_lobby_123"
    assert body["externalPlayerIds"] == ["alice", "bob"]
    assert body["capacity"] == 4


def test_lobbies_read_gets_from_games_lobbies(respx_mock, make_kraty):
    route = respx_mock.get(f"{BASE_URL}/server/v1/games/game_1/lobbies/lob1").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "id": "lob1",
                    "eventId": "e1",
                    "eventWindowId": "w1",
                    "leaderboardId": "lb1",
                    "mode": "lobby_matched",
                    "status": "active",
                    "capacity": 4,
                    "fillBy": None,
                    "participantCount": 2,
                    "botSlots": 0,
                    "startedAt": None,
                    "endsAt": None,
                }
            },
        )
    )
    k = make_kraty()
    k.lobbies.read("game_1", "lob1")
    assert route.call_count == 1
    assert route.calls[0].request.method == "GET"


# ─── PlayersClient ──────────────────────────────────────────────────


def test_players_get_returns_unified_snapshot(respx_mock, make_kraty):
    respx_mock.get(f"{BASE_URL}/server/v1/players/alice").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "player": {
                        "id": "p1",
                        "externalPlayerId": "alice",
                        "studioId": "s1",
                        "gameId": "g1",
                        "createdAt": "2026-01-01",
                        "updatedAt": "2026-01-01",
                    },
                    "inventory": [
                        {
                            "itemKey": "potion",
                            "quantity": 3,
                            "metadata": {},
                            "createdAt": "2026-01-01",
                            "updatedAt": "2026-01-01",
                        }
                    ],
                    "wallet": [
                        {
                            "economyKey": "gold",
                            "balance": 100,
                            "metadata": {},
                            "createdAt": "2026-01-01",
                            "updatedAt": "2026-01-01",
                        }
                    ],
                    "recentGrants": [],
                }
            },
        )
    )
    k = make_kraty()
    snap = k.players.get("alice")
    assert snap["player"]["externalPlayerId"] == "alice"
    assert len(snap["inventory"]) == 1
    assert snap["wallet"][0]["balance"] == 100


# ─── PlayersClient: GDPR delete + export ────────────────────────────


def test_players_delete_posts_reason_and_returns_outcome(respx_mock, make_kraty):
    route = respx_mock.post(f"{BASE_URL}/server/v1/players/alice/delete").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "playerId": "p1",
                    "externalPlayerId": "alice",
                    "anonymizedExternalId": "__deleted_abc-123__",
                    "deletedAt": "2026-06-11T10:00:00Z",
                    "attemptsAnonymized": 12,
                    "lobbiesAnonymized": 3,
                    "leaderboardsScrubbed": 4,
                    "status": "erased",
                }
            },
        )
    )
    k = make_kraty()
    out = k.players.delete("alice", reason="gdpr_erasure")
    assert out["status"] == "erased"
    assert out["anonymizedExternalId"].startswith("__deleted_")
    body = json.loads(route.calls[0].request.content)
    assert body["reason"] == "gdpr_erasure"


def test_players_delete_for_unknown_player_returns_no_op(respx_mock, make_kraty):
    respx_mock.post(f"{BASE_URL}/server/v1/players/ghost/delete").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "playerId": None,
                    "externalPlayerId": "ghost",
                    "anonymizedExternalId": None,
                    "deletedAt": "2026-06-11T10:00:00Z",
                    "attemptsAnonymized": 0,
                    "lobbiesAnonymized": 0,
                    "leaderboardsScrubbed": 0,
                    "status": "no_op_never_existed",
                }
            },
        )
    )
    k = make_kraty()
    out = k.players.delete("ghost")
    assert out["status"] == "no_op_never_existed"
    assert out["playerId"] is None


def test_players_export_gets_full_bundle(respx_mock, make_kraty):
    respx_mock.get(f"{BASE_URL}/server/v1/players/alice/export").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "schemaVersion": 1,
                    "exportedAt": "2026-06-11T10:00:00Z",
                    "player": {
                        "id": "p1",
                        "externalPlayerId": "alice",
                        "studioId": "s1",
                        "gameId": "g1",
                        "firstSeenAt": "2026-01-01T00:00:00Z",
                        "lastSeenAt": "2026-06-10T12:00:00Z",
                        "lastContextSnapshot": {"country": "PT"},
                        "registeredAt": "2026-01-01T00:00:00Z",
                        "secretRotatedAt": None,
                        "deletedAt": None,
                    },
                    "attempts": [{"id": "att1", "status": "completed"}],
                    "grants": [],
                    "inventory": [{"itemKey": "potion", "quantity": 3}],
                    "wallet": [{"economyKey": "gold", "balance": 500}],
                    "lobbies": [],
                }
            },
        )
    )
    k = make_kraty()
    exp = k.players.export("alice")
    assert exp["schemaVersion"] == 1
    assert exp["player"]["externalPlayerId"] == "alice"
    assert len(exp["attempts"]) == 1


def test_players_export_surfaces_not_found(respx_mock, make_kraty):
    respx_mock.get(f"{BASE_URL}/server/v1/players/ghost/export").mock(
        return_value=httpx.Response(
            404,
            json={"error": {"code": "not_found", "message": "Player 'ghost' not found"}},
        )
    )
    k = make_kraty()
    with pytest.raises(KratyServerError) as exc_info:
        k.players.export("ghost")
    assert exc_info.value.is_not_found is True


# ─── PlayersClient: friends (read-only) ─────────────────────────────


def test_players_friends_returns_list(respx_mock, make_kraty):
    route = respx_mock.get(f"{BASE_URL}/server/v1/players/alice/friends").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "friends": [
                        {
                            "externalPlayerId": "bob",
                            "displayIdentity": {"name": "Bob", "avatar": None, "country": "PT"},
                            "friendsSince": "2026-01-01T00:00:00Z",
                            "online": True,
                            "lastActiveAt": "2026-06-10T12:00:00Z",
                            "status": "in_match",
                        }
                    ]
                }
            },
        )
    )
    k = make_kraty()
    friends = k.players.friends("alice")
    assert len(friends) == 1
    assert friends[0]["externalPlayerId"] == "bob"
    assert friends[0]["online"] is True
    assert friends[0]["displayIdentity"]["name"] == "Bob"
    assert route.calls[0].request.method == "GET"


def test_players_friend_requests_returns_incoming_outgoing(respx_mock, make_kraty):
    respx_mock.get(f"{BASE_URL}/server/v1/players/alice/friends/requests").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "incoming": [
                        {
                            "requestId": "r1",
                            "direction": "incoming",
                            "player": {
                                "externalPlayerId": "carol",
                                "displayIdentity": {"name": "Carol"},
                            },
                            "createdAt": "2026-06-01T00:00:00Z",
                        }
                    ],
                    "outgoing": [],
                }
            },
        )
    )
    k = make_kraty()
    reqs = k.players.friend_requests("alice")
    assert len(reqs["incoming"]) == 1
    assert reqs["incoming"][0]["direction"] == "incoming"
    assert reqs["outgoing"] == []


def test_players_blocks_returns_list(respx_mock, make_kraty):
    respx_mock.get(f"{BASE_URL}/server/v1/players/alice/blocks").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "blocked": [
                        {
                            "externalPlayerId": "mallory",
                            "displayIdentity": None,
                            "blockedAt": "2026-05-01T00:00:00Z",
                        }
                    ]
                }
            },
        )
    )
    k = make_kraty()
    blocked = k.players.blocks("alice")
    assert len(blocked) == 1
    assert blocked[0]["externalPlayerId"] == "mallory"
    assert blocked[0]["displayIdentity"] is None


def test_players_friends_surfaces_not_found(respx_mock, make_kraty):
    respx_mock.get(f"{BASE_URL}/server/v1/players/ghost/friends").mock(
        return_value=httpx.Response(
            404,
            json={"error": {"code": "not_found", "message": "Player 'ghost' not found"}},
        )
    )
    k = make_kraty()
    with pytest.raises(KratyServerError) as exc_info:
        k.players.friends("ghost")
    assert exc_info.value.is_not_found is True


# ─── MigrateClient ──────────────────────────────────────────────────


def test_migrate_players_posts_rows_envelope(respx_mock, make_kraty):
    route = respx_mock.post(f"{BASE_URL}/server/v1/migrate/players").mock(
        return_value=httpx.Response(
            200,
            json={"data": {"applied": 2, "skipped": 0, "failed": 0, "failures": []}},
        )
    )
    k = make_kraty()
    rows = [
        {"externalPlayerId": "p_1", "idempotencyKey": "p_1"},
        {"externalPlayerId": "p_2", "idempotencyKey": "p_2", "contextSnapshot": {"country": "PT"}},
    ]
    out = k.migrate.players(rows)
    assert out["applied"] == 2
    body = json.loads(route.calls[0].request.content)
    assert body["rows"] == rows


def test_migrate_wallet_posts_amount_per_row(respx_mock, make_kraty):
    respx_mock.post(f"{BASE_URL}/server/v1/migrate/wallet").mock(
        return_value=httpx.Response(
            200,
            json={"data": {"applied": 1, "skipped": 0, "failed": 0, "failures": []}},
        )
    )
    k = make_kraty()
    out = k.migrate.wallet(
        [{"externalPlayerId": "p_1", "economyKey": "gold", "amount": 500, "idempotencyKey": "p_1:gold"}]
    )
    assert out["applied"] == 1


def test_migrate_inventory_returns_failures_for_bad_rows(respx_mock, make_kraty):
    respx_mock.post(f"{BASE_URL}/server/v1/migrate/inventory").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "applied": 1,
                    "skipped": 0,
                    "failed": 1,
                    "failures": [
                        {
                            "rowIndex": 1,
                            "externalPlayerId": "p_2",
                            "error": {"code": "unknown_item", "message": "item not found"},
                        }
                    ],
                }
            },
        )
    )
    k = make_kraty()
    out = k.migrate.inventory(
        [
            {"externalPlayerId": "p_1", "itemKey": "potion", "quantity": 3, "idempotencyKey": "p_1:potion"},
            {"externalPlayerId": "p_2", "itemKey": "gone", "quantity": 1, "idempotencyKey": "p_2:gone"},
        ]
    )
    assert out["failed"] == 1
    assert out["failures"][0]["error"]["code"] == "unknown_item"


# ─── HealthClient ───────────────────────────────────────────────────


def test_health_ping_returns_key_info(respx_mock, make_kraty):
    respx_mock.get(f"{BASE_URL}/server/v1/ping").mock(
        return_value=httpx.Response(
            200,
            json={
                "ok": True,
                "apiKey": {
                    "id": "k1",
                    "prefix": "sUUVdrM8",
                    "permissionSet": "server_integration",
                    "environment": "live",
                    "studioId": "s1",
                    "gameId": "g1",
                },
            },
        )
    )
    k = make_kraty()
    p = k.health.ping()
    assert p["ok"] is True
    assert p["apiKey"]["permissionSet"] == "server_integration"


GUILD_ID = "0b8a6c56-49bd-4d5a-9d38-1f2b6a5f9b3e"


def test_guilds_list_builds_query_and_unwraps(respx_mock, make_kraty):
    route = respx_mock.get(
        f"{BASE_URL}/server/v1/guilds?q=owls&player=alice&includeDisbanded=true&limit=5"
    ).mock(return_value=httpx.Response(200, json={"data": {"guilds": [], "total": 0}}))
    k = make_kraty()
    out = k.guilds.list(q="owls", player="alice", include_disbanded=True, limit=5)
    assert out == {"guilds": [], "total": 0}
    assert route.called


def test_guilds_reads(respx_mock, make_kraty):
    respx_mock.get(f"{BASE_URL}/server/v1/guilds/{GUILD_ID}").mock(
        return_value=httpx.Response(200, json={"data": {"guildId": GUILD_ID, "members": []}})
    )
    respx_mock.get(f"{BASE_URL}/server/v1/players/alice/guild").mock(
        return_value=httpx.Response(200, json={"data": {"guild": None, "role": None, "history": []}})
    )
    k = make_kraty()
    assert k.guilds.get(GUILD_ID)["guildId"] == GUILD_ID
    assert k.guilds.for_player("alice")["guild"] is None


def test_guilds_moderation(respx_mock, make_kraty):
    patch = respx_mock.patch(f"{BASE_URL}/server/v1/guilds/{GUILD_ID}").mock(
        return_value=httpx.Response(200, json={"data": {"guildId": GUILD_ID}})
    )
    remove = respx_mock.post(f"{BASE_URL}/server/v1/guilds/{GUILD_ID}/members/bob/remove").mock(
        return_value=httpx.Response(200, json={"data": {"disbanded": False, "guild": {}}})
    )
    leader = respx_mock.post(f"{BASE_URL}/server/v1/guilds/{GUILD_ID}/leader").mock(
        return_value=httpx.Response(200, json={"data": {"guildId": GUILD_ID}})
    )
    disband = respx_mock.post(f"{BASE_URL}/server/v1/guilds/{GUILD_ID}/disband").mock(
        return_value=httpx.Response(200, json={"data": {"guildId": GUILD_ID}})
    )
    k = make_kraty()
    k.guilds.update(GUILD_ID, name="Clean")
    k.guilds.remove_member(GUILD_ID, "bob")
    k.guilds.set_leader(GUILD_ID, "carol")
    k.guilds.disband(GUILD_ID)
    assert json.loads(patch.calls.last.request.content)["name"] == "Clean"
    assert remove.called and disband.called
    assert json.loads(leader.calls.last.request.content)["externalPlayerId"] == "carol"


def test_chat_reads_and_posts(respx_mock, make_kraty):
    conv = "0b8a6c56-49bd-4d5a-9d38-1f2b6a5f9b3e"
    lst = respx_mock.get(f"{BASE_URL}/server/v1/players/alice/chat/conversations?kind=direct").mock(
        return_value=httpx.Response(200, json={"data": {"conversations": [], "nextOffset": None}})
    )
    msgs = respx_mock.get(f"{BASE_URL}/server/v1/chat/conversations/{conv}/messages?after=3").mock(
        return_value=httpx.Response(200, json={"data": {"messages": [], "hasMore": False}})
    )
    ann = respx_mock.post(f"{BASE_URL}/server/v1/chat/channels/news/messages").mock(
        return_value=httpx.Response(201, json={"data": {"messageId": "m1", "senderKind": "server"}})
    )
    dele = respx_mock.delete(f"{BASE_URL}/server/v1/chat/messages/m1").mock(
        return_value=httpx.Response(200, json={"data": {"messageId": "m1", "deleted": True}})
    )
    k = make_kraty()
    assert k.chat.conversations_for("alice", kind="direct")["conversations"] == []
    assert k.chat.messages(conv, after=3)["hasMore"] is False
    assert k.chat.announce("news", text="Maintenance at 5pm")["senderKind"] == "server"
    assert k.chat.delete_message("m1")["deleted"] is True
    assert lst.called and msgs.called and ann.called and dele.called
    assert json.loads(ann.calls[0].request.content)["text"] == "Maintenance at 5pm"


def test_moderation_flow(respx_mock, make_kraty):
    reports = respx_mock.get(f"{BASE_URL}/server/v1/moderation/reports?status=open").mock(
        return_value=httpx.Response(200, json={"data": {"reports": [{"reportId": "r1"}]}})
    )
    resolve = respx_mock.post(f"{BASE_URL}/server/v1/players/bob/moderation/resolve").mock(
        return_value=httpx.Response(200, json={"data": {"decision": "mute", "reportsClosed": 1}})
    )
    restrict = respx_mock.post(f"{BASE_URL}/server/v1/players/bob/restrictions").mock(
        return_value=httpx.Response(201, json={"data": {"restrictionId": "x1"}})
    )
    lift = respx_mock.post(f"{BASE_URL}/server/v1/restrictions/x1/lift").mock(
        return_value=httpx.Response(200, json={"data": {"restrictionId": "x1", "active": False}})
    )
    k = make_kraty()
    assert k.moderation.reports(status="open")[0]["reportId"] == "r1"
    assert k.moderation.resolve("bob", decision="mute", durationHours=24)["reportsClosed"] == 1
    k.moderation.restrict("bob", kind="chat_mute", duration_hours=1)
    k.moderation.lift("x1")
    assert json.loads(resolve.calls[0].request.content)["durationHours"] == 24
    assert json.loads(restrict.calls[0].request.content)["kind"] == "chat_mute"
    assert reports.called and lift.called
