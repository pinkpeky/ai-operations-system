# Phase 68A Digital Human Commercial Delivery Link

## Purpose

Phase 68A connects generated digital-human video outputs back into the commercial operation closed loop.

The important boundary is that this phase is not a video generator and not a ComfyUI workflow selector. It assumes the digital-human job is already completed and a generated delivery asset already exists. Its job is to turn that generated asset into a prepared commercial asset request so normal deliverable packaging, approval, customer-machine handoff, result recording, and optimization can continue.

## Flow

```text
DigitalHumanVideoJob completed
  -> DigitalHumanAsset(video, generated)
  -> CommercialOperationAssetRequest(video, prepared)
  -> CommercialOperationDeliverable
  -> CommercialOperationExecutionRequest
  -> Customer-machine OpenClaw/Playwright handoff
  -> Result / observation / optimization loop
```

## API

```text
POST /api/v1/commercial-operations/{operation_id}/digital-human-delivery-link
```

Request fields:

- `digital_human_video_job_id`: required completed digital-human video job.
- `delivery_asset_id`: optional generated digital-human asset. If omitted, the service reads the delivery asset from the job output record.
- `content_draft_id`: optional approved content draft. If omitted, the service uses the first approved content draft when available.
- `step_key`: defaults to `content_production`.
- `channel`, `title`, `purpose`, `metadata`: optional commercial asset-request shaping fields.

Response fields:

- `link_status`: `created` or `reused`.
- `digital_human_video_job_id`: source job.
- `delivery_asset_id`: generated video asset.
- `deliverable_ready`: true when an approved content draft is linked.
- `asset_request`: prepared commercial `video` asset request.
- `next_actions`: operator-facing next steps.
- `boundaries`: explicit no-publish and no-runtime-mutation boundaries.

## Data Contract

The prepared commercial asset request stores:

- `asset_type=video`
- `request_status=prepared`
- `source_materials` including the digital-human job, generated delivery asset, and delivery source URI
- `readiness_checks` for completed job, generated asset presence, human review, and customer-machine approval
- `asset_metadata.phase=68A`
- `asset_metadata.digital_human_delivery_asset_id`
- `asset_metadata.delivery_source_uri`
- `asset_metadata.delivery_output_count`
- `handoff_payload.digital_human_video_job`
- `handoff_payload.digital_human_delivery_asset`

When a linked approved content draft exists, the main Agent deliverable path can include the prepared asset request because `list_asset_requests(content_draft_id=draft.id)` returns it.

## Boundaries

Phase 68A does not:

- mutate ComfyUI workflows
- resubmit ComfyUI prompts
- upload files to ComfyUI
- download models
- install workflows
- publish to social media
- control customer accounts
- run OpenClaw or Playwright
- bypass deliverable or execution approvals
- mutate runtime configuration
- restart services
- rebuild client packages

## Verification

Covered by `tests/test_digital_human_execution_loop.py::test_digital_human_delivery_asset_links_into_commercial_deliverable`.

The test creates a commercial operation, approves a content draft, completes a digital-human ComfyUI output ingestion, links the generated video asset into a prepared commercial asset request, and verifies that a deliverable can package that asset request.
