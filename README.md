## Chat Commerce

対話式 EC Commerce

## Getting Started

### CDK 周りの初期設定

```
$ pnpm install
```

### AWS アカウントで cdk bootstrap を未実行の場合、ブートストラップを設定（AWS アカウントで新規に AWS CDK を動かす場合のみ実施）

```
$ pnpm cdk bootstrap --profile {.aws/configに設定したprofile名} -c environment=dev
```

## デプロイまでの流れ

### テンプレート生成

CloudFormation テンプレートを生成して、CDK->CloudFormation の変換がうまくいくかを確認します。

```
pnpm cdk synth -c environment=dev
```

### 変更差分確認

デプロイ内容と実環境との差分を確認したい場合は、cdk diff コマンドを利用する

```
pnpm cdk diff -c environment=dev
```

#### AWS 環境へデプロイ

#### デプロイ用のロールと ECR のデプロイ

```bash
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query "Account" --output text)
export CDK_DEFAULT_REGION="ap-northeast-1"

# GHAデプロイ用のロールのデプロイ
pnpm cdk deploy -c environment=dev dev-chat-commerce-deploy-role-stack

# ECSを含むスタックは、ECRにコンテナイメージがプッシュ済みである必要があるため先に作成
pnpm cdk deploy -c environment=dev dev-chat-commerce-ecr-stack

# 出力結果はこの後の手順で利用するため、セッションをクリアしないこと
```

#### コンテナイメージの用意

```bash
# プロジェクトルートで実行
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
export REPOSITORY_NAME=chat-commerce-app
export REGISTRY_NAME=$AWS_ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com
export COMMIT_HASH=$(git rev-parse --short HEAD)
docker buildx build \
  --platform=linux/x86_64 \
  -t $COMMIT_HASH \
  -f Dockerfile.server .
docker tag $COMMIT_HASH \
  $REGISTRY_NAME/$REPOSITORY_NAME:$COMMIT_HASH

# assume-roleが必要
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $REGISTRY_NAME
docker push "$AWS_ACCOUNT_ID.dkr.ecr.ap-northeast-1.amazonaws.com/$REPOSITORY_NAME:$COMMIT_HASH"
```

#### ECS 関連リソースのデプロイ

```bash
pnpm cdk deploy \
  -c environment=dev \
  -c imageTag=$COMMIT_HASH \
  dev-chat-commerce-infra-stack
```

## Useful commands

- `npm run build` compile typescript to js
- `npm run watch` watch for changes and compile
- `npm run test` perform the jest unit tests
- `npx cdk deploy` deploy this stack to your default AWS account/region
- `npx cdk diff` compare deployed stack with current state
- `npx cdk synth` emits the synthesized CloudFormation template
