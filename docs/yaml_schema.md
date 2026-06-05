# 剧本 YAML Schema 设计文档 v1.0

## Schema 概览
面向影视剧本的 YAML 数据格式。设计原则：YAML可读性、扁平+嵌套平衡、影视行业惯例对齐。

## 完整 Schema
```yaml
script:
  meta:
    title: "剧本标题"
    original_novel: "原著"
    author: "原作者"
    genre: "题材"
    total_acts: 3
    total_scenes: 12
    summary: "剧情梗概"
  characters:
    - id: "char_001"
      name: "角色名"
      aliases: ["别名"]
      role_type: "主角|配角|反派"
      age: 28
      gender: "男|女"
      personality: "性格"
      background: "背景"
      relationships:
        - target: "char_002"
          relation: "父子"
      first_appearance: "scene_003"
      arc_summary: "角色弧光"
  acts:
    - act_number: 1
      title: "第一幕：建置"
      scenes:
        - scene_id: "scene_001"
          scene_number: 1
          heading: "内景 书房 日"
          location: "书房"
          time_of_day: "日"
          interior: true
          summary: "概要"
          characters_present: ["char_001"]
          beats:
            - type: "action"
              description: "动作描述"
            - type: "dialogue"
              speaker: "char_001"
              line: "台词"
              tone: "愤怒"
            - type: "voiceover"
              speaker: "char_001"
              line: "画外音"
            - type: "transition"
              style: "切入"
            - type: "montage"
              description: "蒙太奇"
              shots: ["镜头1","镜头2"]
```

## 设计原因

### YAML vs JSON
YAML可读性接近自然语言、原生注释支持、多行文本无需转义。剧本是"人机协作"产物——AI出初稿作者反复改。YAML把修改门槛降到最低。

### beats而非平铺
传统动作-对白交替排列，但AI难以精确判断边界。`beats`数组用`type`标记每个节拍(action/dialogue/voiceover/transition/montage)，每种节拍携带专属字段，脚本工具对特定类型批量操作。

### 角色表+别名映射
小说中同一角色多称呼("林冲""林教头""豹子头")，`aliases`映射解决AI识别问题。角色表在顶层，场次仅引用ID避免重复。

> 让小说作者拿到就能改，制片人看到就能用。
