# Excel 公式转数值工具

## 功能说明

这个工具可以将Excel文件中的所有公式转换为其计算后的数值，相当于在Excel中执行"复制-仅粘贴数值"操作。

**特点：**
- ✅ 保留所有单元格格式（字体、颜色、边框等）
- ✅ 保留工作表结构
- ✅ 支持多工作表Excel文件
- ✅ 自动计算公式的最终值
- ✅ 支持自定义输出文件名

## 安装依赖

```bash
pip install openpyxl
```

或者使用requirements.txt安装所有依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 基本用法（自动生成输出文件名）

```bash
python excel_formula_to_value.py input.xlsx
```

输出文件将自动命名为 `input_values.xlsx`

### 2. 指定输出文件名

```bash
python excel_formula_to_value.py input.xlsx -o output.xlsx
```

或使用完整参数：

```bash
python excel_formula_to_value.py input.xlsx --output output.xlsx
```

### 3. Python代码中调用

```python
from excel_formula_to_value import convert_formulas_to_values

# 方式1：自动生成输出文件名
convert_formulas_to_values('data.xlsx')

# 方式2：指定输出文件名
convert_formulas_to_values('data.xlsx', 'data_clean.xlsx')
```

## 使用场景

- **数据分享**：去除公式后分享给他人，避免暴露计算逻辑
- **数据备份**：将计算结果固化，防止引用错误
- **性能优化**：大量公式会拖慢Excel，转为数值可提升性能
- **数据迁移**：确保数据在不同系统间的一致性

## 示例

假设你有一个包含以下公式的Excel文件 `sales.xlsx`：

| A | B | C |
|---|---|---|
| 产品 | 单价 | 总价 |
| 苹果 | 10 | =B2*5 |
| 香蕉 | 8 | =B3*3 |

运行：
```bash
python excel_formula_to_value.py sales.xlsx
```

输出文件 `sales_values.xlsx` 将变为：

| A | B | C |
|---|---|---|
| 产品 | 单价 | 总价 |
| 苹果 | 10 | 50 |
| 香蕉 | 8 | 24 |

所有格式和样式都保持不变，只是公式被替换为了计算值。

## 技术原理

工具使用 `openpyxl` 库：
1. 加载Excel文件两次：一次获取公式，一次获取计算值
2. 遍历所有工作表和单元格
3. 识别包含公式的单元格（以`=`开头）
4. 用计算后的值替换公式
5. 保存新文件，保留所有原始格式

## 注意事项

- 原始文件不会被修改，结果保存到新文件
- 需要Excel文件中的公式能够正确计算
- 如果公式有错误（如 #REF!），错误值也会被保留
- 大型文件处理可能需要一些时间

## 故障排查

**问题：提示找不到文件**
- 检查文件路径是否正确
- 使用绝对路径或确保在正确的目录下运行

**问题：转换后的值为None**
- 原始文件可能需要先在Excel中打开并保存，以确保公式已计算

**问题：格式丢失**
- openpyxl支持大部分Excel格式，但某些复杂格式可能不完全兼容
