# GitOps tools, workflow and consideration


End goal of GitOps with this project:   
    1. Enable a CI/CD pipeline to build/test/publish/deploy code into a server  
    2. Provide access to secrets needed for deployment  
    3. Enable vulnerability, integration and unit testing via CI/CD pipelines  

Workflow: 

```
+------------+     +------------+      +------------+     +------------+     +------------+
|   Commit   |     |            |      |            |     |            |     |            |
|   and tag  +-----+   Trigger  +----->+   build/   +---->+ push image +-----+  deploy to |
|    code    |     |    CI/CD   |      |    test    |     |    to      |     |   server   |
|            |     |            |      |    code    |     | dockerHub  |     |            |
+------------+     +------------+      +------------+     +------------+     +------------+
```

```
Consideration for tools used:   
    1. Should be open sourced/open source compliant   
    2. Free or minimal cost  
    3. Pari should like it  
    4. Preferably doesn't cause a nuclear war  
    
Tools:   
    1. CI/CD - Github actions  
    2. Docker image hosting - DockerHub  
    3. Docker Orchestration tool - Rancher(With or without Kubernetes) or Nomad  
    4. System statistics - Telegraf, InfluxDB and Grafana (TIG stack)  
    5. Error tracking - Sentry   
    6. Logging - NXLog configured for docker OR ELK stack (Not sure if we need something that powerful) OR Papertrail  
    7. Alerting - Sentry + Grafana alerts  
    8. Load balancing - Nginx  
    9. Security - Hashicorp Vault? Do we even need this?   
    10. ChatOps - Kill it with fire. Don't even dream of it.   
    11. Did i miss something?  
```
    