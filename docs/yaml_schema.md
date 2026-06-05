# 鍓ф湰 YAML Schema 璁捐鏂囨。 v1.0

## Schema 姒傝
闈㈠悜褰辫鍓ф湰鐨?YAML 鏁版嵁鏍煎紡銆傝璁″師鍒欙細YAML鍙鎬с€佹墎骞?宓屽骞宠　銆佸奖瑙嗚涓氭儻渚嬪榻愩€?
## 瀹屾暣 Schema
```yaml
script:
  meta:
    title: "鍓ф湰鏍囬"
    original_novel: "鍘熻憲"
    author: "鍘熶綔鑰?
    genre: "棰樻潗"
    total_acts: 3
    total_scenes: 12
    summary: "鍓ф儏姊楁"
  characters:
    - id: "char_001"
      name: "瑙掕壊鍚?
      aliases: ["鍒悕"]
      role_type: "涓昏|閰嶈|鍙嶆淳"
      age: 28
      gender: "鐢穦濂?
      personality: "鎬ф牸"
      background: "鑳屾櫙"
      relationships:
        - target: "char_002"
          relation: "鐖跺瓙"
      first_appearance: "scene_003"
      arc_summary: "瑙掕壊寮у厜"
  acts:
    - act_number: 1
      title: "绗竴骞曪細寤虹疆"
      scenes:
        - scene_id: "scene_001"
          scene_number: 1
          heading: "鍐呮櫙 涔︽埧 鏃?
          location: "涔︽埧"
          time_of_day: "鏃?
          interior: true
          summary: "姒傝"
          characters_present: ["char_001"]
          beats:
            - type: "action"
              description: "鍔ㄤ綔鎻忚堪"
            - type: "dialogue"
              speaker: "char_001"
              line: "鍙拌瘝"
              tone: "鎰ゆ€?
            - type: "voiceover"
              speaker: "char_001"
              line: "鐢诲闊?
            - type: "transition"
              style: "鍒囧叆"
            - type: "montage"
              description: "钂欏お濂?
              shots: ["闀滃ご1","闀滃ご2"]
```

## 璁捐鍘熷洜

### YAML vs JSON
YAML鍙鎬ф帴杩戣嚜鐒惰瑷€銆佸師鐢熸敞閲婃敮鎸併€佸琛屾枃鏈棤闇€杞箟銆傚墽鏈槸"浜烘満鍗忎綔"浜х墿鈥斺€擜I鍑哄垵绋夸綔鑰呭弽澶嶆敼銆俌AML鎶婁慨鏀归棬妲涢檷鍒版渶浣庛€?
### beats鑰岄潪骞抽摵
浼犵粺鍔ㄤ綔-瀵圭櫧浜ゆ浛鎺掑垪锛屼絾AI闅句互绮剧‘鍒ゆ柇杈圭晫銆俙beats`鏁扮粍鐢╜type`鏍囪姣忎釜鑺傛媿(action/dialogue/voiceover/transition/montage)锛屾瘡绉嶈妭鎷嶆惡甯︿笓灞炲瓧娈碉紝鑴氭湰宸ュ叿瀵圭壒瀹氱被鍨嬫壒閲忔搷浣溿€?
### 瑙掕壊琛?鍒悕鏄犲皠
灏忚涓悓涓€瑙掕壊澶氱О鍛?"鏋楀啿""鏋楁暀澶?"璞瑰瓙澶?)锛宍aliases`鏄犲皠瑙ｅ喅AI璇嗗埆闂銆傝鑹茶〃鍦ㄩ《灞傦紝鍦烘浠呭紩鐢↖D閬垮厤閲嶅銆?
> 璁╁皬璇翠綔鑰呮嬁鍒板氨鑳芥敼锛屽埗鐗囦汉鐪嬪埌灏辫兘鐢ㄣ€?
