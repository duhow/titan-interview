# Titan User Helm Chart

Deploy the Titan User API with Helm.

This chart supports a local MariaDB dependency, a remote MySQL or MariaDB server, KEDA, Argo Rollouts, and Istio.

## Requirements

Install these tools before you use this chart:

- Helm 3.
- Access to `registry-1.docker.io` to download the MariaDB dependency.
- A Kubernetes cluster with a default StorageClass when `mysql.enabled` is true.
- An existing Secret named by `externalDatabase.secretName`.
- The Secret must contain `externalDatabase.passwordKey` when `externalDatabase.databaseUrlKey` is empty.
- The Secret must contain `externalDatabase.databaseUrlKey` when that key is set.
- A KEDA installation when `autoscaling.keda.enabled` is true.
- An Argo Rollouts installation when `rollout.enabled` is true.
- Istio CRDs and an Istio installation when `istio.enabled` is true.

## Install the chart

Build the chart dependency first:

```sh
helm dependency build chart/titan-user
```

Create the database Secret. Use a password that matches the local MariaDB Secret when you enable `mysql`:

```sh
kubectl create secret generic titan-user-database \
  --from-literal=mariadb-password='change-me' \
  --from-literal=mariadb-replication-password='change-replication-me' \
  --from-literal=mariadb-root-password='change-root-me'
```

Install the chart with the local database:

```sh
helm upgrade --install titan-user chart/titan-user \
  --set mysql.enabled=true
```

The chart creates a 1GiB MariaDB volume by default. The API runs the Alembic migration before it starts.

## Use a remote database

Keep `mysql.enabled` false. Set the remote host and enable the external database:

```yaml
externalDatabase:
  enabled: true
  host: mysql.example.internal
  port: 3306
  name: titan
  username: titan
  secretName: titan-user-database
  passwordKey: password
```

Create the Secret and install the chart with these values:

```sh
kubectl create secret generic titan-user-database \
  --from-literal=password='replace-with-the-remote-password'

helm upgrade --install titan-user chart/titan-user \
  --set externalDatabase.enabled=true \
  --set externalDatabase.host=mysql.example.internal \
  --set externalDatabase.secretName=titan-user-database \
  --set externalDatabase.passwordKey=password
```

If the Secret contains a complete URL, use `databaseUrlKey` instead:

```yaml
externalDatabase:
  enabled: true
  secretName: titan-user-database
  databaseUrlKey: DATABASE_URL
```

Use this URL format:

```text
mysql+pymysql://<username>:<password>@<host>:<port>/<database>
```

For example:

```sh
kubectl create secret generic titan-user-database \
  --from-literal=DATABASE_URL='mysql+pymysql://titan:replace-me@mysql.example.internal:3306/titan'
```

When `databaseUrlKey` is set, `passwordKey` is not required.

## Use KEDA

Set `autoscaling.enabled` and `autoscaling.keda.enabled` to true. Add at least one trigger:

```yaml
autoscaling:
  enabled: true
  keda:
    enabled: true
    triggers:
      - type: cpu
        metadata:
          type: Utilization
          value: "80"
```

## Use Argo Rollouts

Set `kind` to `Deployment` and enable the rollout:

```yaml
kind: Deployment
rollout:
  enabled: true
```

Do not enable Rollouts with `kind: StatefulSet`.

## Use Istio

Enable Istio resources and provide the gateway and host:

```yaml
istio:
  enabled: true
  gateways:
    - mesh
  hosts:
    - api.example.com
```

