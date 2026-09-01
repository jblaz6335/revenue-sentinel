param(
  [Parameter(Mandatory = $true)][string]$ProjectId,
  [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"
$serviceName = "revenue-sentinel"
$runtimeServiceAccount = "revenue-sentinel-runtime@$ProjectId.iam.gserviceaccount.com"

gcloud config set project $ProjectId
gcloud services enable run.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com aiplatform.googleapis.com artifactregistry.googleapis.com logging.googleapis.com monitoring.googleapis.com
gcloud run deploy $serviceName `
  --source . `
  --region $Region `
  --allow-unauthenticated `
  --service-account $runtimeServiceAccount `
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$ProjectId,GOOGLE_CLOUD_LOCATION=global,GOOGLE_GENAI_USE_VERTEXAI=true,REVENUE_SENTINEL_LEDGER=firestore" `
  --min-instances 1 `
  --max-instances 2 `
  --concurrency 20 `
  --cpu 1 `
  --cpu-throttling `
  --memory 512Mi `
  --timeout 60
