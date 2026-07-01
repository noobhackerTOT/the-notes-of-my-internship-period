# Security and Risk Management

Gavin is creating a report to management on the results of his most recent risk assessment. In his report, he would like to identify the remaining level of risk to the organization after adopting security controls. What term best describes this current level of risk?

Inherent risk A

Residual risk B

Control risk C

 Mitigated risk D

正确答案是：

**B. Residual risk（剩余风险）**

### 解析

在风险管理中：

- **Inherent Risk（固有风险）**

  - 在没有任何控制措施存在时的风险水平。
  - 即“原始风险”。
- **Residual Risk（剩余风险）**  ✅

  - 实施安全控制措施后，仍然存在的风险。
  - 这是管理层最关心的风险水平，因为它代表组织当前实际面临的风险。
- **Control Risk（控制风险）**

  - 控制措施未能发现或阻止问题的风险。
  - 常见于审计领域。
- **Mitigated Risk（已缓解风险）**

  - 不是 CISSP 风险管理中的标准术语。
  - 通常指已经通过控制措施降低的风险部分。

### 题目关键句

> "remaining level of risk to the organization after adopting security controls"

关键词：

- **remaining level of risk**
- **after adopting security controls**

这正是 **Residual Risk（剩余风险）**  的定义。

### CISSP 记忆公式

**Residual Risk \= Inherent Risk − Control Effectiveness**

例如：

- 固有风险 \= 100
- 安全控制降低风险 \= 70

则：

- 剩余风险 \= 30

因此答案是：

✅ ​**B. Residual risk**。

‍

‍

‍

Francine is a security specialist for an online service provider in the United States. She recently received a claim from a copyright holder that a user is storing information on her service that violates the third party's copyright. What law governs the actions that Francine must take? Copyright Act A

Lanham Act B

 Digital Millennium Copyright Act C

Gramm Leach Bliley Ac

t D Not Quite!

正确答案是：

✅ **C. Digital Millennium Copyright Act (DMCA)**

### 解析

题目关键词：

> online service provider  
> copyright holder  
> user is storing information that violates copyright

这正是 **DMCA（Digital Millennium Copyright Act，数字千年版权法）**  所规范的场景。

DMCA 为网络服务提供商（ISP、云存储、论坛、NAS云服务等）提供了 ​**Safe Harbor（避风港条款）** ：

如果服务提供商：

1. 收到版权侵权通知（Takedown Notice）
2. 及时删除或屏蔽涉嫌侵权内容
3. 提供反通知（Counter Notice）机制

则通常不会因用户上传的侵权内容承担版权责任。

---

### 为什么其他选项错误？

#### A. Copyright Act

美国版权法的总称。

DMCA 实际上是对版权法的补充和修订。

题目问的是：

> 收到版权侵权通知后应该采取什么行动

对应的是 DMCA 的通知删除机制（Notice-and-Takedown）。

---

#### B. Lanham Act

《兰哈姆法案》

主要保护：

- 商标（Trademark）
- 服务标志（Service Mark）
- 不正当竞争

与版权侵权无关。

---

#### D. Gramm-Leach-Bliley Act (GLBA)

金融行业隐私法。

要求金融机构保护客户金融信息。

与版权无关。

---

### CISSP 考点记忆

|法律|主要内容|
| ---------------| -------------------------------------|
|DMCA|数字版权、反盗版、Notice & Takedown|
|CFAA|计算机欺诈与滥用|
|ECPA|电子通信隐私|
|GLBA|金融数据隐私|
|HIPAA|医疗数据隐私|
|SOX|财务审计与内控|
|Lanham Act|商标保护|
|Copyright Act|著作权保护|

**考试技巧：**

看到以下关键词，直接想到 ​**DMCA**：

- Copyright complaint
- Takedown notice
- ISP liability
- Online service provider
- User-uploaded content
- Safe Harbor

因此答案是：

✅ **C. Digital Millennium Copyright Act (DMCA)** 。

‍

好的，收到。以下是包含完整题目在内的重新回答，已按您的要求**移除所有“补充知识延伸”** ，仅保留题目、正确答案和逐项解析。

---

### 题目原文

**After conducting a qualitative risk assessment of her organization, Sally recommends purchasing cybersecurity breach insurance. What type of risk response behavior is she recommending?**

- A. Accept
- B. Transfer
- C. Reduce
- D. Reject

---

### 1. 输出正确答案

**正确答案：B**

---

### 2. 逐项解析所有选项

#### B. Transfer（转移）—— 正确选项

- **为什么对**：购买网络安全保险是将风险发生后的**财务损失后果**转嫁给第三方保险公司。这并未改变风险发生的概率或内在影响，而是通过合同机制将经济负担转移出去，符合CISSP域1（安全与风险管理）中“风险转移”的明确定义。
- **管理者视角**：这是一项**风险财务处理策略**，而非技术控制。管理者通过支付固定保费，将不可预测的重大损失置换为可控的运营成本，属于正式的风险处置行为。

---

#### A. Accept（接受）—— 错误选项

- **为什么错**：接受意味着组织有意自留风险，不采取任何转嫁或降低行动，并承担全部潜在损失。购买保险支付保费的行为，恰恰说明组织**不愿自留**该财务风险，因此与接受完全相反。

---

#### C. Reduce（降低/减轻）—— 错误选项

- **为什么错**：降低指通过实施安全控制（如加密、访问控制、入侵检测等）来减小威胁发生的**可能性**或**影响程度**。保险不提供任何预防或遏制作用，它不降低泄露概率，也不减小泄露本身的运营或声誉损害，仅提供事后财务补偿。

---

#### D. Reject（拒绝/规避）—— 错误选项

