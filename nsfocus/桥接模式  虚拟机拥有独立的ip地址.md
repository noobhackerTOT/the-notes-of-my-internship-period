桥接模式 虚拟机拥有独立的ip地址

Nat 虚拟机可以通过主机向外网发送 外网无法与主机通信

http only 虚拟机 可以与虚拟机 主机 相互通信

交换机端口类型 acess 连接用户主机 只允许唯一vlan id 通过本端口

带vlan标签 与该端口vlan 标签 pvid相同则允许通过 否则丢弃

Pvid port vlan id 缺省状态下所属的vlan

Trunk 端口的核心作用

Trunk
端口通常用于交换机之间或交换机与路由器/服务器之间的连接，其目的是允许多个
VLAN 的流量通过。与 Access 端口（只属于一个
VLAN，且通常不带标签）不同，Trunk 端口在发送帧时会根据配置决定是否保留
VLAN 标签（802.1Q tag）。

二、接收帧的处理逻辑

当一个帧到达 Trunk 端口时，交换机会根据该帧是否带有 VLAN
标签来决定如何处理：

如果接收到的帧带有 802.1Q 标签

交换机会读取标签中的 VLAN ID（VID）。

检查该 VLAN 是否在 Trunk 端口的"允许列表"中（即端口配置了允许哪些 VLAN
通过）。

如果允许：帧被接收，并进入对应 VLAN 进行转发。

如果不允许：帧被丢弃。

如果接收到的帧不带标签（untagged）

交换机会将该帧视为属于端口的 PVID（Port VLAN ID，端口默认 VLAN）。

然后检查该 PVID 是否在 Trunk 端口的允许列表中。

如果允许：帧被打上 PVID 对应的标签，然后进入该 VLAN 进行处理。

如果不允许：帧被丢弃。

关键点：对于 Trunk 端口，接收 untagged 帧时会根据 PVID
进行处理，但通常管理员会避免在 Trunk 端口上接收 untagged 帧，或者会将
PVID 设置为一个不用于业务的 VLAN（例如 VLAN 1 或专门的管理
VLAN），以防止意外加入错误的 VLAN。

一、Access 端口的核心特征

只属于一个 VLAN：Access 端口被静态分配到一个特定的 VLAN，这个 VLAN
被称为端口的 PVID（Port VLAN ID，端口默认 VLAN）。

发送帧时不带标签：当交换机从 Access 端口向外发送帧时，总是会去掉 802.1Q
标签，发送的是普通以太网帧（untagged）。终端设备通常不识别 VLAN
标签，所以必须用 untagged 帧。

接收帧时打上 PVID 标签：当 Access
端口收到一个不带标签的帧时，交换机会自动为该帧打上端口的 PVID
标签，将其归入对应的 VLAN 内部处理。

二、接收帧的具体处理

接收到的帧类型 处理方式

不带标签（untagged） 视为属于该端口的 PVID（即所属 VLAN），打上 PVID
标签，然后在交换机内部进行转发。

带标签（tagged） 通常直接丢弃。因为 Access
端口期望连接的是终端设备，终端设备不应发送带标签的帧。少数交换机可以配置为允许接收特定
VLAN 的 tagged 帧（如连接 IP 电话时的语音 VLAN），但这种场景一般会使用
Hybrid 端口或特殊的语音 VLAN 配置，不属于标准 Access 行为。

三、发送帧的具体处理

当交换机内部决定从某个 Access 端口转发一个帧时：

该帧在交换机内部一定属于某个 VLAN（带有 VLAN 标签）。

交换机比较该帧的 VLAN ID 与端口的 PVID：

如果相等：去掉标签，发送一个 untagged 帧。

如果不相等：正常情况下，Access 端口不允许转发其他 VLAN
的帧，因此不会出现这种情况（除非配置了 Hybrid 模式或允许了其他
VLAN，但那样就不再是纯 Access 端口了）。

因此，Access 端口发送出去的帧永远是不带标签的。

四、Access 端口与 PVID 的关系

PVID 是 Access 端口的唯一 VLAN：Access 端口的 PVID 就是它所属的
VLAN，两者总是相等
