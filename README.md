
### GKE cluster setup command:
[reference](https://docs.cloud.google.com/sdk/gcloud/reference/container/clusters/create)
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
  ```yaml
  gcloud container clusters resize dev-cluster \
  --project=poc101-500018 \
  --region=asia-south1 \
  --num-nodes=0 \
  --node-pool=default-pool
  ```
### Argocd 
```bash
kubectl create namespace argocd

# Download the manifest 
curl -o argocd-install.yaml \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
# apply from local file
kubectl apply -n argocd -f argocd-install.yaml

kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

kubectl get secret argocd-initial-admin-secret \
  -n argocd \
  -o jsonpath="{.data.password}" | base64 -d && echo
QL9UsjlylReMgn3u
kubectl get svc argocd-server -n argocd
```
gh key is being used as dispatch token and pat token as well.


      # ── AI Failure Analysis using Gemini ──
      - name: AI Failure Analysis
        if: failure()
        run: |
          APP_NAME=${{ steps.platform.outputs.app_name }}
          SHA=${{ github.event.client_payload.sha }}

          # Capture error logs
          BUILD_LOG=""
          if [ -f /tmp/build-output.txt ]; then
            BUILD_LOG=$(tail -50 /tmp/build-output.txt)
          fi

          # Get GCP Access Token
          # (already authenticated via GCP_SA_KEY)
          ACCESS_TOKEN=$(gcloud auth print-access-token)

          # Escape log for JSON
          ESCAPED_LOG=$(echo "$BUILD_LOG" | python3 -c "
          import sys, json
          print(json.dumps(sys.stdin.read()))
          ")

          # Call Gemini API
          AI_RESPONSE=$(curl -s -X POST \
            "https://us-central1-aiplatform.googleapis.com/v1/projects/poc101-500018/locations/us-central1/publishers/google/models/gemini-1.5-flash:generateContent" \
            -H "Authorization: Bearer ${ACCESS_TOKEN}" \
            -H "Content-Type: application/json" \
            -d "{
              \"contents\": [{
                \"role\": \"user\",
                \"parts\": [{
                  \"text\": \"You are a DevOps expert. A CI/CD pipeline failed for app '${APP_NAME}' at commit '${SHA}'.\n\nActual error logs:\n${ESCAPED_LOG}\n\nProvide:\n1. 🔍 Root Cause\n2. 🛠️ How to Fix\n3. 🚀 Steps Developer Should Take\n4. 🛡️ How to Prevent in Future\n\nBe specific and developer friendly.\"
                }]
              }],
              \"generationConfig\": {
                \"temperature\": 0.2,
                \"maxOutputTokens\": 1024
              }
            }")

          # Extract Gemini response
          AI_EXPLANATION=$(echo "$AI_RESPONSE" | python3 -c "
          import sys, json
          data = json.load(sys.stdin)
          print(data['candidates'][0]['content']['parts'][0]['text'])
          ")

          echo "AI Analysis: $AI_EXPLANATION"

          # Post to developer's PR as comment
          curl -s -X POST \
            -H "Authorization: token ${{ steps.app-token.outputs.token }}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/${{ github.event.client_payload.repo }}/commits/${{ github.event.client_payload.sha }}/comments \
            -d "{
              \"body\": \"## 🤖 AI Pipeline Failure Analysis\n\n${AI_EXPLANATION}\n\n---\n> Pipeline failed at: Build Stage\n> App: ${APP_NAME}\n> Commit: ${SHA}\n> *Analyzed by Google Gemini AI* 🤖\"
            }"

