BGP是互联网的核心骨架协议。它能承载海量路由、实现跨运营商互通，核心在于构建以"路径属性"为基础的精细化选路和策略控制体系。

Boarder gateway protocol

核心概念：BGP是什么？

BGP（Border Gateway
Protocol，边界网关协议）是一个用于在自治系统（AS）之间交换路由信息的路径矢量协议。它通常被称为外部网关协议（EGP,
Exterior Gateway
Protocol），是目前唯一一个能处理互联网规模路由，并妥善处理不相关路由域间多路连接的协议。

自治系统（AS）：由同一个技术管理机构管理，使用统一选路策略的一组路由器集合。每个AS都有一个全球唯一的编号，即AS号。AS号分为2字节和4字节两种，其中2字节公有AS号范围为1-64511，私有范围为64512-65535。

特点：

可靠性：基于TCP协议（端口179）传输，确保路由信息可靠传递。

可扩展性：支持无类别域间路由（CIDR, Classless Inter-Domain Routing）。

稳定性：增量更新（只发送变化的路由），并有路由衰减等机制防止路由震荡，无需周期性路由更新。

可控性：通过丰富的路径属性（Path
Attributes），可实现极其灵活的路由策略，精细控制流量选路。

⚙️ 核心工作原理：邻居与状态机

BGP通过一个严格的有限状态机（FSM） 来建立和维护邻居关系。

1\. 五种报文类型

BGP通过以下五种报文完成邻居建立、路由交换和错误处理。

OPEN报文：TCP连接建立后发送的第一个报文，用于协商BGP版本、AS号、Hold
Time等参数，建立邻居关系。

KEEPALIVE报文：周期性发送，用于维持BGP邻居关系，也是对OPEN报文的确认。

UPDATE报文：用于在邻居之间通告可达路由，或撤销不可达路由。

NOTIFICATION报文：用于报告错误或异常情况，一旦发送或接收，BGP连接会立即中断。

ROUTE-REFRESH报文：用于请求对等体重发指定地址族的路由信息，常用于策略变更后刷新路由。

2\. BGP有限状态机 (FSM) **Finite State Machine**

BGP邻居从启动到完全建立，会依次经历以下6个状态：

1\.
Idle（空闲）：初始状态，BGP拒绝所有连接请求，等待Start事件触发连接尝试。

2\.
Connect（连接）：BGP启动连接重传定时器，主动发起TCP三次握手，等待连接成功。

3\.
Active（活跃）：若TCP连接失败，则进入此状态。它会不断尝试重新建立TCP连接。

4\.
OpenSent（打开发送）：TCP连接建立成功，BGP发送OPEN报文并等待对方的OPEN报文，对收到的报文进行参数协商和验证。

5\.
OpenConfirm（打开确认）：收到正确的OPEN报文后，发送KEEPALIVE报文，并等待对方的KEEPALIVE。

6\.
Established（已建立）：收到对方的KEEPALIVE后，进入此状态。此时BGP邻居关系正式建立，开始通过UPDATE报文交换路由信息。

BGP路径属性与选路原则

BGP不靠单一的"开销"值选路，而是通过一系列路径属性来决定最佳路径，这也是它能实现强大可控性的根本。

1\. 路径属性分类

BGP路径属性可按不同标准分类。

公认必遵：所有BGP实现都必须识别并包含在UPDATE报文中，如AS_PATH、Origin等。

公认任意：所有BGP实现都必须识别，但不强制包含在UPDATE报文中，如Local_Pref。

可选过渡：不强制所有BGP实现都识别，但如果识别了，则必须传递给邻居，如Community。

可选非过渡：不强制所有BGP实现都识别，如果不识别，则丢弃该属性，不传递给邻居。

2\. BGP选路原则 (Best Path Selection)

当存在多条到达同一目的地的路径时，BGP会按以下顺序进行比较：

首选权重（Weight）最高 (Cisco私有，仅在本地有效)

