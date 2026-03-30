# ADR-001: Cloud Run Load Balancer Setup

**Date**: 2026-03-30
**Status**: In Progress

## Context

Cloud Run domain mappings are deprecated for new regions. We use a Global External Application Load Balancer with a Serverless NEG.

## Infrastructure Created

- **Static IP**: `34.110.250.203` (resource: `the-loop-ip`)
- **SSL Certificate**: `the-loop-cert` (Google-managed, domain: loop.oute.pro, status: PROVISIONING)
- **Artifact Registry**: `us-central1-docker.pkg.dev/theloopoute/the-loop`
- **WIF Pool**: `github-pool` with OIDC provider `github-provider` (scoped to `renatobardi/the-loop`)
- **Deployer SA**: `github-deployer@theloopoute.iam.gserviceaccount.com`
  - Roles: run.admin, artifactregistry.writer, iam.serviceAccountUser, datastore.user

## DNS Configuration Required

Point `loop.oute.pro` to the static IP:

```
loop.oute.pro  A  34.110.250.203
```

## Remaining Steps (after first Cloud Run deploy)

After the first GitHub Actions deploy creates the Cloud Run service, run:

```bash
# Create Serverless NEG
gcloud compute network-endpoint-groups create the-loop-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=the-loop \
  --project=theloopoute

# Backend service
gcloud compute backend-services create the-loop-backend \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --global --project=theloopoute

gcloud compute backend-services add-backend the-loop-backend \
  --global \
  --network-endpoint-group=the-loop-neg \
  --network-endpoint-group-region=us-central1 \
  --project=theloopoute

# URL map
gcloud compute url-maps create the-loop-urlmap \
  --default-service=the-loop-backend \
  --project=theloopoute

# HTTPS proxy
gcloud compute target-https-proxies create the-loop-https-proxy \
  --url-map=the-loop-urlmap \
  --ssl-certificates=the-loop-cert \
  --project=theloopoute

# Forwarding rule (HTTPS)
gcloud compute forwarding-rules create the-loop-https-rule \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --network-tier=PREMIUM \
  --address=the-loop-ip \
  --target-https-proxy=the-loop-https-proxy \
  --global --ports=443 \
  --project=theloopoute

# HTTP → HTTPS redirect
gcloud compute url-maps import the-loop-http-redirect \
  --global --source /dev/stdin --project=theloopoute <<'EOF'
name: the-loop-http-redirect
defaultUrlRedirect:
  httpsRedirect: true
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
EOF

gcloud compute target-http-proxies create the-loop-http-proxy \
  --url-map=the-loop-http-redirect \
  --project=theloopoute

gcloud compute forwarding-rules create the-loop-http-rule \
  --load-balancing-scheme=EXTERNAL_MANAGED \
  --network-tier=PREMIUM \
  --address=the-loop-ip \
  --target-http-proxy=the-loop-http-proxy \
  --global --ports=80 \
  --project=theloopoute
```
