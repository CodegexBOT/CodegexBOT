# rbugs
A light-weight tool like spotbugs

## Selected Patterns

[单行多行分类](https://docs.google.com/spreadsheets/d/1aiYDHrQTci_ih8k-YIuSYZqYCnjTwvZHN3zOKpXv5zQ/edit?usp=sharing)

[Bad Practice例子](https://docs.google.com/presentation/d/1LT1VbDGkFMNARI54cV1zKUBHeN0wc-OSX4BLhUc3ieg/edit?usp=sharing)

[Correctness](https://docs.google.com/presentation/d/1mAIUuQgVncQWGuD7QwHzvduCaMhBQygl4KkkZVBOiBs/edit?usp=sharing)

[其它例子](https://docs.google.com/presentation/d/1cC30HDjKWqpbYAxNSyR_pTEAzpOLncFgn7WD0XfQSj4/edit?usp=sharing)

[Spotbugs Pattern Descriptions](https://spotbugs.readthedocs.io/en/stable/bugDescriptions.html)

## 开发流程
1. 从 [单行多行分类](https://docs.google.com/spreadsheets/d/1aiYDHrQTci_ih8k-YIuSYZqYCnjTwvZHN3zOKpXv5zQ/edit?usp=sharing) 表格中选取要实现的 pattern， 阅读 [pattern description](https://spotbugs.readthedocs.io/en/stable/bugDescriptions.html) 和例子, 初步判断是否可以用正则实现
2. 阅读并大概理解 spotbugs 实现代码，找出该 pattern 需要满足的条件，思考我们的实现中如何检查这些条件。如果条件信息不能直接获取，是否有替代方案
3. 构思自己的实现流程，设计正则表达式， 并实现（包含测试用例）
4. 在 `gen_detectors.py` 中添加新实现的 detector （不通过运行 `gen_detectors.py` 更新它的原因是顺序会乱，merge 的时候可能需要额外解决 conflicts）; 然后再运行你的测试用例

## 已有代码解释

1.  `comparison_exp.py` 

    跑和 spotbugs 的对比实验的脚本，暂时不用管

2.  `rparser.py`

    只需要**会用即可**，只会用到`parse()` 方法。具体使用例子看各个tests文件，用法很简单。在Pycharm的Structure窗口可以查看它包含的3个classes，或者在debug模式下可以看到它是如何分割输入的patch String的。

## 实现规范

1.  在 spotbugs 搜索 pattern 的缩写名，Code>Java下会有implementation和test files的链接  [example](https://github.com/spotbugs/spotbugs/search?l=Java&q=CNT_ROUGH_CONSTANT_VALUE)

2.  在 rbugs 下**新建你的实现文件**

    如对于 `spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindRoughConstants.java`, 则新建 `rbugs/patterns/detect/find_rough_constants.py`. 

    因为有的patterns比较相关，可以放在同一个file里。**class 名字**可以参考spotbugs里的

3.  在`implementation_notes`下新建你的 markdown 文件，以后每实现一个pattern，都在这个文件记录如下内容

    ```markdown
    ## PATTERN_NAME
        pattern 简介（可选，如为什么这样做不好）
    ### Examples
        正则表达式可以匹配的字符串的例子
    ### Spotbugs 如何实现
        读代码的笔记，和思路总结等
    ### 我的实现思路
        大致思路，与 spotbugs 不同的点(如哪些条件我们获取不了)
    ### Regex
        ```regexp
            用到的正则表达式
        ```
    ```

4.  测试

    -   测试文件命名：如 `find_rough_constants.py` 对应的测试文件名为 `test_find_rough_constants.py`

    -   测试用例命名规范：如 `test_PATTEN_NAME_01` 、`test_PATTEN_NAME_02` ...

    -   测试用例注释规范：有以下3种情况

        ```python
        # From spotBugs: https://xxx
        def test_PATTEN_NAME_01():
          pass
        
        # From other repository: https://xxx
        def test_PATTEN_NAME_02():
          pass
        
        # DIY
        def test_PATTEN_NAME_03():
          pass
        ```

## 总结

### expression level 中检查特定的 method invocation 的，有3种情况比较实现：
1. method name 比较特别，比如 `finalize()`, `getClass().getResource(...)`, 虽然我们无法获取 object 的类型和 invoked method 的 signature信息，也不太容易出错。
2. 对于比较 general 的  method name，比如 `add()`, 如果patterns检查它的特别用法，比如 `c.add(c)`, 我们也可以用正则实现，并且比较有把握说这样的invocation是有问题的
3. static method，当不是 static import 时，我们可以匹配像 `ClassName.staticMethod(...)` 这样的用法，比如 static method  的例子可以是 `Object.equals(...)`, `EasyMock.verify()`, (easymock 这个我们还没有实现)，减少误报的可能