首选本地优先级（Local_Pref）最高 (在AS内传播)

优选本地起源的路由 (如通过network命令注入)

优选AS路径（AS_PATH）最短 (公认必遵属性，路径上的AS数量最少)

优选起源类型（Origin）最低 (IGP \> EGP \> Incomplete)

优选多出口区分（MED）最低 (用于在多个入口点间选择最佳路径)

优选EBGP路径，而非IBGP路径

优选到下一跳IGP度量（Metric）最低的路径

优选最老的路由 (稳定优先)

优选邻居路由器ID最低的路径

优选集群列表（Cluster_List）最短的路径

优选邻居IP地址最低的路径

大规模IBGP网络的解决方案

在一个AS内部，IBGP水平分割原则规定，从一个IBGP邻居学到的路由不能再通告给其他IBGP邻居。为解决此问题带来的全连接网络（全互联数量公式为n(n-1)/2）扩展性难题，BGP引入了以下两种机制：

1\. 路由反射器 (Route Reflector, RR)

原理：将AS内一台路由器指定为RR，允许它将从一个IBGP客户机学到的路由反射给其他IBGP客户机和非客户机，打破水平分割限制。

角色：RR本身、客户机（与RR建立反射邻居关系）、非客户机（既不是RR也不是客户机的其他IBGP设备）。

防环机制：通过Originator_ID（路由发起者标识）和Cluster_List（记录经过的RR集群）属性防止路由环路。

2\. 联盟 (Confederation)

原理：将一个大的AS划分为多个较小的成员自治系统，对外仍表现为一个统一的AS。成员AS之间建立特殊的联盟EBGP连接。

优势：保留了IBGP的Local_Pref、MED等属性在联盟内传递，并简化了配置和管理。

🛡️ BGP安全机制

MD5认证：对TCP连接进行MD5加密，防止非法邻居建立和路由信息篡改。

Keychain认证：允许定义一组密钥（每个密钥有生命周期和不同加密算法），可在不中断业务的情况下动态切换密钥。

GTSM（通用TTL安全机制）：通过检查IP报文头的TTL（Time to Live）
值是否在预设范围内来防御DoS攻击。

RPKI（资源公钥基础设施）：通过验证BGP路由起源的AS号是否合法，从源头上防止前缀劫持和路由泄露。

TCP-AO（TCP认证选项）：支持报文完整性检查，能有效防御TCP重放攻击，提供更高的安全性。

🚀 MP-BGP多协议扩展

传统BGP-4仅能管理IPv4单播路由。MP-BGP (Multiprotocol BGP)
是其多协议扩展，通过引入两个新的路径属性------MP_REACH_NLRI（发布可达路由）和MP_UNREACH_NLRI（撤销不可达路由），使其能为多种网络层协议传递路由信息。MP-BGP因此能支持IPv6单播（即BGP4+）、组播、VPNv4等众多地址族（Address
Family）。

🔗 BGP与IGP的交互

BGP自身不发现和计算路由，它只是路由的"搬运工"。

将IGP路由注入BGP：通常有两种方式。

Network命令：精确地逐条宣告本地路由表中的路由。

Redistribute（重分发）命令：将一种IGP（如OSPF）的路由批量引入BGP。

将BGP路由注入IGP：通常只在特定场景（如将默认路由注入内部网络）下使用，需要谨慎进行过滤，以防止外部海量路由冲击内部网络。

🛠️ BGP故障排查常用命令

show ip bgp
summary：查看BGP邻居的摘要信息，包括邻居AS号、状态、收发报文数量等。

show ip bgp neighbors
\[IP地址\]：查看指定BGP邻居的详细信息，如状态机、能力协商、定时器等。

show ip bgp
\[网络前缀\]：查看特定路由的详细信息，包括其路径属性（如AS_PATH、Local_Pref）。

show ip route bgp：查看最终被成功安装到全局IP路由表中的BGP路由。

