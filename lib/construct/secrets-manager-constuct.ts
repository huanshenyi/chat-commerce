import { aws_secretsmanager as secretsmanager } from 'aws-cdk-lib';
import type * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface SecretsManagerConstructProps extends cdk.StackProps {
  envName: string;
  projectName: string;
}

export class SecretsManagerConstruct extends Construct {
  public readonly chatCommerceSecret: secretsmanager.Secret;

  constructor(scope: Construct, id: string, props: SecretsManagerConstructProps) {
    super(scope, id);

    const { projectName, envName } = props;

    const chatCommerceSecret = new secretsmanager.Secret(this, `${id}-AppSecret`, {
      secretName: `${envName}/${projectName}/secret`,
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ WEATHER_API_KEY: '' }),
        generateStringKey: 'WEATHER_API_KEY',
      },
    });
    this.chatCommerceSecret = chatCommerceSecret;
  }
}
