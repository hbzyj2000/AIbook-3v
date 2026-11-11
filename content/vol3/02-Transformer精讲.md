:abs 把配置读成形状、把形状读成参数量，再把参数量读成显存与算力。
:tag 架构

# 1　Transformer 精讲：从配置到形状到账本

原理在卷一第 12 章推导过。这一章做三件事：**读懂一份模型配置、追踪一次前向的全部形状、算出它的参数与显存**。这三件事会了，你看任何新模型架构都不会慌。

## 1.1 读懂配置

拿一个典型的 7B 配置举例：

```text
hidden_size          4096     # d_model，残差流的宽度
num_hidden_layers    32       # 层数
num_attention_heads  32       # 头数
head_dim             128      # = hidden_size / num_attention_heads
intermediate_size    11008    # FFN 中间维，约 2.7 倍 d_model
vocab_size           32000
max_position         4096
```

四个数字之间的关系记住：**每头维度 = 隐藏维 / 头数**。头数增加则每头维度减小。现代模型（LLaMA 系）常用 `head_dim=128` 固定，让头数与隐藏维解耦。

## 1.2 参数量手算

每层的参数量：

| 部件 | 公式 | 7B 配置下的值 |
| --- | --- | --- |
| Q、K、V 投影 | 3 × 隐藏维平方（MHA） | 3 × 16.8M = 50.3M |
| 输出投影 | 隐藏维平方 | 16.8M |
| FFN（SwiGLU，3 个矩阵） | 3 × 隐藏维 × 中间维 | 3 × 4096 × 11008 ≈ 135M |
| 两个 RMSNorm | 2 × 隐藏维 | 8K |
| **每层合计** | | **≈ 202M** |

32 层约 6.5B，加上嵌入（$32000\times4096\approx131$M，通常与输出层共享权重）约 **6.7B**。这就是"7B"的来源。

**记住这个比例：FFN 占每层参数的三分之二。** 所以"加宽 FFN"和"加层"是两种不同性质的扩容，前者提升每层的特征变换能力，后者提升组合深度。

## 1.3 一次前向的形状追踪

下面这段是教学用的简化实现，注释里标了每一步的形状。跑一遍，形状就长在脑子里了。

```python
import torch, torch.nn as nn, math

B, T, D, H, F = 2, 1024, 4096, 32, 11008
dh = D // H                       # 128

class Block(nn.Module):
    def __init__(self):
        super().__init__()
        self.ln1 = nn.RMSNorm(D)
        self.wq = nn.Linear(D, D, bias=False)
        self.wk = nn.Linear(D, D, bias=False)
        self.wv = nn.Linear(D, D, bias=False)
        self.wo = nn.Linear(D, D, bias=False)
        self.ln2 = nn.RMSNorm(D)
        self.w1 = nn.Linear(D, F, bias=False)   # SwiGLU 的 gate
        self.w3 = nn.Linear(D, F, bias=False)   # SwiGLU 的 up
        self.w2 = nn.Linear(F, D, bias=False)   # down

    def forward(self, x):                        # (B,T,D)
        h = self.ln1(x)
        q = self.wq(h).view(B, T, H, dh).transpose(1, 2)   # (B,H,T,dh)
        k = self.wk(h).view(B, T, H, dh).transpose(1, 2)
        v = self.wv(h).view(B, T, H, dh).transpose(1, 2)
        att = (q @ k.transpose(-1, -2)) / math.sqrt(dh)    # (B,H,T,T)
        att = att.masked_fill(causal_mask, -torch.inf)
        att = att.softmax(dim=-1)
        o = (att @ v).transpose(1, 2).reshape(B, T, D)      # (B,T,D)
        x = x + self.wo(o)
        h = self.ln2(x)
        x = x + self.w2(torch.silu(self.w1(h)) * self.w3(h))  # (B,T,D)
        return x
```

三个值得停下来看的地方：

- **`view(B,T,H,dh).transpose(1,2)`**：把"隐藏维"拆成"头数 × 每头维度"，再把头提到 batch 维旁边。这是所有实现里最容易写错的一步；
- **`att @ v` 之后再 `transpose` 回 `(B,T,D)`**：多头的输出要拼回去；
- **SwiGLU 有两个上投影一个下投影**：$w_1$ 做门控，$w_3$ 提供值，相乘后由 $w_2$ 降维。相比传统 FFN（两个矩阵），参数多 50%。

## 1.4 每个子层在做什么

| 子层 | 功能直觉 | 工程要点 |
| --- | --- | --- |
| 自注意力 | 位置之间交换信息（"我该看谁"） | 复杂度与序列长平方成正比，是长上下文瓶颈 |
| FFN | 每个位置独立做特征变换 | 参数占三分之二，可按位置并行 |
| 残差 | 保证梯度直通 | 深层需要缩放初始化 |
| 归一化 | 稳定各层尺度 | Pre-LN 是现代默认 |

一个流传很广的类比：**注意力是"通信"，FFN 是"计算"**。注意力让 token 之间传递信息，FFN 把信息加工。这个类比在分析 MoE（把 FFN 换成多个专家）时特别有用——MoE 本质是"扩大计算容量而不增加通信量"。

## 1.5 现代变体：四个必知改动

| 改动 | 作用 | 代价 |
| --- | --- | --- |
| RoPE | 相对位置编码，支持长度外推 | 需要配合插值方法才能真的外推 |
| RMSNorm | 省掉均值计算 | 数值上略不同，效果基本持平 |
| SwiGLU | 门控 FFN，效果更好 | 参数多 50% |
| GQA / MQA | 多个查询头共享一组 KV | KV cache 减少数倍，质量略降 |

**GQA 值得重点理解**：标准 MHA 里每个头都有自己的 K、V，KV cache 大小与头数成正比。GQA 让 $q$ 个查询头共享 1 组 KV（例如 32 个 Q 头共享 8 组 KV），KV cache 直接降到四分之一。这是长上下文与高并发场景的关键优化，几乎所有新模型都用它。

$$ \text{KV 大小}=2\times L\times S\times H_{kv}\times d_{head}\times B\times b $$

注意这里的 $H_{kv}$ 是 KV 头数，不是查询头数。**看模型配置时一定确认 `num_key_value_heads`**，它直接决定你的显存能撑多少并发。

## 1.6 Pre-LN 与 Post-LN

```text
Post-LN:  x = LN(x + Attn(x))     # 原始论文
Pre-LN:   x = x + Attn(LN(x))     # 现代主流
```

Pre-LN 的好处是**残差路径上没有归一化**，梯度可以无损地直通，深层训练更稳，不需要精细的 warmup。代价是输出范数会随层数增长，所以最后要加一个 final norm。

:::warn 常见坑
- 加载别人的权重却用了不同的 Norm 位置，loss 会异常高——这不是训练问题，是结构不匹配；
- 注意力实现里忘了因果掩码，训练时 loss 会异常低（因为看到了答案），推理时完全错乱。这是最隐蔽的一类 bug；
- 开了 flash attention 后某些自定义掩码不被支持，会静默回退到慢速实现，性能莫名下降。
:::
