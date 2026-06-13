---
id: websocket_realtime_patterns
version: 1.0.0
owners: [backend_lead, frontend_lead]
tags: [websocket, realtime, sse, pubsub, redis-pubsub, socket.io, presence]
when_to_use: |
  When the server needs to push data to clients without polling:
  chat, live dashboards, collaborative editing, live order tracking,
  notifications. Use SSE for server→client only; WebSocket for bidirectional.
inputs:
  - update_frequency, message_direction, client_count, message_ordering_required
outputs:
  - "realtime_design: transport choice + connection management + pub/sub topology + scaling strategy"
---

# WebSocket & Real-Time Patterns

> Don't default to WebSocket. Use the simplest transport that works.
> SSE → polling → WebSocket (in order of increasing complexity).

## Transport selection

| Need | Best transport |
|---|---|
| Server pushes, client reads only (notifications, dashboards) | SSE |
| Client sends occasionally, server pushes frequently | SSE + REST POST |
| Bidirectional, low latency (chat, gaming, collaboration) | WebSocket |
| Infrequent updates, simple implementation | Long polling |

## Server-Sent Events (SSE)

```python
# FastAPI SSE
from sse_starlette.sse import EventSourceResponse

@router.get("/stream/orders/{order_id}")
async def stream_order(order_id: str, request: Request, user=Depends(get_user)):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            order = await Order.get(order_id)
            if order.customer_id != user.id:
                break  # auth check on every event
            yield {"data": json.dumps({"status": order.status}), "event": "order_update"}
            if order.status in ("delivered", "cancelled"):
                break
            await asyncio.sleep(2)

    return EventSourceResponse(event_generator())
```

## WebSocket with Redis pub/sub (horizontal scaling)

The problem with WebSocket + multiple server instances:
```
Client A → Server 1 (WebSocket)
Client B → Server 2 (WebSocket)
Server 1 processes event → needs to send to Client B on Server 2
```

Solution: Redis pub/sub as message bus between instances.

```python
# FastAPI + Redis pub/sub
import aioredis

@router.websocket("/ws/chat/{room_id}")
async def websocket_chat(ws: WebSocket, room_id: str):
    await ws.accept()
    redis = await aioredis.create_redis_pool('redis://localhost')
    channel = await redis.subscribe(f"room:{room_id}")

    async def reader():
        async for message in channel[0].iter():
            if message:
                await ws.send_text(message.decode())

    async def writer():
        try:
            while True:
                data = await ws.receive_text()
                msg = json.dumps({"user": user.id, "text": data})
                await redis.publish(f"room:{room_id}", msg)
        except WebSocketDisconnect:
            pass

    await asyncio.gather(reader(), writer())
    redis.close()
```

## Connection management

```python
# Track active connections in memory (per instance)
class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, ws: WebSocket, room_id: str):
        await ws.accept()
        self.connections[room_id].add(ws)

    async def disconnect(self, ws: WebSocket, room_id: str):
        self.connections[room_id].discard(ws)
        if not self.connections[room_id]:
            del self.connections[room_id]

    async def broadcast(self, room_id: str, message: str):
        dead = set()
        for ws in self.connections[room_id]:
            try:
                await ws.send_text(message)
            except:
                dead.add(ws)
        for ws in dead:
            await self.disconnect(ws, room_id)
```

## Heartbeat / keepalive

```python
# Send ping every 30s, close if no pong within 10s
async def keepalive(ws: WebSocket):
    while True:
        await asyncio.sleep(30)
        try:
            await ws.send_text(json.dumps({"type": "ping"}))
        except:
            break  # client disconnected
```

## Anti-patterns

- **WebSocket for one-way push**: SSE is simpler and works through HTTP/2 multiplexing.
- **Broadcasting to all clients without room/channel filtering**: every message hits every client.
- **No heartbeat**: load balancers kill idle connections after 60-120s. Clients think they're connected.
- **State in WebSocket handlers**: use Redis/DB for state. Handlers die on deploy.
- **No reconnection logic on client**: clients must implement exponential backoff reconnect.

## Validation

- [ ] Transport choice justified (SSE vs WebSocket).
- [ ] Redis pub/sub used for multi-instance coordination.
- [ ] Heartbeat implemented (30s ping, 10s timeout).
- [ ] Auth checked on connection establishment AND on sensitive messages.
- [ ] Client implements automatic reconnection with backoff.
