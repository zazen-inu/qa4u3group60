# 食品原材料最適化アプリケーション

量子アニーリングアルゴリズムとOpenAI APIを組み合わせた食品原材料最適化アプリケーションです。このアプリケーションは、AWS LambdaとS3を使用したサーバーレスアーキテクチャで構築されています。

## 機能

- OpenAI APIを使用して食品の原材料情報を分析
- 量子アニーリングアルゴリズムを使用して最適な配合比率を計算
- 目標栄養成分値（カロリー、タンパク質、脂質、炭水化物、塩分）に近づける最適化
- 結果をグラフと表で視覚的に表示

## プロジェクト構造

```
food-optimizer/
├── backend/
│   ├── app.py              # Flaskアプリケーション
│   ├── openai_analyzer.py  # OpenAI API関連の機能
│   ├── quantum_optimizer.py # 量子アニーリング関連の機能
│   ├── lambda_handler.py   # AWS Lambda用ハンドラー
│   ├── serverless.yml      # AWS Lambdaの設定
│   └── requirements.txt    # 依存関係
├── frontend/
│   ├── index.html          # メインページ
│   ├── styles.css          # スタイルシート
│   └── script.js           # フロントエンド機能
└── README.md               # プロジェクト説明
```

## 必要な環境

- Python 3.9以上
- Node.js 14以上（Serverlessフレームワーク用）
- AWS CLI（設定済み）
- OpenAI APIキー

## ローカルでの実行方法

### バックエンド

```bash
cd backend
pip install -r requirements.txt
export OPENAI_API_KEY="your-openai-api-key"
flask run --port=5000
```

### フロントエンド

```bash
cd frontend
python -m http.server 8000
```

ブラウザで `http://localhost:8000` にアクセスしてアプリケーションを使用できます。

## AWSへのデプロイ方法

### バックエンド（AWS Lambda）

1. 必要なパッケージをインストールします：

```bash
cd backend
pip install -r requirements.txt -t .
npm install -g serverless
```

2. OpenAI APIキーを環境変数として設定します：

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

3. Serverlessフレームワークを使用してデプロイします：

```bash
serverless deploy
```

4. デプロイが完了すると、以下のような出力が表示されます：

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
functions:
  analyze: food-optimizer-dev-analyze
layers:
  None
```

5. 表示されたエンドポイントURLをメモします。これをフロントエンドの設定で使用します。

### フロントエンド（S3）

1. S3バケットを作成し、静的ウェブサイトホスティングを有効にします：

```bash
aws s3 mb s3://food-optimizer-frontend
aws s3 website s3://food-optimizer-frontend --index-document index.html
```

2. フロントエンドのコードを編集して、Lambda関数のエンドポイントを設定します：

```bash
cd frontend
```

`script.js`ファイルを開き、`API_ENDPOINT`変数を更新します：

```javascript
// ローカル開発用のエンドポイント（コメントアウト）
// const API_ENDPOINT = 'http://localhost:5000/analyze';

// AWS Lambda用のエンドポイント
const API_ENDPOINT = 'https://xxxxxxxxxx.execute-api.ap-northeast-1.amazonaws.com/dev/analyze';
```

3. フロントエンドファイルをS3バケットにアップロードします：

```bash
aws s3 sync . s3://food-optimizer-frontend --acl public-read
```

4. S3バケットのウェブサイトURLを取得します：

```bash
aws s3 website s3://food-optimizer-frontend --region ap-northeast-1
```

出力されたURLにアクセスしてアプリケーションを使用できます。通常、URLは以下の形式になります：
`http://food-optimizer-frontend.s3-website-ap-northeast-1.amazonaws.com`

### CORS設定

Lambda関数にCORSを設定するには、`serverless.yml`ファイルに以下の設定が含まれていることを確認してください：

```yaml
functions:
  analyze:
    handler: lambda_handler.handler
    events:
      - http:
          path: analyze
          method: post
          cors: true
```

## 使用方法

1. 原材料リストをテキストボックスに入力します（例：「きなこ（大豆を含む）（国内製造）、水飴、砂糖」）
2. 目標栄養成分値を設定します（デフォルト値はきなこ飴の一般的な栄養成分値）
3. 「分析・最適化」ボタンをクリックします
4. 結果が表示されます：
   - 原材料の栄養成分情報
   - 最適な配合比率
   - 計算された栄養成分値
   - グラフによる視覚化

## 技術スタック

- バックエンド：Python、Flask、OpenAI API、dimod、neal（シミュレーテッドアニーリング）
- フロントエンド：HTML、CSS、JavaScript、Chart.js
- インフラ：AWS Lambda、S3、API Gateway

## 注意事項

- OpenAI APIキーは環境変数として設定する必要があります
- AWS認証情報が適切に設定されている必要があります
- 初期デプロイ後、フロントエンドのAPI_ENDPOINTを更新する必要があります
