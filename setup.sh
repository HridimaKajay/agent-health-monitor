#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Agent Health Monitor Setup${NC}"

# Load environment
source .env
echo -e "${GREEN}✅ Environment loaded${NC}"

# Check Python
python3 --version || { echo -e "${RED}❌ Python3 not found${NC}"; exit 1; }

# Create virtual environment
echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}📥 Installing dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Verify Google Cloud
echo -e "${YELLOW}🔐 Verifying Google Cloud setup...${NC}"
gcloud auth list
gcloud config list | grep project


# Create BigQuery dataset
echo -e "${YELLOW}📊 Creating BigQuery schema...${NC}"
python data/create_bigquery_schema.py

echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. python data/generate_synthetic_traces.py  (generate test data)"
echo "2. python data/init_firestore.py            (initialize Firestore)"