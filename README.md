
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

      # LAST STEP - AI Failure Analysis
      - name: AI Failure Analysis
        if: failure()
        run: |
          APP_NAME=${{ steps.platform.outputs.app_name }}
          SHA=${{ github.event.client_payload.sha }}

          # Collect error logs
          ERROR_LOG=""
          for f in /tmp/build-output.txt /tmp/push-output.txt; do
            if [ -f "$f" ]; then
              ERROR_LOG="${ERROR_LOG}\n$(tail -30 $f)"
            fi
          done

          # Escape for JSON
          ESCAPED_LOG=$(echo -e "$ERROR_LOG" | python3 -c "
          import sys, json
          print(json.dumps(sys.stdin.read()))
          ")

          # Call Gemini API
          AI_RESPONSE=$(curl -s -X POST \
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${{ secrets.GEMINI_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d "{
              \"contents\": [{
                \"parts\": [{
                  \"text\": \"You are a DevOps expert. CI/CD pipeline failed for app '${APP_NAME}' commit '${SHA}'.\n\nError logs:\n${ESCAPED_LOG}\n\nProvide:\n1. Root Cause\n2. How to Fix\n3. Steps Developer Should Take\n4. How to Prevent\n\nBe concise and developer friendly.\"
                }]
              }]
            }")

          # Extract response
          AI_EXPLANATION=$(echo "$AI_RESPONSE" | python3 -c "
          import sys, json
          data = json.load(sys.stdin)
          print(data['candidates'][0]['content']['parts'][0]['text'])
          " 2>/dev/null || echo "AI analysis unavailable")

          # Post to developer's PR
          curl -s -X POST \
            -H "Authorization: token ${{ steps.app-token.outputs.token }}" \
            -H "Accept: application/vnd.github.v3+json" \
            https://api.github.com/repos/${{ github.event.client_payload.repo }}/commits/${{ github.event.client_payload.sha }}/comments \
            -d "{
              \"body\": \"## 🤖 AI Pipeline Failure Analysis\n\n${AI_EXPLANATION}\n\n---\n> App: ${APP_NAME}\n> Commit: ${SHA}\n> *Analyzed by Google Gemini AI* 🤖\"
            }"

      - name: Build Docker Image
        run: |
          IMAGE_NAME=${{ steps.platform.outputs.app_name }}
          SHA=${{ github.event.client_payload.sha }}
          docker build \
            -t ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPO }}/${IMAGE_NAME}:${SHA} \
            . 2>&1 | tee /tmp/build-output.txt
          exit ${PIPESTATUS[0]}

      - name: Push Docker Image
        run: |
          IMAGE_NAME=${{ steps.platform.outputs.app_name }}
          SHA=${{ github.event.client_payload.sha }}
          docker push \
            ${{ env.REGION }}-docker.pkg.dev/${{ env.PROJECT_ID }}/${{ env.REPO }}/${IMAGE_NAME}:${SHA} \
            2>&1 | tee /tmp/push-output.txt
          exit ${PIPESTATUS[0]}

