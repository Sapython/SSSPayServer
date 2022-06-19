gcloud builds submit . --tag gcr.io/ssspay-prod/ssspay-proxy-server
gcloud run deploy ssspay-proxy-server --image gcr.io/ssspay-prod/ssspay-proxy-server --platform managed --allow-unauthenticated --region asia-south2 --vpc-connector ssspay-connector --vpc-egress all-traffic