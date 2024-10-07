import type * as cdk from 'aws-cdk-lib'

export interface InfraStackProps extends cdk.StackProps {
  vpcCidr: string
  vpcIdSsmParamName: string
  repositoryName: string
  imageTag: string
  webAclScope: 'REGIONAL' | 'CLOUDFRONT'
  taskCpu: number
  taskMemory: number
  containerCpu: number
  containerMemory: number
  certificateArn: string
  envName: string
  projectName: string
  domainPrefix: string
  callbackUrls: string[]
  logoutUrls: string[]
}
