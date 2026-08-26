# Streaming

The streaming client connects to a supported Central Streaming API endpoint, decodes its protobuf payloads, and passes dictionaries to a callback.

## Supported topics

| Event | Description |
| --- | --- |
| `audit-trail-events` | Audit trail |
| `location` | Location |
| `rssi-events` | RSSI  |
| `geofence` | Geofence |
| `ap-events` | Access point |
| `clients-events` | Client |
| `switch-events` | Switch |
| `alert-events` | Alert |

Pass the event name to `Streaming`. Optional filters are sent as the `event-types` query parameter for supported topics. Refer these [Developer Hub guides](https://developer.arubanetworks.com/new-central/docs/streaming-api-events) to get details for supported events including filters(or `event-types)

## Streaming Module

::: pycentral.streaming.streaming

---
