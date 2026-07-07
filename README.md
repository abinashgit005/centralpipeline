# centralpipeline

GKE cluster setup command:

```yaml
gcloud container clusters create dev-cluster \
  --project=poc101-500018 \
  --region=asia-south1 \
  --num-nodes=1 \
  --machine-type=e2-medium \
  --disk-size=20GB \
  --no-enable-basic-auth \
  --no-issue-client-certificate
  ```
