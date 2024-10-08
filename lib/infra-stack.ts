import * as cdk from 'aws-cdk-lib'
import type { Construct } from 'constructs'
import { VpcConstruct } from './construct/vpc-construct'
import { SecurityGroupConstruct } from './construct/common-sg-construct'
import { WafConstruct } from './construct/waf-construct'
import { DynamodbConstruct } from './construct/dynamo-db-construct'
import { EcsConstruct } from './construct/ecs-construct'

export interface InfraStackProps extends cdk.StackProps {
  vpcCidr: string
  // vpcIdSsmParamName: string
  repositoryName: string
  imageTag: string
  webAclScope: 'REGIONAL' | 'CLOUDFRONT'
  taskCpu: number
  taskMemory: number
  containerCpu: number
  containerMemory: number
  certificateArn: string
  envName: 'dev' | 'stg' | 'prd'
  projectName: string
  // domainPrefix: string
  // callbackUrls: string[]
  // logoutUrls: string[]
}

export class InfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: InfraStackProps) {
    super(scope, id, props)

    const vpc = new VpcConstruct(this, `${id}-vpc`, {
      vpcCidr: props.vpcCidr,
      // vpcIdSsmParamName: props.vpcIdSsmParamName,
      envName: props.envName,
      projectName: props.projectName,
    })

    const sg = new SecurityGroupConstruct(this, `${id}-sg`, {
      myVpc: vpc.myVpc,
      envName: props.envName,
      projectName: props.projectName,
    })

    const waf = new WafConstruct(this, `${id}-waf`, {
      webAclScope: props.webAclScope,
      envName: props.envName,
      projectName: props.projectName,
    })

    const db = new DynamodbConstruct(this, `${id}-dynamodb`, {
      projectName: props.projectName,
      envName: props.envName,
    })

    const ecs = new EcsConstruct(this, `${id}-ecs`, {
      myVpc: vpc.myVpc,
      webAcl: waf.webAcl,
      taskCpu: props.taskCpu,
      taskMemory: props.taskMemory,
      containerCpu: props.containerCpu,
      containerMemory: props.containerMemory,
      repositoryName: props.repositoryName,
      ecsSecurityGroup: sg.securityGroupForFargate,
      albSecurityGroup: sg.securityGroupForAlb,
      imageTag: props.imageTag,
      table: db.chatCommerceTable, // dynamodb
      // dbRootSecret: aurora.dbRootSecret,
      // TODO: HTTPS対応
      certificateArn: 'TBD',
      // userPool: cognito.userPool,
      // userPoolClient: cognito.userPoolClient,
      envName: props.envName,
      projectName: props.projectName,
    })

    new cdk.CfnOutput(this, 'LOAD_BALANCER_DNS_NAME', {
      value: ecs.loadBalancerDnsName,
    })
  }
}
