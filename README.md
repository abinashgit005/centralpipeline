
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
  gcloud container clusters create dev-cluster \
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