## Default values

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| affinity | object | `{}` |  |
| autoscaling.enabled | bool | `false` |  |
| autoscaling.keda.advanced | object | `{}` |  |
| autoscaling.keda.cooldownPeriod | string | `nil` |  |
| autoscaling.keda.enabled | bool | `false` |  |
| autoscaling.keda.fallback | object | `{}` |  |
| autoscaling.keda.idleReplicaCount | string | `nil` |  |
| autoscaling.keda.initialCooldownPeriod | string | `nil` |  |
| autoscaling.keda.maxReplicaCount | string | `nil` |  |
| autoscaling.keda.minReplicaCount | string | `nil` |  |
| autoscaling.keda.pollingInterval | string | `nil` |  |
| autoscaling.keda.triggers | list | `[]` |  |
| autoscaling.maxReplicas | int | `100` |  |
| autoscaling.minReplicas | int | `1` |  |
| autoscaling.targetCPUUtilizationPercentage | int | `80` |  |
| externalDatabase.databaseUrlKey | string | `""` |  |
| externalDatabase.enabled | bool | `false` |  |
| externalDatabase.host | string | `""` |  |
| externalDatabase.name | string | `"titan"` |  |
| externalDatabase.passwordKey | string | `"mariadb-password"` |  |
| externalDatabase.port | int | `3306` |  |
| externalDatabase.secretName | string | `"titan-user-database"` |  |
| externalDatabase.username | string | `"titan"` |  |
| fullnameOverride | string | `""` |  |
| httpRoute | object | `{"annotations":{},"enabled":false,"hostnames":["chart-example.local"],"parentRefs":[{"name":"gateway","sectionName":"http"}],"rules":[{"matches":[{"path":{"type":"PathPrefix","value":"/headers"}}]}]}` | Expose the service via gateway-api HTTPRoute Requires Gateway API resources and suitable controller installed within the cluster (see: https://gateway-api.sigs.k8s.io/guides/) |
| image.pullPolicy | string | `"Always"` |  |
| image.repository | string | `"ghcr.io/duhow/titan-interview"` |  |
| image.tag | string | `"latest"` |  |
| imagePullSecrets | list | `[]` |  |
| ingress.annotations | object | `{}` |  |
| ingress.className | string | `""` |  |
| ingress.enabled | bool | `false` |  |
| ingress.hosts[0].host | string | `"chart-example.local"` |  |
| ingress.hosts[0].paths[0].path | string | `"/"` |  |
| ingress.hosts[0].paths[0].pathType | string | `"ImplementationSpecific"` |  |
| ingress.tls | list | `[]` |  |
| istio.enabled | bool | `false` |  |
| istio.gateways[0] | string | `"mesh"` |  |
| istio.hosts[0] | string | `"*"` |  |
| kind | string | `"Deployment"` |  |
| livenessProbe.enabled | bool | `false` |  |
| livenessProbe.httpGet.path | string | `"/healthz/startup"` |  |
| livenessProbe.httpGet.port | string | `"http"` |  |
| mysql.auth.database | string | `"titan"` |  |
| mysql.auth.existingSecret | string | `"titan-user-database"` |  |
| mysql.auth.username | string | `"titan"` |  |
| mysql.enabled | bool | `false` |  |
| mysql.primary.persistence.enabled | bool | `true` |  |
| mysql.primary.persistence.size | string | `"1Gi"` |  |
| nameOverride | string | `""` |  |
| nodeSelector | object | `{}` |  |
| podAnnotations | object | `{}` |  |
| podLabels | object | `{}` |  |
| podManagementPolicy | string | `"OrderedReady"` |  |
| podSecurityContext | object | `{}` |  |
| readinessProbe.enabled | bool | `false` |  |
| readinessProbe.httpGet.path | string | `"/healthz/startup"` |  |
| readinessProbe.httpGet.port | string | `"http"` |  |
| replicaCount | int | `1` |  |
| resources | object | `{}` |  |
| rollout.canary.steps | list | `[]` |  |
| rollout.enabled | bool | `false` |  |
| securityContext.readOnlyRootFilesystem | bool | `true` |  |
| securityContext.runAsNonRoot | bool | `true` |  |
| securityContext.runAsUser | int | `1001` |  |
| service.containerPort | int | `8000` |  |
| service.headless | bool | `false` |  |
| service.port | int | `80` |  |
| service.type | string | `"ClusterIP"` |  |
| serviceAccount.annotations | object | `{}` |  |
| serviceAccount.automount | bool | `true` |  |
| serviceAccount.create | bool | `true` |  |
| serviceAccount.name | string | `""` |  |
| serviceName | string | `""` |  |
| startupProbe.enabled | bool | `true` |  |
| startupProbe.httpGet.path | string | `"/healthz/startup"` |  |
| startupProbe.httpGet.port | string | `"http"` |  |
| tolerations | list | `[]` |  |
| updateStrategy | object | `{}` |  |
| volumeClaimTemplates | list | `[]` |  |
| volumeMounts | list | `[]` |  |
| volumes | list | `[]` |  |
