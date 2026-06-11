# k8s troubleshooting

# k8s troubleshooting

kubectl get
↓
kubectl describe
↓
kubectl logs
↓
kubectl get events
↓
kubectl exec
↓
netshoot

‍

明白，你想要整理一份 ​**Kubernetes 常用排障命令 + 参数表**​，便于快速定位问题。我给你做一份比较完整的“​**实战运维排障清单**”。

---

# 1️⃣ 查看资源状态

|命令|常用参数|用途|
| ----| ---------------------------------------------| --------------------------|
|​`kubectl get pods`|​`-A`​显示所有 namespace`-o wide`显示 Node、IP、容器信息|查看 Pod 状态|
|​`kubectl get svc`|​`-A`显示所有 namespace|查看 Service 状态|
|​`kubectl get endpoints`|-|查看 Service 对应的 Pod IP|
|​`kubectl get nodes`|​`-o wide`|查看 Node 状态、IP、版本|
|​`kubectl get deployments`|​`-A`|查看 Deployment 状态|
|​`kubectl get replicasets`|​`-A`|查看副本集状态|

---

# 2️⃣ 查看详细信息 / 描述

|命令|参数|用途|
| ----| ----| ------------------------------|
|​`kubectl describe pod POD_NAME`|-|查看 Pod 详细信息，包括 Events|
|​`kubectl describe svc SERVICE_NAME`|-|查看 Service 详细信息|
|​`kubectl describe node NODE_NAME`|-|查看 Node 资源使用、事件|
|​`kubectl describe deployment DEPLOY_NAME`|-|查看 Deployment 状态及副本信息|

​**技巧**​：`kubectl describe pod POD_NAME -n NAMESPACE` 指定命名空间。

---

# 3️⃣ 查看日志

|命令|参数|用途|
| ----| ----------------------------------| ---------------------------|
|​`kubectl logs POD_NAME`|​`-f`​跟随日志输出`--previous`查看上一个容器日志|Pod 日志排障|
|​`kubectl logs POD_NAME -c CONTAINER_NAME`|-|多容器 Pod 指定容器|
|​`kubectl logs -l LABEL_SELECTOR`|-|通过 label 获取日志（批量）|

---

# 4️⃣ 查看事件 / 资源变动

|命令|参数|用途|
| ----| ----| ------------------------------|
|​`kubectl get events`|​`--sort-by=.metadata.creationTimestamp`|按时间顺序查看事件|
|​`kubectl get events -A`|-|查看全部命名空间事件|
|​`kubectl describe pod POD_NAME`|-|事件也会包含在 describe 输出中|

---

# 5️⃣ 进入 Pod / 执行命令

|命令|参数|用途|
| ----| ----| -------------------|
|​`kubectl exec -it POD_NAME -- sh`|-|进入 Pod shell|
|​`kubectl exec POD_NAME -- COMMAND`|-|直接在 Pod 执行命令|
|​`kubectl exec -it POD_NAME -c CONTAINER_NAME -- sh`|-|多容器 Pod 指定容器|

​**常用容器内命令**：

```bash
env
cat /etc/resolv.conf
ls /usr/share/nginx/html
ps aux
df -h
```

---

# 6️⃣ 排查网络 / DNS / Service

|命令|参数|用途|
| ----| ----| --------------------------|
|​`kubectl get svc`|-|查看 Service IP / NodePort|
|​`kubectl get endpoints`|-|查看 Service 对应 Pod IP|
|​`kubectl exec POD -- nslookup SERVICE_NAME`|-|DNS 解析|
|​`kubectl exec POD -- ping POD_IP`|-|网络连通性|
|​`kubectl exec POD -- curl http://SERVICE_IP`|-|测试访问|

---

# 7️⃣ 扩缩容 / 状态调整

|命令|参数|用途|
| ----| ----| ------------------------|
|​`kubectl scale deployment DEPLOY_NAME --replicas=N`|-|调整副本数|
|​`kubectl rollout status deployment DEPLOY_NAME`|-|查看 Deployment 滚动状态|
|​`kubectl rollout restart deployment DEPLOY_NAME`|-|重启 Deployment|

---

# 8️⃣ 调试工具 Pod

```bash
kubectl run netshoot \
--image=nicolaka/netshoot \
-it --rm -- sh
```

工具集成：

- ​`ip addr`
- ​`ss -tulpn`
- ​`ping`
- ​`curl`
- ​`dig / nslookup`
- ​`traceroute / tcpdump`

> 专业排障通常不在业务 Pod 安装工具，而是启动一个调试 Pod。调试专用 Pod（netshoot）测试业务 Pod，本质上是 Pod 作为客户端去访问另一个 Pod 或 Service，而不是进入或控制另一个 Pod。

---

# 9️⃣ 过滤 / 查询技巧

|命令|作用|
| ----| -------------------------------|
|​`-n NAMESPACE`|指定命名空间|
|​`-l LABEL_SELECTOR`|按 label 过滤|
|​`-o wide`|显示更多信息|
|​`-o yaml / json`|输出 YAML / JSON 格式，方便分析|
|​`--field-selector status.phase=Running`|按状态筛选 Pod|

---

# 🔹 总结排障流程对应命令

1. **确认 Pod 是否正常**

```bash
kubectl get pods -o wide
kubectl describe pod POD_NAME
```

2. **查看日志**

```bash
kubectl logs POD_NAME [-c CONTAINER_NAME] [-f]
```

3. **查看事件**

```bash
kubectl get events --sort-by=.metadata.creationTimestamp
```

4. **进入 Pod 检查内部状态**

```bash
kubectl exec -it POD_NAME -- sh
```

5. **网络 / DNS / 服务检查**

```bash
kubectl get svc / endpoints
kubectl exec POD -- nslookup SERVICE_NAME
kubectl exec POD -- curl http://SERVICE_IP
```

6. **高级调试**

```bash
kubectl run netshoot --image=nicolaka/netshoot -it --rm -- sh
```
