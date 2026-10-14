# Skip Empty GLP Device Batches

## Context

`Devices.add_devices` delegates requests to `__add_dev` separately for network,
compute, and storage devices when the total input exceeds the per-request limit.
It currently invokes all three helpers even when one or more category lists are
empty. Each empty helper call sends a POST with an empty category and waits for
the POST rate-limit interval, adding network traffic and up to 15 seconds of
avoidable delay per unused category. The current helper calls also omit the
required `conn` argument, causing this path to raise `TypeError` before sending
any request.

## Approaches

1. **Skip empty categories in `add_devices` (recommended).** Dispatch only
   categories containing devices. This is a small local change, preserves the
   request and ordering for every non-empty category, and avoids calls that
   cannot add devices.
2. **Refactor batching and pacing across categories.** Build one queue of
   category batches and centralize rate-limit scheduling. This could also avoid
   unnecessary waits, but changes more of the batching behavior and requires
   care around workspace-wide rate limits.
3. **Tune pagination and response transformations.** Remove temporary
   allocations and repeated work in scope loading. These changes have lower
   impact on the specific GLP device onboarding path and do not address its
   unnecessary API calls.

## Design

In the existing `count > INPUT_SIZE` branch, call `__add_dev(conn, device_type,
device_list)` only when the category input list is non-empty. Passing `conn`
matches the helper's existing signature and is required for its request and
logging behavior. Preserve the current network, compute, storage order, return
format for each dispatched category, and all existing request chunking and
rate-limit behavior. Leave the single-request branch unchanged.

## Compatibility and validation

The optimization removes empty-category requests. Calls for supplied devices
retain their request payloads and order, and the >5-device branch becomes
callable by passing the connection to its helper. Validate with a mocked
connection that more than five devices in one category generate requests only
for that category, and that mixed non-empty categories still dispatch in order
without empty-category requests. Run the repository's available checks.
