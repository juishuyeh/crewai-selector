# CrewAI Selector

一個 CrewAI CLI 插件，讓你可以輕鬆選擇並運行專案中的任何 Crew 或 Flow。

## 功能特色

- 🔍 自動發現專案中的所有 Crews 和 Flows
- 📋 互動式選單選擇要運行的項目
- 🚀 支援直接指定名稱運行
- 📊 Flow 視覺化支援
- 💡 自動提示需要的輸入參數

## 安裝
```bash
# 進入專案目錄
cd crewai-selector

# 安裝套件
uv pip install -e .

# 或使用 pip
pip install -e .
```

## 使用方法

### 1. 互動式選擇並運行
```bash
crewai-select run
```

會顯示所有可用的 Crews 和 Flows，讓你選擇要運行哪一個。

### 2. 列出所有 Crews 和 Flows
```bash
crewai-select list
```

### 3. 直接指定名稱運行
```bash
# 運行特定的 Crew
crewai-select run --name BsCrew

# 運行特定的 Flow
crewai-select run --name BusinessAnalysisFlow
```

### 4. 提供輸入參數
```bash
crewai-select run --name BsCrew --inputs '{"topic": "AI", "current_year": "2024"}'
```

### 5. 視覺化 Flow
```bash
crewai-select plot
```

### 6. 指定專案路徑
```bash
crewai-select run --path /path/to/your/project
```

## 範例

假設你的專案結構如下：
```
my-project/
├── src/
│   └── my_project/
│       ├── crew.py           # 包含 ConceptCrew, HierarchyCrew
│       └── main.py           # 包含 AnalysisFlow
└── pyproject.toml
```

運行 `crewai-select run` 會顯示：
```
可用的 Crews 和 Flows
┌────┬────────┬────────────────────┬─────────────────┐
│ #  │ 類型   │ 名稱               │ 位置            │
├────┼────────┼────────────────────┼─────────────────┤
│ 1  │ Crew   │ ConceptCrew        │ src/.../crew.py │
│ 2  │ Crew   │ HierarchyCrew      │ src/.../crew.py │
│ 3  │ Flow   │ AnalysisFlow       │ src/.../main.py │
└────┴────────┴────────────────────┴─────────────────┘

選擇要運行的項目 [1/2/3/q]:
```

## 開發
```bash
# 安裝開發依賴
uv pip install -e ".[dev]"

# 執行測試
pytest

# 格式化程式碼
ruff format .
```

## 授權

MIT License
