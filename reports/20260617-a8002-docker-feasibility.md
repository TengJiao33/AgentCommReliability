# A800_2 Docker 可行性检查

## 核心判断

A800_2 可以下载 Docker 相关文件，但当前用户无法安装或启动官方 Docker Engine。原因是标准 Docker daemon 需要 root 权限，当前用户没有免密 sudo，也不在已有 Docker daemon 环境里。

Rootless Docker 有一点希望，但当前也跑不起来。机器已经打开 unprivileged user namespaces，并且 `/etc/subuid`、`/etc/subgid` 里给 `xuhaoming` 配了 65536 subordinate IDs；但 `newuidmap`、`newgidmap`、`rootlesskit`、`slirp4netns`、`fuse-overlayfs` 都缺失。其中 `newuidmap/newgidmap` 是 Docker rootless 官方前置条件，通常需要管理员通过 `uidmap` 包安装。

## 只读检查结果

检查时间：2026-06-17

远端：`A800_2`

当前用户：

```text
USER=xuhaoming
KERNEL=5.15.0-113-generic
SUDO_N=false
USERNS=1
MAX_USERNS=4125219
SUBUID=xuhaoming:493216:65536
SUBGID=xuhaoming:493216:65536
CGROUP=cgroup2fs
uid=1006(xuhaoming) gid=1006(xuhaoming) groups=1006(xuhaoming)
```

缺失工具：

```text
NO_docker
NO_dockerd
NO_podman
NO_singularity
NO_apptainer
NO_nerdctl
NO_buildah
NO_newuidmap
NO_newgidmap
NO_slirp4netns
NO_fuse-overlayfs
NO_rootlesskit
```

## 为什么下载不等于可运行

Docker client 只是命令行前端。真正隔离容器、挂载文件系统、管理网络和 cgroup 的是 daemon/runtime。标准 Docker Engine 的 daemon 由 root 运行；普通用户下载一个 `docker` 二进制，仍然没有可连接的 daemon，也无法创建系统 socket、iptables/network namespace、overlay storage 和 cgroup delegation。

Docker rootless 可以把 daemon 和 container 都放进用户命名空间，但它要求 host 上存在 `newuidmap/newgidmap`，并需要 subordinate UID/GID 映射。A800_2 的映射已经有了，工具缺失。用户自己下载 `newuidmap/newgidmap` 通常不够，因为它们需要系统安装时的权限位来安全写 uid/gid map。

## 对 TeamBench 的影响

TeamBench 的核心可信点是 OS-enforced role separation：不同 role 在不同 container 里，通过 bind mounts 和权限边界隔离 spec、workspace、grader。当前 A800_2 不能给出这个条件下的官方结果。

能做的事情：

- 读 TeamBench 代码和任务。
- 跑 mock / parser / grader sanity。
- 在非官方 shim 里模拟角色边界。

不能声称的事情：

- 官方 Docker 隔离下的 TeamBench pass rate。
- OS-enforced role separation 已经复现。

## 可行路径

1. 管理员安装 Docker Engine，并把当前用户加入 `docker` group。最快拿到 TeamBench 官方条件，但 docker group 近似 root 权限，很多共享服务器不会批准。
2. 管理员只安装 rootless 前置工具：`uidmap`、`rootlesskit`、`slirp4netns`、`fuse-overlayfs`。之后我们在 home 目录安装 rootless Docker，风险较小。
3. 管理员安装 Apptainer/Singularity。HPC 上更常见，但 TeamBench 需要改运行脚本，官方可比性会下降。
4. 换一台有 Docker 的机器或临时云主机跑 TeamBench small subset。
5. 继续用 HiddenBench / PACT 做短期主实验，TeamBench 等基础设施到位后再上。

## 官方依据

- Docker Linux post-install 文档说明标准 Docker daemon 以 root user 运行。
- Docker Rootless 文档说明 rootless mode 需要 host 上安装 `newuidmap` 和 `newgidmap`，并需要 `/etc/subuid`、`/etc/subgid` 里有至少 65536 subordinate IDs。
