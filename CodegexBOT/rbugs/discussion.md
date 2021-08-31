# False Positive

## SA_SELF_COMPUTATION

### 运算优先级
```java
long expectUnacked = msgOutCounter - (i - i % cumulativeInterval);
```

### 在 String 中
```java
$(".lolkek").shouldNotBe(and("visible&visible", visible, visible));    // visible&visible

final AtomicReference<String> latest = new AtomicReference<>("2015-01-01-00-00-00");  // 01-01, 00-00
```

**保守策略**

跳过所有包含 String (即 `"`) 的语句

**激进策略**

想办法排除上述的 FP

## SA_SELF_COMPARISON

### 在 <...> 中

```java
List<List<Object>> rows = data.build();  // List<List

public <C, R> R accept(AnalyzedStatementVisitor<C, R> analyzedStatementVisitor, C context) {  // R> R

private static final List<String> STEP_NAMES = Arrays.asList("Given a stock of symbol <symbol> and a threshold <threshold>",
                        "When the stock is traded at price <price>",
                        "Then the alert status should be status <status>"
        );   // symbol <symbol, threshold <threshold, price <, status <status
```

### 设计缺陷

```java
  if (capabilities.profile == profile && capabilities.level >= level) {  // level >= level
```



**保守策略**

只检查 `if`,  `while` 和 `for` 等条件语句

**激进策略**

想办法排除上述的 FP

## CNT_ROUGH_CONSTANT_VALUE

### 在 String 中

```java
private String[] jstrUnionOfRightArray = { " [ ]", "[\"Today\"]", "[1234]", "[-0]", "[1.2333]", " [3.14e+0]", " [-3.14E-0]", "[0e0]", "[true]", 
                                          "[false]", "[null]", "[\"\\u1234\"]", " [{\"name\":\"test\"}]", "[{}, [{}, []]]   " , "    "};  // 3.14

TestUtil.testCall(db, "return custom.answer(42,3.14,'foo',{a:1},[1],true,date(),datetime(),point({x:1,y:2})) as data", (row) -> assertEquals(9, ((List)row.get("data")).size()));  // 3.14
```

**保守策略**

跳过所有包含 String (即 `"`) 的语句

**激进策略**

我觉得对这个 pattern 来说，保守策略就很好

# False Negative

## VA_FORMAT_STRING_USES_NEWLINE

这个不属于 filter 的 part

### String 拼接

```java
	if (expectedSha.equals(sha) == false) {
            final String exceptionMessage = String.format(
                Locale.ROOT,
                "SHA has changed! Expected %s for %s but got %s."
                    + "\nThis usually indicates a corrupt dependency cache or artifacts changed upstream."
                    + "\nEither wipe your cache, fix the upstream artifact, or delete %s and run updateShas",
                expectedSha,
                jarName,
                sha,
                shaFile
            );
```

### String 匹配中的转义字符

1. `"` 嵌套

   ```json
   "patch": "return new StringBuilder(\"<a href=\\\"\").append(href).append(\"\\\">\").append(text).append(\"</a>\").toString();"
   ```

   print 出来的样子

   ```
   return new StringBuilder("<a href=\"").append(href).append("\">").append(text).append("</a>").toString();
   ```

   在 Debug 模式下看到的是这样的

   ```
   'return new StringBuilder("<a href=\\"").append(href).append("\\">").append(text).append("</a>").toString();'
   ```

   对于 patch，我想到的解决方案是用 `[^\\](")` 找出 `"` (同时不会匹配 `\"`), 然后划分 string 范围

   ---

   类似的，String 中的换行符是如何转义的呢？

   ```json
   "patch": "System.out.println(\"\\nThis is a line.\" +\n"
   ```

   print 出来的样子

   ```
   System.out.println("\nThis is a line." +
   
   ```

   在 Debug 模式下看到的是这样的

   ```
   'System.out.println("\\nThis is a line." +\n'
   ```

   # 引入 Filter

   针对 FP 不同的解决策略，引入 conservative mode 和 aggressive mode

   

   # 注意

   1.  爬取时统计 repo 的 diversity(指the number of unique repos)
   2.  记录跑每一个 pull request 的时间
   3.  对比实验中，如果 warnings 不多对我们是好事，因为 spotbugs 不精确找到的 warnings 少，还要花时间 compile + download
   4.  目前问题：找到的 warnings 不多，FP 问题
       -   加 patterns
           -   是否要加 patterns，爬 1w PRs 看看多少个有 warnings，如果比例太少就加patterns，不需要一个个analysis判断是否为FP/FN
       -   加 rules 减少 FP
           -   总结出 general 的 rules，不然太 specific 就有 overfitting 的嫌疑

   # Rules

   ## 步骤

   1.  先判断 line 里是否有关键词 (mode)

   2.  用正则提取信息

   3.  condition 判断最好放后面

       `\1` 判断放后面

   ```regexp
   (\b\w[\w.]*(?P<aux1>\((?:[^()]++|(?&aux1))*\))*+)\s*([><=!]+)\s*\1[^.\w$]
   ```

   ```java
   if (capabilities.profile == profile && capabilities.level >= level) { 
   ```

   ## types 信息

   提升 priority

   如 `boolean a = c > b` 的 `boolean`，帮助判断 method 的 return type


