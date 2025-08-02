#!/bin/bash

# Cloud Build deployment script for chatterbox-whisper

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="chatterbox-whisper"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying Chatterbox Whisper to Google Cloud${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if PROJECT_ID is set
if [ "$PROJECT_ID" = "your-project-id" ]; then
    echo -e "${RED}❌ Please provide your Google Cloud Project ID as the first argument${NC}"
    echo "Usage: $0 <PROJECT_ID> [REGION]"
    exit 1
fi

echo -e "${YELLOW}📋 Project ID: $PROJECT_ID${NC}"
echo -e "${YELLOW}📍 Region: $REGION${NC}"
echo -e "${YELLOW}🏷️  Service Name: $SERVICE_NAME${NC}"

# Set the project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Build and deploy using Cloud Build
echo -e "${YELLOW}🏗️  Starting Cloud Build...${NC}"
gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=$REGION

echo -e "${GREEN}✅ Deployment complete!${NC}"

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

if [ ! -z "$SERVICE_URL" ]; then
    echo -e "${GREEN}🌐 Your service is available at:${NC}"
    echo -e "${GREEN}   - Service URL: $SERVICE_URL${NC}"
    echo -e "${GREEN}   - API Docs: $SERVICE_URL/docs${NC}"
    echo -e "${GREEN}   - Health Check: $SERVICE_URL/health${NC}"
else
    echo -e "${YELLOW}⚠️  Could not retrieve service URL. Check the Cloud Console for deployment status.${NC}"
fi
