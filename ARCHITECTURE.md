# AWS Deployment Architecture

This document defines a highly available AWS deployment for the API birthday service.
The service uses the current container image and the Lambda Web Adapter.
The design focuses on high availability in one AWS Region.

## Recommended deployment

```mermaid
flowchart TB
    User[Users and API clients]
    DNS[Route 53\nhealth checks]
    CF[CloudFront\nTLS with ACM]
    WAF[AWS WAF\nmanaged rules and rate limits]
    URL[Lambda Function URL\nHTTPS origin]

    User --> DNS --> CF --> WAF --> URL

    subgraph Region[Primary AWS Region]
        direction TB

        subgraph VPC[VPC]
            direction TB

            subgraph PrivateApp[Private application subnets - 3 AZs]
                direction LR
                Lambda[AWS Lambda\ncontainer image and Lambda Web Adapter\nreserved and provisioned concurrency]
                Proxy[RDS Proxy\nconnection pooling and failover support]
                Lambda --> Proxy
            end

            subgraph PrivateData[Private data subnets - 3 AZs]
                direction LR
                DB[(RDS MySQL\nMulti-AZ primary)]
                Standby[(Multi-AZ standby\nautomatic failover)]
                ReadReplica[(RDS MySQL read replica\nread-only traffic)]
                DB -. synchronous standby .-> Standby
                DB -. read scaling .-> ReadReplica
            end

            Proxy --> DB
            Proxy --> ReadReplica

            VPCE[VPC endpoints\nECR, CloudWatch, Secrets Manager and S3]
            NAT[NAT gateways\none per AZ, when required]
            Lambda -. AWS service access .-> VPCE
            PrivateApp -. required egress .-> NAT
        end

        URL --> Lambda

        ECR[Amazon ECR\nimage scan and immutable tags]
        Secrets[Secrets Manager and KMS\ndatabase credentials and secrets]
        Logs[CloudWatch Logs and Metrics\nalarms and dashboards]
        Traces[X-Ray or OpenTelemetry]
        Backup[AWS Backup and RDS point-in-time recovery\nlocked backup vault]

        ECR -. pulls image .-> Lambda
        Secrets -. provides secrets .-> Lambda
        Lambda -. sends logs .-> Logs
        Lambda -. sends traces .-> Traces
        DB -. backup and recovery .-> Backup
        ReadReplica -. backup and recovery .-> Backup
    end
```

## Request flow

1. Route 53 sends clients to CloudFront.
2. CloudFront terminates Transport Layer Security.
3. CloudFront sends API traffic to the Web Application Firewall.
4. The Web Application Firewall blocks common attacks and applies rate limits based on client IP address.
5. CloudFront sends allowed requests to the Lambda Function URL.
6. Lambda runs the container image with the Lambda Web Adapter.
7. RDS Proxy manages database connections and database failover.
8. Write operations use the RDS MySQL primary.
9. Read operations can use the RDS MySQL read replica.
