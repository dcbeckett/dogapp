#!/bin/bash

# AWS Lambda Deployment Script for Dog Voting App
# Run this script to deploy your app to AWS

set -e

echo "🚀 Starting AWS Lambda deployment..."

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run:"
    echo "aws configure"
    exit 1
fi

# Set variables
STACK_NAME="dog-voting-app"
REGION="${AWS_REGION:-us-east-1}"
BUCKET_PREFIX="dog-voting-app-bucket"

echo "📍 Deploying to region: $REGION"
echo "📦 Stack name: $STACK_NAME"

# Create deployment package
echo "📦 Creating deployment package..."
rm -rf deployment-package
mkdir deployment-package

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt -t deployment-package/

# Copy application files
cp lambda_app.py deployment-package/
cp -r templates deployment-package/
cp -r static deployment-package/

# Create ZIP file
cd deployment-package
zip -r ../lambda-deployment.zip . -q
cd ..

echo "✅ Deployment package created: lambda-deployment.zip"

# Deploy CloudFormation stack
echo "🏗️ Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file cloudformation-template.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides BucketName=$BUCKET_PREFIX \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --region $REGION

echo "✅ CloudFormation stack deployed!"

# Get the Lambda function name from the stack
LAMBDA_FUNCTION=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
    --output text)

# Update Lambda function code
echo "🔄 Updating Lambda function code..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION \
    --zip-file fileb://lambda-deployment.zip \
    --region $REGION

echo "✅ Lambda function updated!"

# Get the website URL
WEBSITE_URL=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`WebsiteURL`].OutputValue' \
    --output text)

# Get the S3 bucket name
S3_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`S3BucketName`].OutputValue' \
    --output text)

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Deployment Summary:"
echo "   🌐 Website URL: $WEBSITE_URL"
echo "   🪣 S3 Bucket: $S3_BUCKET"
echo "   ⚡ Lambda Function: $LAMBDA_FUNCTION"
echo "   📍 Region: $REGION"
echo ""
echo "💰 Estimated monthly cost for light usage: $0.00 - $0.50"
echo ""
echo "🔗 Your dog voting app is now live at:"
echo "   $WEBSITE_URL"
echo ""
echo "🎯 Next steps:"
echo "   1. Visit your website URL above"
echo "   2. The app will automatically fetch 100 pictures on first load"
echo "   3. Start swiping and voting!"
echo ""

# Clean up
rm -rf deployment-package
rm lambda-deployment.zip

echo "🧹 Cleanup completed!"
echo "✨ Happy dog voting! 🐕" 