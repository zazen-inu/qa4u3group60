# AWS Lambda & S3 デプロイガイド

このガイドでは、食品原材料最適化アプリケーションをAWS LambdaとS3を使用したサーバーレスアーキテクチャにデプロイする方法を説明します。

## 前提条件

- AWS CLIがインストールされていること
- AWS認証情報が設定されていること
- Serverless Frameworkがインストールされていること
- OpenAI APIキーが利用可能であること

## 1. バックエンドのデプロイ（AWS Lambda）

### 1.1 依存関係のインストール

```bash
cd lambda_app
pip install -r requirements.txt -t .
```

### 1.2 環境変数の設定

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 1.3 Serverless Frameworkを使用したデプロイ

```bash
npm install -g serverless
serverless deploy
```

デプロイが完了すると、以下のような出力が表示されます：

```
Service Information
service: food-optimizer
stage: dev
region: ap-northeast-1
stack: food-optimizer-dev
resources: 12
api keys:
  None
endpoints:
  POST - https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/analyze
  OPTIONS - https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/analyze
functions:
  analyze: food-optimizer-dev-analyze
layers:
  None
```

表示されたエンドポイントURLをメモしておきます。

## 2. フロントエンドのデプロイ（S3）

### 2.1 S3バケットの作成

```bash
aws s3 mb s3://food-optimizer-frontend
aws s3 website s3://food-optimizer-frontend --index-document index.html
```

### 2.2 APIエンドポイントの更新

`s3_frontend/script.js`ファイルを編集し、APIエンドポイントを実際のLambda関数のURLに更新します：

```javascript
const API_ENDPOINT = 'https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/analyze';
```

### 2.3 S3バケットへのアップロード

```bash
cd s3_frontend
aws s3 sync . s3://food-optimizer-frontend --acl public-read
```

### 2.4 CORSの設定

`cors.json`ファイルを作成します：

```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "HEAD", "PUT", "POST", "DELETE"],
      "MaxAgeSeconds": 3000
    }
  ]
}
```

S3バケットにCORS設定を適用します：

```bash
aws s3api put-bucket-cors --bucket food-optimizer-frontend --cors-configuration file://cors.json
```

## 3. アプリケーションへのアクセス

S3バケットのウェブサイトURLにアクセスします：

```
http://food-optimizer-frontend.s3-website-ap-northeast-1.amazonaws.com
```

## 4. トラブルシューティング

### 4.1 CORS関連のエラー

フロントエンドからバックエンドへのリクエストでCORSエラーが発生する場合は、以下を確認してください：

1. Lambda関数のCORS設定が正しいこと
2. S3バケットのCORS設定が正しいこと
3. APIエンドポイントのURLが正しいこと

### 4.2 Lambda関数のエラー

Lambda関数でエラーが発生する場合は、CloudWatchログを確認してください：

```bash
aws logs filter-log-events --log-group-name /aws/lambda/food-optimizer-dev-analyze
```

### 4.3 OpenAI APIキーの問題

OpenAI APIキーに関する問題が発生した場合は、以下を確認してください：

1. 環境変数`OPENAI_API_KEY`が正しく設定されていること
2. APIキーが有効であること
3. APIキーの使用制限に達していないこと

## 5. セキュリティ上の注意点

1. OpenAI APIキーを直接コードに埋め込まないでください
2. 本番環境では、AWS Secrets Managerを使用してAPIキーを管理することを検討してください
3. S3バケットのアクセス権限を適切に設定してください
4. API Gatewayに認証を追加することを検討してください

## 6. 運用コストの最適化

1. Lambda関数のメモリサイズとタイムアウト設定を調整してください
2. CloudFrontを使用してS3コンテンツをキャッシュすることを検討してください
3. 使用頻度が低い場合は、Lambda関数のプロビジョニングされた同時実行数を減らしてください
