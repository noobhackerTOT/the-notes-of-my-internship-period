# ads

串联模式

所有进出流量都必须经过该设备。设备对经过的每个数据包进行实时分析，并可根据策略允许、阻断、修改或记录流量

同时必须支持bypass和转发 避免设备本身故障

不防护返回的流量

旁路模式（Out-of-Band）

安全设备通过交换机端口镜像（SPAN）或分光器（TAP）等方式复制一份流量进行分析，不参与实际数据包的转发。设备只"看"流量，不改变流量的走向。

Port channel 接口捆绑 扩大清洗流量的带宽

Ebgp 集群 利用ebgp路由协议进行负载均衡

高可用集群会为虚拟服务（如网关、虚拟IP）分配一个固定的虚拟MAC地址。正常情况下，主节点使用这个虚拟MAC响应请求。

核心价值：当主节点故障，备节点接管时，会立即对外宣布自己开始使用这个相同的虚拟MAC地址。这样做的好处是，交换机等网络设备不会感知到MAC地址的变化，避免了广播风暴和ARP缓存更新延迟，从而实现毫秒级的业务无缝切换。

针对syn 攻击有效的两种方法 过滤掉畸形的64字节的syn包
（相比正常的syn缺少两字节 option字段）和 syn invalid

三秒重传算法 丢弃首个syn
只对在规定时间内发起重传的对应的ip发送的包才会进行后续通信
因为syn攻击大概率不会进行相同ip+syn的多次攻击（存在风险
部分app和os不会进行重传，致使业务无法正常进行）

Syn算法1 触发条件syn速率包到达阈值 算法一 防火墙发送错误的ack+syn
只有合法的客户端会发送reset 然后允许其与服务器连接

Syn算法2 触发条件syn速率包到达阈值 算法二 ads代替服务器发送 ack+syn
合法的客户端接受到对应的包后会相应对应的ack 此时ads在发送rst
此时可正常与服务器通信

三层回注![](D:\docxnotes\nsfocus\media/media/image1.png){width="6.5055555555555555in"
height="2.629861111111111in"}

vlan 0

quit

interface Vlanif10 创建vlan10的三层虚拟接口

ip address 10.10.10.254 255.255.255.0 给该接口配置ip地址

quit

interface Ethernet0/0/10 进入物理接口

port hyrid pvid vlan 10 设置该接口的pvid号为10

port hybrid untagged vlan 10 使 VLAN 10
的数据帧从该接口出去时不带标签（untagged）

bgp 65533

router-id 1.1.1.1

peer 20.20.20.1 as-number 65535

将当前的本地as号65533

设置 BGP 的 Router ID

指定一个 BGP 对等体，IP 地址为 20.20.20.1，对方 AS 号为 65535

主动路由牵引（通过 BGP 动态引流）

设备角色：向现网路由器（通常是核心交换机或边界路由器）发送 BGP
路由，宣告自己"更适合"处理某些流量（如被攻击
IP），从而将流量引到自己这里。

AS 号处理：强烈建议使用一个与现网不同且不冲突的私有 AS 号。

如果现网使用的是公有 AS 号（如 64512
以上一般是私有，但需确认），旁路设备应使用另一个私有 AS 号（例如现网 AS
65000，旁路用 65001）。

如果现网没有启用 BGP，只是静态路由，则旁路设备可独立配置
BGP，使用一个未使用的私有 AS 号即可。

1\. 避免路由环路

如果旁路设备和现网路由器使用同一个 AS
号，当旁路设备把路由发给路由器时，路由器会认为这条路由来自自己所在的
AS，可能不会接受（在 BGP 中，默认不接受 AS_PATH 中已包含自己 AS
号的路由，即防环机制）。即使接受，也可能造成路由振荡。

2\. 策略控制清晰

不同的 AS 号便于通过 BGP 属性（如 Local
Pref、MED）和路由策略，精准控制哪些流量被牵引、哪些不被牵引。运维时也能快速识别哪些路由是旁路设备发布的。

3\. 简化故障排查

当出现路由问题时，通过查看 AS_PATH
就能清楚知道流量经过了哪些设备，避免混淆。

