# Chai Counter ☕

A tiny web app for learning **containers** and **Azure Container Apps**, step by step.
You pick how many cups of chai you want, and it adds up the total: 2 cups × ₹20 = ₹40. That's all it does — on
purpose. The app stays simple, so you can watch what the platform does around it: package it, store it in a registry,
put it on the internet, scale it, ship a new version, and clean up.

It's the practice app for the **Sketch the Cloud** videos on Azure Container Apps (Hindi and English).

| File | What it does |
|---|---|
| `app.py` | The web app (Python + Flask): one page that adds up the cups. It also shows which **revision** and **replica** answered — Azure Container Apps sets those for every container. |
| `templates/index.html` | The page you see. |
| `requirements.txt` | The app's dependencies (Flask, and gunicorn as the web server). |
| `Dockerfile` | The recipe for the container image: runtime + dependencies + code, and how to start it. |
| `.dockerignore` | Files the image doesn't need. |

Two versions live in two branches: **`v1`** (the first design) and **`v2`** (a new design); `main` is the latest.
Compare them on GitHub ([v1…v2](https://github.com/realsanket/chai-counter/compare/v1...v2)) or with
`git diff origin/v1 origin/v2`.

---

## 1. Run it on your laptop
You need Python 3.10+.
```bash
git clone https://github.com/realsanket/chai-counter
cd chai-counter
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Open http://localhost:8080 — change the cups with − and +. The footer says `revision local · replica local`,
because nothing is managing your laptop's copy.

## 2. Package it as a container image
With Docker on your laptop:
```bash
docker build -t chai-counter:v1 .
docker run -p 8080:8080 chai-counter:v1          # same app, now from the image
```
Read the `Dockerfile` top to bottom — each step is commented.

## 3. Put the image in Azure Container Registry
In [Azure Cloud Shell](https://shell.azure.com) (Bash — no install needed):
```bash
RG=rg-chai-demo
LOCATION=centralindia
ACR=chaicounter$RANDOM            # registry names are global: lowercase letters and numbers

az group create --name $RG --location $LOCATION
az acr create --resource-group $RG --name $ACR --sku Basic

git clone https://github.com/realsanket/chai-counter && cd chai-counter
git checkout v1
az acr build --registry $ACR --image chai-counter:v1 .     # builds the image in Azure and pushes it
```
`az acr build` builds in the cloud, so you don't need Docker. (If your subscription runs on free credits, ACR Tasks
may be paused for it — then build with Docker and `docker push` to `$ACR.azurecr.io`.)

## 4. Run it on Azure Container Apps
```bash
az containerapp env create --resource-group $RG --name chai-env --location $LOCATION

az containerapp create --resource-group $RG --name chai-counter --environment chai-env \
  --image $ACR.azurecr.io/chai-counter:v1 \
  --registry-server $ACR.azurecr.io --registry-identity system \
  --target-port 8080 --ingress external \
  --cpu 0.25 --memory 0.5Gi

az containerapp show --resource-group $RG --name chai-counter \
  --query properties.configuration.ingress.fqdn --output tsv     # open https://<that address>
```
`--registry-identity system` lets the app pull from your registry with its managed identity — no passwords.

## 5. Watch it scale
```bash
az containerapp update --resource-group $RG --name chai-counter \
  --min-replicas 1 --max-replicas 3 \
  --scale-rule-name http-rule --scale-rule-type http --scale-rule-http-concurrency 10

URL=https://$(az containerapp show -g $RG -n chai-counter --query properties.configuration.ingress.fqdn -o tsv)
seq 3000 | xargs -P 30 -I{} curl -s -o /dev/null "$URL"          # a burst of requests
az containerapp replica list --resource-group $RG --name chai-counter --output table
```
Refresh the page a few times: the footer shows different replicas answering.
Set `--min-replicas 0` and leave it idle for a few minutes — it scales to zero; the next visit starts it again
(a cold start).

## 6. Ship v2 and split the traffic
```bash
git checkout v2
az acr build --registry $ACR --image chai-counter:v2 .

az containerapp revision set-mode --resource-group $RG --name chai-counter --mode multiple
az containerapp revision list --resource-group $RG --name chai-counter --output table     # note the current revision
az containerapp update --resource-group $RG --name chai-counter \
  --image $ACR.azurecr.io/chai-counter:v2 --revision-suffix v2
az containerapp ingress traffic set --resource-group $RG --name chai-counter \
  --revision-weight <current-revision>=90 chai-counter--v2=10
```
Refresh a few times: most visits show v1, some show v2. Traffic weights are shares, not a fixed pattern.

## 7. Clean up
```bash
az group delete --name $RG --yes
```
Deleting the resource group deletes everything in it: the registry, the environment and the app. Nothing keeps
running or costing money.

---

Facts and limits change — check [Azure Container Apps on Microsoft Learn](https://learn.microsoft.com/azure/container-apps/overview)
for the current details. MIT licence.
