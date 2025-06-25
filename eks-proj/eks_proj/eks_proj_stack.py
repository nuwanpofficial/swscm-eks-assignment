import datetime
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_eks as eks,
    aws_lambda as _lambda,
    CustomResource,
    custom_resources as cr,
    CfnOutput,
)
from constructs import Construct
from aws_cdk.lambda_layer_kubectl_v32 import KubectlV32Layer

class EksProjStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account_env = 'development'

        vpc = ec2.Vpc(self, "eks-vpc",
                      max_azs=2,
                      cidr="172.18.0.0/16",
                      )
        
        eks_cluster = eks.Cluster(self, "eks-helm-cluster",
                                  version=eks.KubernetesVersion.V1_32,
                                  cluster_name="eks-helm-cluster",
                                  default_capacity=2,
                                  vpc=vpc,
                                  default_capacity_instance=ec2.InstanceType("t3a.medium"),
                                  kubectl_layer=KubectlV32Layer(self, "kubectl"),
                                  )
        
        ssm_env_para = ssm.StringParameter(self, 'eks-helm',
                                           parameter_name='/platform/account/env',
                                           string_value=account_env
                                           )
        
        helm_lambda = _lambda.Function(self, 'eks-helm-lambda',
                                       runtime=_lambda.Runtime.PYTHON_3_13,
                                       handler="helmval.handler",
                                       code=_lambda.Code.from_asset("lambda/helm_values")
        )

        ssm_env_para.grant_read(helm_lambda)

        
        helm_cr = CustomResource(self, 'helm-values-cr',
                                 service_token=helm_lambda.function_arn,
                                 properties={
                                     "env": account_env,
                                    #  "date": datetime.datetime.now(datetime.timezone.utc)
                                 })
        
        helm_cr.node.add_dependency(ssm_env_para)  

        replica_count = helm_cr.get_att('replicaCount').to_string()
        
        nginx_ingress_chart = eks.HelmChart(self, 'nginx-ingess-chart',
                                            cluster=eks_cluster,
                                            chart='ingress-nginx',
                                            repository='https://kubernetes.github.io/ingress-nginx',
                                            namespace='ingress-nginx',
                                            version='4.12.3',
                                            release='ingress-nginx',
                                            values={
                                                'controller': {
                                                    'replicaCount': replica_count
                                                }
                                            }
                                            )
        
        nginx_ingress_chart.node.add_dependency(helm_lambda)
        
        ## Add Permissions to a User to view/access the Cluster 
        # existing_user = iam.User.from_user_name(self, "ExistingUser", "USERNAME")

        # eks_cluster.aws_auth.add_user_mapping(
        #                     user=existing_user,
        #                     groups=["system:masters"]
        #                 )
        
        ## Add Permissions to a Role to view/access the Cluster
        # existing_role = iam.Role.from_role_name(self, "ExistingRole", "ROLENAME")

        # eks_cluster.aws_auth.add_role_mapping(
        #                     role=existing_role,
        #                     groups=["system:masters"]
        #                 )

        CfnOutput(self, "ReplicaCount",
                  value=replica_count,
                  description="Replica Count"
                )
        
        