- **为什么错**：CISSP标准术语中使用 **Avoid（规避）**  ，指终止导致风险的活动或项目以彻底消除风险。Sally推荐购买保险，意味着组织仍在继续原业务活动，并未终止任何事项，因此不符合规避的定义。

‍

‍

‍

‍

### 题目原文

**Wanda is working with one of her organization's European Union business partners to facilitate the exchange of customer information. Wanda's organization is located in the United States. What would be the best method for Wanda to use to ensure GDPR compliance?**

- A. Binding corporate rules
- B. Privacy Shield
- C. Standard contractual clauses
- D. Safe harbor

---

### 1. 输出正确答案

**正确答案：C**

---

### 2. 逐项解析所有选项

#### C. Standard contractual clauses（标准合同条款）—— 正确选项

- **为什么对**：标准合同条款（SCCs）是欧盟委员会预先批准的一套标准化合同模板，签约双方将其嵌入商业合同中，以承诺对传输的个人数据提供 GDPR 要求的保护水平。在欧盟法院（CJEU）通过“Schrems II”判决宣布 Privacy Shield 无效后，SCCs 与约束性公司规则（BCRs）成为向美国传输数据的两项主要合法机制。对于美国公司与欧盟伙伴之间**首次、非集团内部**的数据交换，SCCs 是操作最直接、成本相对可控且法律上被普遍认可的首选方案。
- **CISSP知识域对应**：本题对应**域1（安全与风险管理）**  中的“法律、法规与合规”以及“数据隐私”概念。GDPR 第五章对向第三国传输个人数据有严格限制，安全管理者必须熟悉合法的传输机制。
- **管理者视角**：作为风险决策者，面临欧美间数据跨境传输的合规需求时，应优先选用**欧盟委员会批准的标准合同条款（SCCs）**  。SCCs 提供了标准化的法律框架，能快速在合作双方之间建立合规的数据保护义务，是启动业务合作最高效、风险可控的路径。

---

#### A. Binding corporate rules（约束性公司规则）—— 错误选项

- **为什么错**：BCRs 是跨国企业集团内部用于规范其全球各分支机构间个人数据传输的内部隐私政策。它需要经过欧盟各成员国数据保护监管机构的审批，流程漫长且复杂。Wanda 是与“欧盟商业伙伴”（外部实体）交换信息，而非在其公司集团内部传输数据，因此 BCRs 在场景上不适用。

---

#### B. Privacy Shield（隐私盾）—— 错误选项

- **为什么错**：欧盟-美国隐私盾（Privacy Shield）框架**已于 2020 年 7 月被欧盟法院（CJEU）在“Schrems II”判决中正式宣布无效**。法院认为该框架未能为欧盟公民的个人数据提供与 GDPR 要求“实质等同”的保护。因此，Privacy Shield 已不再是合法可用的数据传输机制。虽然其后继者“欧盟-美国数据隐私框架”（DPF）已存在，但“Privacy Shield”这一选项本身是错误的。

---

#### D. Safe harbor（安全港）—— 错误选项

- **为什么错**：安全港（Safe Harbor）是比 Privacy Shield 更早的欧美数据传输框架，**已于 2015 年被欧盟法院在“Schrems I”判决中宣布无效**。它早已不再是一个合法有效的数据传输依据。该选项作为历史遗留的过时机制，是典型的干扰项。

### 题目原文

**Yolanda is the chief privacy officer for a financial institution and is researching privacy requirements related to customer checking accounts. Which one of the following laws is most likely to apply to this situation?**

- A. GLBA
- B. SOX
- C. HIPAA
- D. FERPA

---

### 1. 输出正确答案

**正确答案：A**

---

### 2. 逐项解析所有选项

#### A. GLBA（格雷姆-里奇-比利雷法案）—— 正确选项

- **为什么对**：GLBA（Gramm-Leach-Bliley Act）是专门针对**金融机构**的美国联邦法律，要求金融机构向客户清晰说明其信息共享做法，并采取适当的保护措施来保障客户**非公开个人信息**（如支票账户信息、社保号、交易记录等）的安全与隐私。Yolanda 所在的金融机构及其客户支票账户正好落入 GLBA 的管辖范围。
- **CISSP知识域对应**：本题对应**域1（安全与风险管理）**  中的“法律、法规、合规与调查”概念，重点考查常见行业隐私法规的适用范围。
- **管理者视角**：作为首席隐私官，首要任务是识别机构所面临的法律义务。GLBA 规定了**隐私通知义务**和**安全保障规则**，要求建立涵盖行政、技术和物理措施的信息安全计划。管理者应确保将 GLBA 合规要求融入机构的风险治理框架，定期进行风险评估并更新安全计划。

---

#### B. SOX（萨班斯-奥克斯利法案）—— 错误选项

- **为什么错**：SOX 主要针对**上市公司**的财务报告准确性和内部控制有效性，旨在防止财务欺诈。虽然 SOX 涉及信息系统的完整性（如 IT 控制），但它**不直接规范客户个人信息的隐私保护**。Yolanda 研究的隐私要求显然与 SOX 的核心目标（财务合规）无关。

---

#### C. HIPAA（健康保险携带和责任法案）—— 错误选项

- **为什么错**：HIPAA 适用于**医疗保健提供者、健康计划和医疗信息交换所**，以及处理受保护健康信息（PHI）的业务伙伴。客户支票账户信息属于**财务数据**，而非健康信息，因此 HIPAA 在此场景下不适用。

---

#### D. FERPA（家庭教育权利和隐私法案）—— 错误选项

- **为什么错**：FERPA 保护的是**学生教育记录**的隐私，适用于接受美国联邦教育资助的教育机构。金融机构的客户支票账户完全不涉及教育记录，因此该选项与题干场景毫无关联。
