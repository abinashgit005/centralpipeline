
### GKE cluster setup command:
[reference](https://docs.cloud.google.com/sdk/gcloud/reference/container/clusters/create)
```yaml
gcloud config set project central-pipeline-515411
gcloud container clusters get-credentials poc-cluster --region us-central1

# 1. Stop ArgoCD first, or its self-heal undoes everything below
kubectl scale deployment --all -n argocd --replicas=0
kubectl scale statefulset --all -n argocd --replicas=0

# 2. Stop the app and release the load balancer
kubectl scale deployment devrepo -n dev --replicas=0
kubectl delete svc devrepo-service -n dev

# 3. Release the ArgoCD UI load balancer
kubectl patch svc argocd-server -n argocd -p '{"spec":{"type":"ClusterIP"}}'
  ```
  ```yaml
kubectl scale statefulset --all -n argocd --replicas=1
kubectl scale deployment --all -n argocd --replicas=1
kubectl patch svc argocd-server -n argocd -p '{"spec":{"type":"LoadBalancer"}}'
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
gcloud services enable aiplatform.googlwapis.com --project=central-pipeline-515411
```
