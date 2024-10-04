#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { EcrStack } from '../lib/ecr-stack';
import { DeployRoleStack } from '../lib/deploy-role-stack';
import { getAppParameters } from './parameter';

const app = new cdk.App();

const argContext = 'environment';
const envKey = app.node.tryGetContext(argContext);
const appParameter = getAppParameters(envKey);

/**
 * Build Container Image
 * デプロイパイプラインからタグの指定がある場合は、優先して使用する
 */
const imageTag = app.node.tryGetContext('imageTag')
  ? app.node.tryGetContext('imageTag')
  : appParameter.imageTag;

  new DeployRoleStack(
    app,
    `${appParameter.envName}-${appParameter.projectName}-deploy-role-stack`,
    {
      projectName: appParameter.projectName,
      gitHubOwner: appParameter.github.owner,
      gitHubRepo: appParameter.github.repo,
    }
  );

  new EcrStack(
    app,
    `${appParameter.envName}-${appParameter.projectName}-ecr-stack`,
    {
      repositoryName: appParameter.repositoryName,
      envName: appParameter.envName,
      projectName: appParameter.projectName,
    }
  );