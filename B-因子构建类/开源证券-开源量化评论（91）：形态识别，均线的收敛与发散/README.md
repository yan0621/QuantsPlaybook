# 形态识别：均线的收敛与发散

复现开源证券开源量化评论（91）《形态识别，均线的收敛与发散》。将 K 线均线收敛/发散形态从"个股择时"转变为"截面选股"因子，测试价量指标均线收敛对个股未来收益的预测能力。

## 核心因子

**收敛因子公式**：

```
factor = -log(1 + std(MA_1, MA_5, MA_10, MA_20, MA_60, MA_120))
```

其中 `MA_1` 即原始数据本身，对多根均线的取值计算标准差后取对数并取负。均线越收敛（标准差越小），因子值越大，表示形态越"收紧"，后续可能迎来突破行情。

基于不同价量指标，共构建五个因子：

| 因子 | 全称 | 输入数据 |
|------|------|----------|
| **PCF** | 价格收敛因子 | 后复权收盘价 |
| **VCF** | 成交量收敛因子 | 成交量 |
| **PVCF** | 价量双收敛因子 | PCF + VCF 截面标准化后合成 |
| **ACF** | 成交额收敛因子 | 成交额 |
| **TRCF** | 换手率收敛因子 | 换手率 |

## 项目结构

```
开源证券-开源量化评论（91）：形态识别，均线的收敛与发散/
├── FactorArithmetic/
│   └── convergence_factor.py   # 核心收敛因子计算
├── src/
│   ├── data_provider.py        # LoadH5Data: HDF5 数据加载（TTL 缓存）
│   ├── preprocess.py           # 因子预处理（标准化/去极值）
│   ├── utils.py                # 工具函数
│   └── analyzer/               # FactorAnalyzer 单因子分析框架
├── notebook/
│   └── 均线的收敛与发散.ipynb   # 主分析入口
├── data/                       # HDF5 本地数据文件
├── docs/
│   └── 20240414-开源证券-开源量化评论（91）.pdf  # 参考研报
├── CLAUDE.md                   # 项目技术文档
└── README.md
```

## 数据准备

本项目数据通过百度网盘分享：

- **链接**: https://pan.baidu.com/s/12N9xdzmeXb4SzN3YJLBeXw?pwd=68ix
- **提取码**: 68ix

下载后将所有文件放入 `data/` 目录，包含：

| 文件 | 说明 | 大小 |
|------|------|------|
| `adjclose.h5` | 后复权收盘价 | ~120MB |
| `volume.h5` | 成交量 | ~121MB |
| `amount.h5` | 成交额 | ~129MB |
| `turn.h5` | 换手率 | ~104MB |
| `calendar.h5` | 交易日历 | ~200KB |
| `meta_Dataset` | 数据集元信息 | - |

## 快速开始

```bash
# 1. 进入项目目录
cd "B-因子构建类/开源证券-开源量化评论（91）：形态识别，均线的收敛与发散"

# 2. 安装依赖
pip install pandas numpy loguru cachetools plotly

# 3. 启动 Notebook
jupyter notebook notebook/均线的收敛与发散.ipynb
```

> 注意：Notebook 中通过 `sys.path.append` 引用 `src/` 模块，需从策略根目录启动 Jupyter。

### 因子计算示例

```python
from FactorArithmetic.convergence_factor import calculate_convergence_factor
from src.data_provider import LoadH5Data

data = LoadH5Data()

# 加载后复权收盘价（2014-01-01 至 2023-12-31）
adjclose = data.get_data("data.adjclose", start_date="2014-01-01", end_date="2023-12-31")

# 计算价格收敛因子（PCF）
pcf = calculate_convergence_factor(adjclose, windows=[5, 10, 20, 60, 120])
```

## 关键约定

- 因子计算使用**后复权价格**（adjclose），避免除权除息导致的价格跳空
- 均线窗口默认 `[5, 10, 20, 60, 120]`，与研报一致
- `standardlize` 沿 axis=1（截面方向）做 z-score 标准化
- 与研报的差异：未对股票池做 ST/上市不足一年剔除，未做行业市值中性化

## 参考研报

- 开源证券，2024年4月，《开源量化评论（91）：形态识别，均线的收敛与发散》

## 许可证

本项目仅供学习和研究使用。
