
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

kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl get pods -n argocd -w

kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
kubectl get svc argocd-server -n argocd

kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath="{.data.password}" | base64 -d; echo
vFF511wYpkjltljc
kubectl get svc argocd-server -n argocd
```
gh key is being used as dispatch token to trigger from dev-repo to central pipeline and gitops_token for GCP intraction.

```yaml
gcloud services enable aiplatform.googlwapis.com --project=poc101-500018
```