acl number 3000

rule permit i destination 40.40.40.1 0

traffic classifier cls operator and

if-match acl 3000

traffic behavior beh

redirect ip-exthop 30.30.30.2 forced

traffic policy po

classifier csbehavior beh

interface Ethernet 0/0/3

traffic-policy po inbound

避免已经被牵引的流量收到二次牵引 能够正确的被服务器获取

![](D:\docxnotes\nsfocus\media/media/image2.png){width="4.388888888888889in"
height="2.9652777777777777in"}

vlan 40

quit

interface vlanif40

ipaddress 10.10.10.254 255.255.255.0

quit

interface Ethernet0/0/10

port link-type trunk

port trunk allow-pass vlan 40

创建一个 VLAN 40 的三层网关（10.10.10.254/24），并将 Ethernet0/0/10 设为
Trunk 端口，允许 VLAN 40
的带标签流量通过。这在网络中是常见的基础配置，用于连接下游交换机或路由器

三层虚拟接口（VLANIF接口），简单来说就是：给一个 VLAN 配了一个"网关 IP
地址"，让这个 VLAN 里的设备能够跨网段通信，并让交换机能够对属于该 VLAN
的流量进行路由转发。交换机既有二层转发（同一 VLAN
内），也有三层路由（不同 VLAN 间）。

根据回注时使用的转发机制不同，分为二层回注和三层回注。两者的核心区别在于转发依据是
MAC 地址还是 IP 地址，以及是否依赖路由表。

二层交换机

只工作在数据链路层。

没有 IP 路由表

![](D:\docxnotes\nsfocus\media/media/image3.png){width="4.194444444444445in"
height="2.298611111111111in"}

多台ADS 旁路部署在路由器上；

 在路由器上Xg1/0/6-xg1/0/11 捆绑成一个portchannel 接口；

 通过手工式配置portchannel 或lacp
方式动态生成portchannel，系统将自动选举出

一个端口作为portchannel 的主端口(masterpor)。主端口负责发送和接受bgp
等协议

Port-channel 的"选举"到底是什么？

Port-channel（链路聚合，即 IEEE 802.1AX /
802.3ad）的"选举"不是选主备设备，而是决定哪些物理端口可以加入同一个聚合组，以及哪些端口处于活动状态。

1\. 静态聚合（无协议）

管理员手动指定哪些端口加入 Port-channel。

没有"选举"过程，所有被指定的端口都参与聚合（只要链路 up）。

如果某个端口 down，它自动从聚合组中移除。

2\. 动态聚合（LACP，链路聚合控制协议） Link Aggregation Control Protocol

LACP 有一个协商选举过程，但它是端口级的角色协商，不是设备级的主备：

系统优先级：两端设备通过 LACP
协商，系统优先级高的设备在协商中具有主导权（决定哪些端口可以聚合）。

端口优先级：在系统优先级相同的情况下，再比较端口优先级，决定哪些端口是活动端口（Active），哪些是备用端口（Standby）。

活动链路数限制：如果配置了最大活动链路数（例如 max active-linknumber
2），则 LACP 会从可用端口中选出优先级最高的作为活动链路，其余作为备用。

本质：端口级的角色协商，目的是保证两端对聚合组的成员达成一致，并控制活动链路的数量。

注入接口 ：ADS设备上将清洗后的干净流量送回网络的物理或逻辑接口。

注入路由：ADS通过动态路由协议（通常是BGP）向网络中的路由器宣告的指向ADS自身的路由，用于将攻击流量牵引到ADS。

NTA上多个IP触发告警，但ADS只牵引了部分IP：IP组DDoS攻击告警类型里面ACK Flood的牵引告警等级是牵引高级告警，就只会牵引高级告警。4个IP的告警里面只有 211.139.77.55是触发了高级告警，所以只会牵引这一个IP。

![](D:\docxnotes\nsfocus\media/media/image4.png){width="5.767361111111111in"
height="2.4069444444444446in"}

![](D:\docxnotes\nsfocus\media/media/image5.png){width="5.760416666666667in"
height="1.5152777777777777in"}