-------------------- zhouying ------------------

## Mode 模式

### For Efficiency

#### Filter

- keywords 过滤
- type 信息
  - e.g. `int`, `boolean`



### For Effectiveness

#### Online search

- 提高工具分析能力, e.g.提供class类型信息

#### Reducing FP|FN

- Common problems

  - String

    - e.g.  "..."

  - General Type

    - T \<T\>

  - Lambda (*)

    - ->

  - Substring match

    - using `\b`



# Filter Rules

## Regular Expression Opposite

>   ((?!REGULAR_EXPRESSION_HERE).)*

### NM_METHOD_NAMING_CONVENTION

**目的**: 为了避免匹配 `new Constructor()` 

**正则**：

```regexp
(\b\w+\s+)?(?:\b\w+\s*\.\s*)*(\b\w+)\s*\(\s*((?:(?!new)\w)+(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+\w+)?
```

说明：有两处的 `\w+` 需要避免匹配  `new Constructor()` ，上述正则只在后面一处用了 `(?:(?!new)\w)+`。之后会考虑是否把前一处也改了，目前不改的原因是担心会增加正则的复杂度，需要执行更多steps才能完成匹配

**例子**：

```java
TrackSelector trackSelector = new DefaultTrackSelector(new AdaptiveTrackSelection.Factory(bandwidthMeter));  // 不匹配
```

## Capturing group to get extra information

出现 0 或 1 次的 capturing group

>   (REGULAR_EXPRESSION_HERE)?

### NM_METHOD_NAMING_CONVENTION

**正则**：

```regexp
(\b\w+\s+)?(?:\b\w+\s*\.\s*)*(\b\w+)\s*\(\s*((?:(?!new)\w)+(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+\w+)?
```

中的 `(\b\w+\s+)?`

**目的**：获取 target 前后的 token，来帮助 filter，因为一个正则需要适应多个应用场景。例如，上述正则需要能识别一下形式的 method name

-   ```
    methodName(...);
    obj.methodName(...);
    obj.m1(...).methodName(...);  // 每个method之间可以换行
    public void methodName(int i)  // 方法定义
    ```

所以需要 methodName 前后的 token 信息来帮助过滤以下几种 FPs

```java
			  # skip statements like "new Object(...)"
                if pre_token == 'new':
                    continue
                # skip constructor definitions, like "public Object(int i)"
                if pre_token in ('public', 'private', 'protected', 'static'):
                    continue
                # skip constructor definitions without access modifier, like "Object (int i)", "Object() {"
                if not pre_token and (args_def or strip_line.endswith('{')):
                    continue
                # skip match within string
                string_ranges = get_string_ranges(strip_line)
                method_name_offset = m.start(2)
                if in_range(method_name_offset, string_ranges):
                    continue
                # skip annotations
                if method_name_offset - 1 >= 0 and strip_line[method_name_offset - 1] == '@':
                    continue
```



