# 🚀 AWS Deployment Guide

Deploy your Dog Voting App to AWS Lambda for **ultra-low cost** serverless hosting!

## 💰 Cost Estimate
- **Monthly cost**: $0.00 - $0.50 for occasional use
- **First 1M requests**: FREE
- **Perfect for**: Apps used 1-2 times per month

## 📋 Prerequisites

1. **AWS Account** - [Sign up here](https://aws.amazon.com/free/)
2. **AWS CLI** - [Install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## 🔧 One-Time Setup

1. **Configure AWS credentials**:
   ```bash
   aws configure
   ```
   Enter your:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Output format: `json`

## 🚀 Deploy Your App

**Super simple - just run one command:**

```bash
./deploy.sh
```

The script will:
- ✅ Create all AWS resources (Lambda, S3, DynamoDB, API Gateway)
- ✅ Package and upload your app
- ✅ Set up the database
- ✅ Give you a live website URL
- ✅ Handle all the complex AWS configuration

## 🎯 What Gets Created

- **Lambda Function**: Runs your Flask app serverlessly
- **S3 Bucket**: Stores uploaded dog pictures
- **DynamoDB Table**: Stores votes and picture metadata  
- **API Gateway**: Provides the web URL
- **IAM Roles**: Secure permissions

## 📊 After Deployment

You'll get output like:
```
🎉 Deployment completed successfully!

📊 Deployment Summary:
   🌐 Website URL: https://abc123.execute-api.us-east-1.amazonaws.com/prod/
   🪣 S3 Bucket: dog-voting-app-bucket-123456789
   ⚡ Lambda Function: dog-voting-app
   📍 Region: us-east-1

💰 Estimated monthly cost for light usage: $0.00 - $0.50

🔗 Your dog voting app is now live at:
   https://abc123.execute-api.us-east-1.amazonaws.com/prod/
```

## 🎉 Features on AWS

- ✅ **100 pictures minimum** - Auto-downloads from dog APIs
- ✅ **Swipe interface** - Works perfectly on mobile
- ✅ **Cat attention test** - Random cats mixed in
- ✅ **Auto-scaling** - Handles traffic spikes
- ✅ **Global CDN** - Fast loading worldwide
- ✅ **No server management** - 100% serverless

## 🧹 Cleanup (Optional)

To delete everything and stop charges:
```bash
aws cloudformation delete-stack --stack-name dog-voting-app
```

## 🤔 Troubleshooting

**"AWS CLI not found"**
- Install AWS CLI first: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html

**"AWS credentials not configured"**
- Run `aws configure` with your access keys

**"Access Denied"**
- Make sure your AWS user has admin permissions or CloudFormation access

**Cold start delays**
- First request after inactivity may take 2-3 seconds (normal for Lambda)

## 🎯 Perfect For

- ✅ Personal projects
- ✅ Demos and portfolios  
- ✅ Apps with sporadic usage
- ✅ Cost-conscious hosting
- ✅ Zero server maintenance

Your dog voting app will be **live on the internet** with a real URL that you can share with anyone! 🌐🐕 