debug ip bgp
updates：实时跟踪BGP路由更新，帮助分析路由波动或策略失效问题。

🧭 BGP最新发展与演进趋势

BGP协议自身也在不断发展，以适应现代网络的需求。

精细化错误处理：RFC 7606 定义了更精细的错误处理机制，如
treat-as-withdraw（视为撤销），减少因个别错误路由导致BGP会话重置的影响。

ADD-PATH能力扩展：允许BGP同时发布多条到达同一目的地的路径，用于负载分担和快速重路由。

Flowspec演进：BGP Flow Spec 与 Segment Routing (SR)
结合，实现更高效的流量引导和DDoS流量远程触发黑洞。

增强的韧性：针对格式错误的Update报文等场景，协议标准正朝着避免简单粗暴地复位整个会话的方向演进，以提升BGP会话的韧性和网络的整体可用性。

1.启动BGP进程，指定AS号

首先进入全局配置模式，启用BGP并指定你所在的AS号。

bash

\# 进入全局配置模式

configure terminal

\# 启用BGP，进入路由器配置模式，并指定本地AS号

router bgp 65001 \# 假设本地AS号为65001\[reference:0\]

2 配置Router ID

BGP Router
ID用于唯一标识你的路由器，是一个32位的数值，通常使用Loopback接口的IP地址。

bash

\# 在router bgp配置模式下设置Router ID

bgp router-id 1.1.1.1 \# 推荐使用Loopback接口地址\[reference:1\]

3 配置BGP邻居 (Peer)

使用 neighbor 命令来指定BGP对等体。关键参数是对方IP和所在的AS号。

EBGP (外部BGP)：对端AS号 不同。通常用于连接运营商或不同组织的网络。

bash

neighbor 203.0.113.2 remote-as 65002 \#
对端IP和AS号\[reference:2\]\[reference:3\]

IBGP (内部BGP)：对端AS号
相同。用于在同一个AS内部传递BGP路由。为了稳定性，通常使用Loopback地址建立邻居，并需要指定更新源。

bash

neighbor 10.0.0.2 remote-as 65001 \# 对端IP和AS号相同

neighbor 10.0.0.2 update-source loopback0 \#
指定从Loopback0接口发起连接\[reference:4\]

4 宣告本地路由

将你希望向邻居通告的网络前缀注入BGP路由表。

bash

\# 宣告一个本地网络，BGP会自动从路由表中寻找精确匹配的路由

network 192.168.1.0 mask 255.255.255.0\[reference:5\]\[reference:6\]

5 配置路由策略

通过路由策略（如prefix-list和route-map）可以精细控制路由的进出。

第一步：创建前缀列表 (Prefix-List)，定义需要匹配的网段。

bash

\# 创建一个名为"TO-INTERNAL"的前缀列表，允许10.0.0.0/8网段

ip prefix-list TO-INTERNAL permit 10.0.0.0/8

第二步：创建路由映射 (Route-Map)，关联前缀列表并定义动作。

bash

\# 创建一个名为"EXPORT-ROUTES"的路由映射，序列号10

route-map EXPORT-ROUTES permit 10

match ip address prefix-list TO-INTERNAL \# 匹配前缀列表中的路由

set local-preference 150 \# 设置本地优先级

第三步：在BGP邻居上应用策略。

bash

router bgp 65001

neighbor 203.0.113.2 route-map EXPORT-ROUTES out\]

路由守护进程（Routing
Daemon）是一个在操作系统后台运行的软件，它负责动态地学习、计算和更新系统的路由表，是构建动态路由网络的核心组件。

它的核心价值在于自动化：当网络拓扑结构发生变化（例如链路中断）时，它能自动发现新路径，并更新路由表，而无需人工干预。如果没有它，路由就必须通过route命令等方式手动维护，这种方式称为静态路由，在小规模且稳定的网络中很适用，但在复杂环境中将变得难以维护
