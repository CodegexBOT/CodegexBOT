## FS: Format string should use %n rather than n (VA_FORMAT_STRING_USES_NEWLINE)

### Regex
```regexp
(?:(?:String\.format)|printf)\([\w.\s()]*,?\s*"([^"]*)"\s*
```
### Examples
```java

String.format( Locale.US , "Payload:\n%s" , new Object[1]);

String.format("Payload:\n%s" , new Object[1]);
```

### 实现思路

[SpotBugs](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FormatStringChecker.java#L107-L113)

```java
if ((m == null || m.isVarArgs())
    && sig.indexOf("Ljava/lang/String;[Ljava/lang/Object;)") >= 0
    && ("java/util/Formatter".equals(cl) && "format".equals(nm) || "java/lang/String".equals(cl)
            && "format".equals(nm) || "java/io/PrintStream".equals(cl) && "format".equals(nm)
            || "java/io/PrintStream".equals(cl) && "printf".equals(nm) || cl.endsWith("Writer")
                    && "format".equals(nm) || cl.endsWith("Writer") && "printf".equals(nm)) || cl.endsWith("Logger")
                            && nm.endsWith("fmt")) {

    if (formatString.indexOf('\n') >= 0) {
        bugReporter.reportBug(new BugInstance(this, "VA_FORMAT_STRING_USES_NEWLINE", NORMAL_PRIORITY)
```

- java.lang.String
    - `static String	format(Locale l, String format, Object... args)`
    - `static String	format(String format, Object... args)`
- java.util.Formatter (interface)
    - `Formatter	format(Locale l, String format, Object... args)`
    - `Formatter	format(String format, Object... args)`
- java.io.PrintStream.format()
    - `PrintStream	format(Locale l, String format, Object... args)`
    - `PrintStream	format(String format, Object... args)`
- java.io.PrintStream.printf()
    - `PrintStream	printf(Locale l, String format, Object... args)`
    - `PrintStream	printf(String format, Object... args)`
- *Writer.format()
- \*Writer.printf()
- \*Logger.fmt()

1. 检查方法名字，提取 caller 名字和括号中的参数

2. 检查参数内的 string 部分是否包含 `\n` 字符. 在 Java 里可以直接检查 `indexOf('\n')`，
   但用 python 实现时，发现string里的`\n`会被表示为 `\\n`



## DMI: Random object created and used only once (DMI_RANDOM_USED_ONLY_ONCE)
### Regex
```regexp
new\s+[\w\.]*Random(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\)))++\.next\w*\(\s*\)
```
### Examples
```java
// https://github.com/jenkinsci/android-emulator-plugin/commit/0e104f3f0fc18505c13932fccd3b2297e78db694#diff-238b9af87181bb379670392cdb1dcd6bL173
seedValue = new Random().nextLong();
// https://github.com/adaptris/interlok/commit/8dd32e9b89a4b17662faa7ca986756f3cc348cc7#diff-1e0469ce35c1d148418525088df452a2L405
pool.setTimeBetweenEvictionRunsMillis(threadLifetimeMs() + new Random(threadLifetimeMs()).nextLong());
// https://github.com/adaptris/interlok/commit/8dd32e9b89a4b17662faa7ca986756f3cc348cc7#diff-766b5e25592ad321e107f1f856d8a08bL102
pool.setTimeBetweenEvictionRunsMillis(EVICT_RUN + new Random(EVICT_RUN).nextLong());
// DIY
seedValue = new java.util.Random().nextLong();
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/DumbMethods.java#L495): 判断变量类型，其中freshRandomOnTos和freshRandomOneBelowTos两个变量意思不明。

根据[搜到的例子](https://github.com/search?q=DMI_RANDOM_USED_ONLY_ONCE&type=commits)，可以匹配形如 `new java.util.Random(XXX).nextXXX()` 的用法，它创建对象后马上使用，而不是把对象存在变量里，方便复用

##DMI: Don’t use removeAll to clear a collection (DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION)
检测形如 c.removeAll(c) 的pattern

### Regex

```regexp
(.*)\.removeAll\((.*)\)
```
### Examples
```java
c.removeAll(c)
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindUnrelatedTypesInGenericContainer.java#L509)

1. 判断 object 和传参是否相等
2. 如是，再判断 method name 是否是 `removeAll`

## ES: Comparison of String objects using == or != (ES_COMPARING_STRINGS_WITH_EQ)
如题，unless both strings are either constants in a source file, or have been interned using the String.intern() method
### Regex
```regexp
((?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w."])++)\s*[!=]=\s*((?:(?&aux1)|[\w."])+)
```
### Examples
```java
if ("FOO" == value)
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindRefComparison.java#L996) 

由于我们无法获得变量类型等信息，故提取 `op_1 == op_2` 中的 `op_1` 和 `op_2`。如果其中一个是带双引号的string constant，另一个既不是string constant，也不以 `String.intern` 开头，则判断它为 ES_COMPARING_STRINGS_WITH_EQ

## UI: Usage of GetResource may be unsafe if class is extended (UI_INHERITANCE_UNSAFE_GETRESOURCE)

### Regex
```regexp
(\w*)\.*getClass\(\s*\)\.getResource(?:AsStream){0,1}\(
```
### Examples
```java
getClass().getResourceAsStream("XStreamDOMTest.data1.xml")
this.getClass().getResourceAsStream(DB_SCHEMA)
URL url = this.getClass().getResource(imagePath)
```
### 实现思路
[spotbugs](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/InheritanceUnsafeGetResource.java#L108)

我的思路：提取 `this.getClass().getResource(...)` 里 `this` 位置的内容，如果为 None 或 this， 则生成 warning

## Nm: Class names shouldn’t shadow simple name of superclass (NM_SAME_SIMPLE_NAME_AS_SUPERCLASS)
Java 编译规则：

1. class只能继承一个父类，但可以实现多个接口
2. extends 在 implements 之前 

### Regex
```regexp
class\s+([\w$]+)\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+extends\s+([\w$.]+)
```
### Examples
```java
public class SpringLiquibase extends liquibase.integration.spring.SpringLiquibase
public class Future<V> extends io.netty.util.concurrent.Future<V>
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L308) 

1. 提取 class name 和 superclass name，默认 class name 是 simple name
2. 假如 superclass name 是 qualified name，则从中提取 simple name
3. 判断两者是否相等。

## Nm: Class names shouldn’t shadow simple name of implemented interface (NM_SAME_SIMPLE_NAME_AS_INTERFACE)
Java 编译规则： 

1. interface 可以 `extends` 多个 interfaces
2. interface 定义不能有 implements 语句

### Regex
有两种情况：
1. class 定义里的 implements 部分
2. interface 定义里的 extends 部分

```regexp
class\s+([\w$]+)\b.*\bimplements\s+([^{]+)
interface\s+([\w$]+)\s*(?P<gen><(?:[^<>]++|(?&gen))*>)?\s+extends\s+([^{]+)
```
第二个正则表达式参考了 `((?!m).)*`， 表示匹配 `.` 的时候不包含
### Examples

```java
public class LocaleResolver implements org.springframework.web.servlet.LocaleResolver

public interface Future<V> extends io.netty.util.concurrent.Future<V> {

public class LocaleResolver implements DIY, org.springframework.web.servlet.LocaleResolver {

public class ALActivityImpl extends org.apache.shindig.social.core.model.ActivityImpl implements Activity
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/Naming.java#L313) 类似 NM_SAME_SIMPLE_NAME_AS_SUPERCLASS

1. 提取 class/interface name 和 implements/extends 后的字符串
2. 将字符串 split 成 superclass/superinterface 的 simple name 列表
3. 判断列表中是否包含 class/interface name


## IL: A collection is added to itself (IL_CONTAINER_ADDED_TO_ITSELF)
As a result, computing the hashCode of this set will throw a StackOverflowException.
### Regex
```regexp
(.*)\.add\((.*)\)
```
不建议使用 `(\w*)\.add\(\1\)` 这样的写法，会少匹配。如 `bb.add(b)` 会匹配 `b.add(b)`
### Examples
```java
testee.add(testee)
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/InfiniteRecursiveLoop.java#L104):
1. 检查 add 方法的 signature
2. 判断 stack 里的 object 和参数是否相等

我的做法：用正则匹配 `c.add(c)` 中 object 和参数位置，判断它们是否相等. 类似 DMI_USING_REMOVEALL_TO_CLEAR_COLLECTION.

## RV: Random value from 0 to 1 is coerced to the integer 0 (RV_01_TO_INT)
### Regex
```regexp
\(\s*int\s*\)\s*(\w+)\.(?:random|nextDouble|nextFloat)\(\s*\)
```
### Examples
```java
(int) Math.random()
(int) randomObject.nextDouble()
(int) randomObject.nextFloat()
```
### 实现思路
[spotbugs 实现](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/DumbMethods.java#L1144)
1. 首先要满足以下条件, 似乎是调用了 `Random.nextDouble` 或 `Math.random` 方法
```java
seen == Const.INVOKEVIRTUAL && "java/util/Random".equals(getClassConstantOperand())
&& "nextDouble".equals(getNameConstantOperand()) || seen == Const.INVOKESTATIC
&& ClassName.isMathClass(getClassConstantOperand()) && "random".equals(getNameConstantOperand())
```
2. 然后要满足 `seen == Const.D2I` ，其中 seen 是传入的参数，Const.D2I 是某个库定义的，应该是什么浮点数被 convert 成 integer 的意思

我的实现思路：
1. 匹配静态调用 `(int) Math.random()`
2. 匹配调用 `(int) randomObject.nextDouble()`， 并且拓展到 `nextFloat()` 方法。由于 randomObject 的名字可变，我们可以提取变量名，转成lowercase，看看是否包含 `rand`或者等于 `r`, 如果是，则 confidence 可以较高一点。


## Se: The readResolve method must be declared with a return type of Object. (SE_READ_RESOLVE_MUST_RETURN_OBJECT)

规范的定义为 `ANY-ACCESS-MODIFIER Object readResolve() throws ObjectStreamException`；与 SE_READ_RESOLVE_IS_STATIC 一起实现

### Regex
```regexp
((?:static|final|\s)*)\s+([^\s]+)\s+readResolve\s*\(\s*\)\s+throws\s+ObjectStreamException
```
### Examples
```java
Object readResolve() throws ObjectStreamException

public String readResolve() throws ObjectStreamException

static String readResolve() throws ObjectStreamException // 优先报返回值类型的 warning，而不报 static 的warning
```
### 实现思路
[Spotbugs](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/SerializableIdiom.java)
中的思路是先检测方法名是否为readResolve 且当前 class 是 serializable，如果是，则检查返回值类型是否是 `java.lang.Object` 类型，然后才
检测是否有static修饰词。

我的实现思路为：

1. 我们无法获取 class 是否是 serializable，故将默认 priority 从 high 降为 normal，且假设程序员只在 serializable class 中重写 readResolve 方法

2. 用 `([^\s]+)\s+readResolve` 提取返回值类型，判断是否为 `Object`

## EQ_COMPARING_CLASS_NAMES
错误原因：different classes with the same name if they are loaded by different class loader

### 例子
```java
if (auth.getClass().getName().equals(
    "complication.auth.DefaultAthenticationHandler")) {
```

```java
if (x.getClass().getName().equals(y.getClass().getName() )) {
```

### Spotbugs 实现思路
```java
if (callToInvoke(seen)) {
    equalsCalls++;
    checkForComparingClasses();
    if (AnalysisContext.currentAnalysisContext().isApplicationClass(getThisClass()) && dangerDanger) {
        bugReporter.reportBug(new BugInstance(this, "EQ_COMPARING_CLASS_NAMES", Priorities.NORMAL_PRIORITY)
                .addClassAndMethod(this).addSourceLine(this));
    }
}
```
没看懂，部分理解
1. callToInvoke(seen) 大概干了什么：
    - 检查是否是 equals 方法或类似 equals 的方法
        - 方法名的LowerCase是否包含 equals
        - 检查 signature, 即参数类型和返回值 (注意有两种用法)
            - o1.equals(o2)
            - Objects.equals(o1, o2)
2. checkForComparingClasses() 大概干了什么:
    - 好的 equals class 用法 (sawGoodEqualsClass = true):
        - o1.getClass() == o2.getClass()
        - xx.class == o2.getClass(), 且 xx.class 是 final class
    - 不好的用法 (sawBadEqualsClass = true)
        - xx.class == o2.getClass(), 但 xx.class 不是 final class: 报 EQ_GETCLASS_AND_CLASS_CONSTANT (Bad Practice)
    - 总的来说就是检查 EQ_GETCLASS_AND_CLASS_CONSTANT，给它调整 priority，并且设置两个成员变量 `sawGoodEqualsClass` 和 `sawBadEqualsClass` 的值
3. 要使得 dangerDanger 为 true，需要出现 `getName` 和 `getClass` 方法名
4. report bug 如果该 class 是 application class 且 danger 为 true

综上，首先检查是否调用了 equals 方法，然后检查 equals 方法要比较的两个对象是否调用了 `getClass().getName()`

### 我的实现思路
1. 当检查到 equals 方法时，提取它要比较的两个对象 (两种用法)
2. 判断两个参数是否有一个以 `getClass().getName()` 结尾
3. 提速: 只对同时包含 `equals`, `getClass` 和 `getName` 的语句进行正则匹配

### 正则
用来提取 equals 的比较对象，equals 前的不一定提取得完整，但至少可以保证可以完整提取到 `getClass().getName()`
```regexp
\b((?:[\w\.$"]|(?:\(\s*\)))+)\s*\.\s*equals(?P<aux1>\(((?:[^()]++|(?&aux1))*)\))
```

## DM_INVALID_MIN_MAX

Incorrect combination of Math.max and Math.min

### 例子
[spotbugs tests](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugsTestCases/src/java/sfBugsNew/Feature329.java)

```java
return Math.min(0, Math.max(100, rawInput));

return Math.max(Math.min(0, rawInput), 100);

int score = (totalCount == 0) ? 100 : (int) (100.0 * Math.max(1.0,
                Math.min(0.0, 1.0 - (scaleFactor * failCount) / totalCount)));
```

### spotbugs 实现
见 [InvalidMinMaxSubDetector](https://github.com/spotbugs/spotbugs/blob/d9557689c2a752a833eedf4eb5f37ee712a9c84f/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/DumbMethods.java#L94)

初时，两成员变量 `upperBound = lowerBound = null`

1. 检查是否调用了 `Math.max` 或者 `Math.min` 方法。是则到下一步
2. 检查该方法的两个参数是否只有一个为 constant (数字)。 是则到下一步，否则两成员变量设为 null
3. 如果该方法名为 `min` ，则将 constant 赋值给成员变量 `upperBound` ，否则赋值给 `lowerBound`

接下来的部分不太理解，因为它似乎只对 `upperBound != null` 即外层是 `min` 成立。大概理解一下就好

4. 检查外层 min/max 函数的两个参数，是否只有一个是 method 类型，且也是 `Math.min` 或 `Math.max` 函数，如是则下一步
5. 如果 `lowerBound.compareTo(upperBound)` 结果大于 0, 则报该 bugs

我估计这个 subDetector 的 sawOpcode 方法应该是被调用了两次，才能给两个成员变量都赋上值。而且它从 stack 中读取的内容原本顺序应该也和我之前想的不一样，即先读取的是内层的 min/max，然后才是外层的 min/max，但是我不确定。

### 我的实现
1. 用正则提取第一个 `Math.min(...)` 或 `Math.max(...)` 的传参字符串 A
2. 再对传参字符串 A 应用上述正则，提取它的传参字符串 B
3. 将两个传参字符串的 `\s` 替换为空，然后根据 `,` split
4. 用强制转换成数字的办法，分别找出它们的参数中为 constant 的那个
5. 比较它们的大小


## BIT_SIGNED_CHECK， BIT_SIGNED_CHECK_HIGH_BIT

### Regex

```regex
\(\s*([~-]?(?:(?P<aux1>\((?:[^()]++|(?&aux1))*\))|[\w.-])++)\s*([&|])\s*([~-]?(?:(?&aux1)|[\w.])++)\s*\)\s*([><=!]+)\s*([0-9a-zA-Z]+)
```

### Examples

```Java
if ((e.getChangeFlags() & 0x8000000000000000L) > 0)
if ((x & ~0x10000000) > 0)
if ((-1 & x) > 0)
```

### 实现思路

#### Spotbugs
1. 由 `!equality && arg2.longValue() == 0` 可知，BIT_SIGN_CHECK 和 BIT_SIGN_CHECK_HIGH_BIT 针对 `((A & CONSTANT)) > 0`, `((A & CONSTANT)) >= 0`, `((A & CONSTANT)) < 0` 和 `((A & CONSTANT)) <= 0`.
2. 根据 `highBit` 和 `onlyLowBits` 的字面意思可以猜测，它们取决于 `arg1` 的二进制形式最高位的 1 在哪里，也就是 `arg1` 的大小。看了 `getFlagBits` 方法的代码后，我猜测大概是用来处理 long 和 int 这两种类型的，具体目的不明。
3. 接下来关注 high bit 和 low bit 的定义，即有多少个 bits 算是 high bit 或 low bit。我们可以找出几个临界值。

	- 从 `onlyLowBits = bits >>> 12 == 0`，我们可以判断二进制在 12 bits 以内的 `arg1` 会使得 `onlyLowBits` 为 true, 因为不考虑符号位，移除最低 12 bits 后，只剩下 0 了。于是第一个临界值为`0b1111 1111 1111`, 即4095。最后发现当 `-4096 <= arg1 <= 4095` 时，onlyLowBits 就会为 true，且 `highbit` 为 false，无论 long or int

	- 从 `highbit = !isLong && (bits & 0x80000000) != 0` 得当constant `arg1` 为 int，且它的最高位(第32位)为 1 时，`highbit` 为 true. `0x80000000` 对应的数字是 `2147483648L`, 但在 Java 中它们并不相等，但是 `0x80000000 == -2147483648` 是 true. 经试验，

		- 131071，即 `0x1ffff`（17个1,超32半数，用 `~arg1` 进行的判断），从两者皆为 false 跳转为 `highbit = true	onlyLowBits = false`， 之后又变回两者皆 false

		- 196607，即 `2fffe` （17个1,超32半数，用 `~arg1` 进行的判断），又出现上面的跳转

	> Integer.MAX_VALUE = 2^31 - 1 = 2147483647, 即 0x7fffffff, 31个 one-bit
	> Integer.MAX_VALUE + 1 = Integer.MIN_VALUE = -2147483648, 即 0x80000000, 只有第 32 bit 是 1


```java
// arg1 和 arg2 可以为 null 或 Long 和 Integer 的  constant
if (arg1 == null || arg2 == null) { return; }
boolean isLong = arg1 instanceof Long;
// 当 Opcode 为 <, <=, >, >= 时，equality 为 false; 当 == 或 != 时，为 true
if (!equality && arg2.longValue() == 0) {
	// 看不懂以下三句在干什么
    long bits = getFlagBits(isLong, arg1.longValue());
    // 似乎是为了判断 arg1 是不是负数， 
    // 据观察，对 long 来说(64 bits)，大于等于 0x8000000000000000L 的是负数，0x7fffffffffffffffL 为最大的正数
    // 对 int 来说 (32 bits), 大于等于 0x80000000 的是负数， 0x7fffffff 为最大的正数
    // 而在 python 里，int('0x8000000000000000', 0) 转换出来的还是正数
    // 如何区分 int 和 long 呢？ 可以通过判断 constant 是否有后缀 'L' 实现。如果没有，则为 int 类型（不然编译不通过），和 int 的最大正数比较判断是否是负数
    // 如果给 int 类型赋超过 32 bits 的值，或者给 long 类型赋超过 64 bits 的值, Java 编译器都会报错; 
    // Java 编译器还要求 超过 32 bits 的 constant， 都要带 'L' 后缀
    boolean highbit = !isLong && (bits & 0x80000000) != 0 || isLong && bits < 0 && bits << 1 == 0;
    boolean onlyLowBits = bits >>> 12 == 0;  // -4096 <= arg1 <= 4095 (二进制12个1)，
    BugInstance bug;
    if (highbit) {
    	// Const.IFLE 代表 <=, IFGT 为 >， 见 https://docs.oracle.com/javase/specs/jvms/se8/html/jvms-6.html#jvms-6.5.ifge  对于这两种符号，置信度为 High， 对另外两种为 Medium
        bug = new BugInstance(this, "BIT_SIGNED_CHECK_HIGH_BIT", (seen == Const.IFLE || seen == Const.IFGT) ? HIGH_PRIORITY: MEDIUM_PRIORITY);
    } else {
        bug = new BugInstance(this, "BIT_SIGNED_CHECK", onlyLowBits ? LOW_PRIORITY : MEDIUM_PRIORITY);
    }
```
相关方法
```java
static int populationCount(long i) {
        /* 
        1. Returns the number of one-bits in the two's complement binary representation of the specified long value. 即数给定的long值的二进制补码表示形式中，1的个数

        2. 正整数的补码是其二进制表示, 与原码相同, 例：+9的补码是00001001
        
        3. 负整数的补码，将其原码除符号位外的所有位取反（0变1，1变0，符号位为1不变）后加1. 
        	例：-5对应负数5（10000101）→所有位取反（11111010）→加00000001(11111011)
		*/
        return Long.bitCount(i);
    }

    static long getFlagBits(boolean isLong, long arg0) {
    	/*
    		如果 arg0 实际是 int，则把它转成 32-bit (0xffffffffL)
   
			返回 arg0 和 ~arg0 (即 arg0 全部取反)中，对应的二进制补码含 1 个数最多的那个
			但不知道有什么意义
    	*/
        long bits = arg0;
        if (isLong) {
            int a = populationCount(bits);
            long b = ~bits;
            int c = populationCount(b);
            if (a > c) {
                bits = ~bits;
            }
        } else if (populationCount(0xffffffffL & bits) > populationCount(0xffffffffL & ~bits)) {
            bits = 0xffffffffL & ~bits;
        }
        return bits;
    }
```

#### rbugs
因为不太看得懂 spotbugs 的实现，只好根据 description 出发，提取 `&` 两边的操作数, 判断是否包含 constant。如果 constant 是负数，则为 BIT_SIGNED_CHECK_HIGH_BIT, 否则 BIT_SINED_CHECK

注意 Java 中 int 和 long 的正负数分界，如果提取到的 constant 不是用十进制表示的，那么在 python 中转化成数字时，是个正数，因为 python 可以表示任意大小的数字。具体解决方法见代码实现。

### BIT_AND_ZZ

与上述两个 patterns 一起实现。当 constant 为 0, 操作符为 `!=` 或 `==` 时，为 BIT_AND_ZZ

## BIT_AND, BIT_IOR

### 例子
```java
if ((e & 0x40) == 0x1){

if ((e | 1) != 0) {
```

### SpotBugs 实现思路

代码还比较容易读懂需要满足什么条件，难点在于 BIT_IOR 和 BIT_AND 的 dif 计算的理解（我还没有理解为什么这样算可以检测）

```java
if (equality) {
    long dif;
    String t;

    long val1 = arg1.longValue();  // arg1 是 & 或者 | 的 const 操作数
    long val2 = arg2.longValue();  // arg2 是 == 或 != 后面那个 constant

    if (bitop == Const.IOR) {
        dif = val1 & ~val2;
        t = "BIT_IOR";
    } else if (val1 != 0 || val2 != 0) {
        dif = val2 & ~val1;
        t = "BIT_AND";
    } else {
        dif = 1;
        t = "BIT_AND_ZZ";
    }
    if (dif != 0) {
        BugInstance bug = new BugInstance(this, t, HIGH_PRIORITY).addClassAndMethod(this);
```

### 我的实现思路
基本照搬上面的

### 正则
同 BIT_SIGNED_CHECK 的，改了一下，使得它可以提取两个操作数、位运算符号、大小比较符号和对应的常数。

发现：
1. 位运算操作必须要用括号括起来，然后才能和别的数比较，否则编译报错。例如 `A & C == D` 是不合法的，应为 `(A & C) == D`
2. 假如 `(A & C) == D` 会引发 warning，spotBugs 和 rbugs 都不会对 `D == (A & C)`。估计 spotBugs 从栈中读取顺序也有限制。


## SA_SELF_COMPUTATION

SA_FIELD_SELF_COMPUTATION 和 SA_LOCAL_SELF_COMPUTATION，因为我们无法区分 field 和 local variable

### 例子
```java
x & x
x - x
boolean dieselXorManual = car.isDiesel() ^ car.isDiesel();
```
### SpotBugs 实现思路
[field](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindSelfComparison.java#L316)


1. 从以下代码可以看出包括的操作符有 `|`, `&`, `^` 和 `-`

```java
switch (seen) {
	...
    case Const.LOR:
    case Const.LAND:
    case Const.LXOR:
    case Const.LSUB:
    case Const.IOR:
    case Const.IAND:
    case Const.IXOR:
    case Const.ISUB:
        checkForSelfOperation(seen, "COMPUTATION");
        break;
```

2. 从 stack 获取两个 operands，如果是 float 或者 double 类型则返回（后面看不懂）

[local](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindSelfComparison2.java#L212)

### 我的实现思路
直接匹配

## SA_SELF_COMPARISON

### SpotBugs 实现思路
第一种触发的情况
```java
case LCMP:            // Compare long
case IF_ACMPEQ:		  // Branch if reference comparison succeeds if and only if value1 = value2
case IF_ACMPNE:
case IF_ICMPNE:       // Branch if int comparison succeeds
case IF_ICMPEQ:
case IF_ICMPGT:
case IF_ICMPLE:
case IF_ICMPLT:
case IF_ICMPGE:
    checkForSelfOperation(classContext, location, valueNumberDataflow, "COMPARISON", method, methodGen, sourceFile);
```

第二种触发的情况：
```java
switch (ins.getOpcode()) {
    case INVOKEVIRTUAL:
    case INVOKEINTERFACE:
    	// 如果 methodName, className, superClassName 的 lowercase 包含 “test” break

		boolean booleanComparisonMethod = FindSelfComparison2.booleanComparisonMethod(name);
		// 返回值： “Z" 代表 boolean 类型， ”I“ 代表 int 类型
    	if ((numParameters == 1 || seen == Const.INVOKESTATIC && numParameters == 2) && (booleanComparisonMethod && sig.endsWith(";)Z") || FindSelfComparison2.comparatorMethod(name) && sig.endsWith(";)I"))) {
                    checkForSelfOperation(seen, "COMPARISON");
                }
```
包含的方法名如下，注意 static 用法

```java
static boolean booleanComparisonMethod(String methodName) {
        return "equals".equals(methodName) || "endsWith".equals(methodName) || "startsWith".equals(methodName)
                || "contains".equals(methodName) || "equalsIgnoreCase".equals(methodName);
    }

static boolean comparatorMethod(String methodName) {
    return "compareTo".equals(methodName) || "compareToIgnoreCase".equals(methodName);
}
```

### 我的实现思路
spotbugs 只对 int 和 long 类型的变量发出该警报，但是我们没法知道变量类型。

1. 先判断是否出现大小比较符号或者关键方法名字
2. 分别套用不同的正则表达式提取信息
	- 大小比较符号可以用 SELF COMPUTATION 的正则
	- 方法名用提取 object 和括号内容的正则
3. 假如是方法名，object 名和括号内容是否相等，如否，试着分割括号内容提取参数，参考 EQ_COMPARING_CLASS_NAMES

由于我们无法判断 object 的类型，`DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES` 也会识别 "contains" 方法，然后发出 warning。
也许可以通过 local search 来提高 `DMI_COLLECTIONS_SHOULD_NOT_CONTAIN_THEMSELVES` 的准确性？
[对应 issue](https://github.com/Xiaoven/rbugs/issues/79)

## DLS_DEAD_LOCAL_INCREMENT_IN_RETURN

### 例子
```java
@ExpectWarning("DLS_DEAD_LOCAL_INCREMENT_IN_RETURN")
public int getIntMinus1Bad(String intStr) {
    int i = Integer.parseInt(intStr);
    return i--;
}
```

```java
// 假设下面这些都是局部变量名
return num123$++;  // DLS_DEAD_LOCAL_INCREMENT_IN_RETURN, high
return num123++;  // DLS_DEAD_LOCAL_INCREMENT_IN_RETURN, high
return $num123++;  // DLS_DEAD_LOCAL_INCREMENT_IN_RETURN, low

return arr[i]++;  // no warning, no matter arr is a local var or field

return 2*(i++);  // DLS_DEAD_LOCAL_STORE. No warning if i is a field
return 2*(i++) + i;  // No warning
return i + 2*(i++);  // DLS_DEAD_LOCAL_STORE
```
### SpotBugs 实现思路
它判断 dead increment 的方法好长啊，不好理解
初始为 NORMAL_PRIORITY
```java
...
InstructionHandle next = location.getHandle().getNext();
if (next != null && next.getInstruction() instanceof IRETURN) {
propertySet.addProperty(DeadLocalStoreProperty.DEAD_INCREMENT_IN_RETURN);
...
```
### 我的实现思路
观察到 `++`, `--` 似乎只能用在variable 上，像 `arrayList.get(i)` 是 value，不能直接用自增/减符
1. 只识别最简单的 patterns
    - `return i++;`
    - `return i--;`
2. 难点在于如何判断是否是 local increment，而不是 field increment，可以通过 local search 加强？

### Regex
```regexp
return\s+([\w$]+)(?:\+\+|--)\s*;
```

## NM_BAD_EQUAL

### SpotBugs 实现思路
```java
if (obj.isAbstract()) {
    return;
}
if (obj.isPrivate()) {
    return;
}
        
if ("equal".equals(mName) && "(Ljava/lang/Object;)Z".equals(sig)) {
    bugReporter.reportBug(new BugInstance(this, "NM_BAD_EQUAL", HIGH_PRIORITY).addClassAndMethod(this)
                    .lowerPriorityIfDeprecated());
    return;
}
```

### Regex

```regexp
^[\w\s]*?\bboolean\s+equal\s*\(\s*Object\s+[\w$]+\s*\)
```

## QBA_QUESTIONABLE_BOOLEAN_ASSIGNMENT
This method assigns a literal boolean value (true or false) to a boolean variable inside an **if** or **while** expression. Most probably this was supposed to be a boolean comparison using ==, not an assignment using =.

这样的 variable 一定是布尔类型的。

### Examples


```java
// https://github.com/TouK/sputnik-test/pull/3#discussion_r57453267
    private static void incorrectAssignmentInIfCondition() {
        boolean value = false;
        if (value = false) {
```

下面这个issue的发起者认为它是 FN，我觉得不是，因为它看起来更像是把赋值顺便放在条件语句里做了，并不会影响最终结果。但如果是直接给 variable 赋值就错的很明显了，变成了恒真/假。

```java
// https://github.com/spotbugs/spotbugs/issues/1149
if(b = inKnowledge(g.directGoals)) {

if (scanning = b == true)

if (received = (barrier != null)) {
```

```java
    void tmp(boolean b){
        boolean sum = false;
        if (sum = b){	// 也不会产生 warning
```

### SpotBugs 实现思路
[link](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/QuestionableBooleanAssignment.java#L90)

没看懂
```java
switch (state) {
	...
	case SEEN_ISTORE:
        if (seen == Const.IFEQ || seen == Const.IFNE) {
            bug = new BugInstance(this, "QBA_QUESTIONABLE_BOOLEAN_ASSIGNMENT", HIGH_PRIORITY).addClassAndMethod(this)
                    .addSourceLine(this);
            state = SEEN_IF;
        } else {
            state = SEEN_NOTHING;
        }
        break;
    ...
```

### 我的实现思路
1. 提取 `if` 和 `while` 括号里的内容
2. 判断是否有 `var = true` 或 `var = false`

### Regex
```regexp
\b(?:if|while)\s*(?P<aux>\(((?:[^()]++|(?&aux))*)\))
\b[\w$]+\s*=\s*(?:true|false)\b
```

## DMI_BAD_MONTH

### Examples
```java
// https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugsTestCases/src/java/bugPatterns/DMI_BAD_MONTH.java
@ExpectWarning("DMI_BAD_MONTH")
void bug(Date date) {
    date.setMonth(12);
}

@DesireWarning("DMI_BAD_MONTH")  // 其实没有 warning
void bug2(Date date) {
    boolean b = date.getMonth() == 12;
}

// spotbugs 没有检查两个参数的重载
calendarInstance.set(Calendar.MONTH, Calendar.SEPTEMBER)
calendarInstance.set(Calendar.MONTH, 12)
// spotbugs 只检查三个参数以上的重载
cal.set(2021, 12, 10);

Calendar c = new GregorianCalendar(2020, 12, 1);
```
### SpotBugs 实现思路
[link](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindPuzzlers.java#L416)

它检查了 4 个类的用法：

1. "java/util/Date" 或 "java/sql/Date" 的 "setMonth" 方法，它的 signature 为 "(I)V"，即参数类型为 int 返回值类型为 void。
    ```java
        // java.util.Date (sql 的 Date 继承了 util 中的 Date)
        * @param   month   the month value between 0-11.
        * @see     java.util.Calendar
        * @deprecated As of JDK version 1.1,
        * replaced by <code>Calendar.set(Calendar.MONTH, int month)</code>.
        */
    ```
2. "java/util/Calendar" 的  "set" 方法
    - spotbugs 没有检查的重载 
      - `public void set(int field, int value)`
    - spotbugs 只检查三个参数以上的重载
        - `public final void set(int year, int month, int date)`
        - `public final void set(int year, int month, int date, int hourOfDay, int minute)`
        - `public final void set(int year, int month, int date, int hourOfDay, int minute,
          int second)`
3. "java/util/GregorianCalendar" 的 constructor
    - `GregorianCalendar(int year, int month, int dayOfMonth)`
    - `GregorianCalendar(int year, int month, int dayOfMonth, int hourOfDay, int minute)`
    - `GregorianCalendar(int year, int month, int dayOfMonth, int hourOfDay, int minute, int second)`
    
上述 moth 的值范围为 0-11

### 我的实现思路
1. 对于 `Date` 类可以识别方法名 `setMonth`, 提取括号内的数字，判断是否合法
2. 对于 `Calendar` 类，暂且先识别方法名 `set`, 提取 object 名字和参数内容
   - 根据逗号分割参数内容，得到参数列表
   - 如果长度为 2， 判断参数内容是否包含 `Calendar.MONTH`, 并提取数字并判断范围 (用正则)
   - 如果长度大于等于 3，判断 object 名字小写是否包含 "calendar" 来辅助判断 object 的类型，提取第二个参数值判断范围
3. 识别 `new GregorianCalendar(...)`, 提取参数列表，判断长度是否至少为 3；提取第二个参数值判断范围

对于 `Calendar` 和 `GregorianCalendar`，最好当 linecontent 缺失后面的部分参数时也能 work


## BSHIFT: Possible bad parsing of shift operation (BSHIFT_WRONG_ADD_PRIORITY)
The code performs an operation like `(x << 8 + y)`. Although this might be correct, probably it was meant to perform `(x << 8) + y`, but shift operation has a lower precedence, so it's actually parsed as `x << (8 + y)`.

### Examples
```java
// no warning
int main(int foo, int var){
  return rst = foo << 32 + var;
}

// 在实践中它没有报错，理论上应该会报错
long main(long foo, long var){
  return foo << 8L + var;


// low
return foo << 16 + bar;
int rst = foo << 9 + var;

int constant = 16;
return foo << constant + var;

// medium
return foo << 8 + var;


// spotbugs 不考虑减法的样子
return foo << 8 - var;



```

### SpotBugs 实现思路
[link](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/FindPuzzlers.java#L365)

1. 如果看到 `Const.IADD` (int add) 且 `getNextOpcode()` 是 `Const.ISHL` 或 `Const.LSHL` (int/long shift left)

2. 排除 `1 << (const + var)` 形式

3. 如果 const 为 32 且是 `Const.ISHL`, 则 ((foo << 32) + var) 是无意义的，但是 (foo << (32 + var)) 再 var 为负数的情况下是有意义的。所以开发者是故意这么写的，此时不报warning。对 `Const.LSHL` 同理。故做如下判断

```java
if (c < 32 || (c < 64 && getNextOpcode() == Const.LSHL)) 
```

4. 根据 const 大小、加号类型还有是否在 `hashCode` 方法的 return 语句里调高 priority
```java
if (c == 8) {
        priority--;
}
if (getPrevOpcode(1) == Const.IAND) {
    priority--;
}
if (getMethodName().equals("hashCode") && getMethodSig().equals("()I")
        && (getCode().getCode()[getNextPC() + 1] & 0xFF) == Const.IRETURN) {
    // commonly observed error is hashCode body like "return foo << 16 + bar;"
    priority = HIGH_PRIORITY;
}
```

### 我的实现思路
我们无法获取 int 或 long 的信息，无法判断 const = 32 时是否应该报 warning

1. 用正则匹配，如果匹配得上，且 const 不为 32 或 64, 报 warning (至少 low priority)。例子 `foo << constant + var;`

2. 提取 const 信息，尝试转为 int，如果小于 64 且不等于 32，进一步判断是否等于 8, 如果是，priority 为 medium


### Regex
```regexp
\b[\w$]+\s*<<\s*([\w$]+)\s*[+-]\s*[\w$]+
```


## RE: “.” or “|” used for regular expression (RE_POSSIBLE_UNINTENDED_PATTERN)

A String function is being invoked and "." or "|" is being passed to a parameter that takes a regular expression as an argument. Is this what you intended? 

### Examples

- `s.replaceAll(".", "/")` will return a String in which every character has been replaced by a '/' character
- `s.split(".")` always returns a zero length array of String
- `"ab|cd".replaceAll("|", "/")` will return "/a/b/|/c/d/"
- `"ab|cd".split("|")` will return array with six (!) elements: [, a, b, |, c, d]

### SpotBugs 实现思路
[link](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/BadSyntaxForRegularExpression.java#L75)

```java
} else if (seen == Const.INVOKEVIRTUAL && "java/lang/String".equals(getClassConstantOperand())
                && "replaceAll".equals(getNameConstantOperand())) {
            sawRegExPattern(1);
            singleDotPatternWouldBeSilly(1, true);
        } else if (seen == Const.INVOKEVIRTUAL && "java/lang/String".equals(getClassConstantOperand())
                && "replaceFirst".equals(getNameConstantOperand())) {
            sawRegExPattern(1);
            singleDotPatternWouldBeSilly(1, false);
        } else if (seen == Const.INVOKEVIRTUAL && "java/lang/String".equals(getClassConstantOperand())
                && "matches".equals(getNameConstantOperand())) {
            sawRegExPattern(0);
            singleDotPatternWouldBeSilly(0, false);
        } else if (seen == Const.INVOKEVIRTUAL && "java/lang/String".equals(getClassConstantOperand())
                && "split".equals(getNameConstantOperand())) {
            sawRegExPattern(0);
            singleDotPatternWouldBeSilly(0, false);
        }
```

 
 它检查 `String` 类的以下四个方法:

- `String replaceAll(String regex, String replacement)`
- `String replaceFirst(String regex, String replacement)`
- `String[]	split(String regex)`
	- `String[]	split(String regex, int limit)`
- `boolean	matches(String regex)`

前两个方法要检查两个参数，后两个方法只检查第一个参数。只有 `replaceAll` 的 ignorePasswordMasking 为 true

```java
// singleDotPatternWouldBeSilly
// 获取第一个参数，判断是否等于 "." 或 "|"
Object value = it.getConstant();
if (!(value instanceof String)) {
    return;
}
String regex = (String) value;
boolean dotIsUsed = ".".equals(regex);
if (!dotIsUsed && !"|".equals(regex)) {
    return;
}
// 如果包含已经可以报 warning 了
int priority = HIGH_PRIORITY;
// 现在 对replaceAll 做 ignorePasswordMasking
if (ignorePasswordMasking && dotIsUsed) {
    priority = NORMAL_PRIORITY;
    OpcodeStack.Item top = stack.getStackItem(0);  // 获取第二个参数
    Object topValue = top.getConstant();
    if (topValue instanceof String) {
        String replacementString = (String) topValue;
        // 如果第二个参数是以下的值，很可能是在做加密操作，没必要报 warning
        if ("x".equals(replacementString.toLowerCase()) || "-".equals(replacementString) || "*".equals(replacementString)
                || " ".equals(replacementString) || "\\*".equals(replacementString)) {
            return;
        }
        // 否则，如果满足以下条件，有问题的可能新也比较低
        if (replacementString.length() == 1 && getMethodName().toLowerCase().indexOf("pass") >= 0) {
            priority = LOW_PRIORITY;
        }
    }
}

```

### 我的实现思路

1. 匹配上述四种方法并提取参数
2. 按照上述流程判断

但是我无法获取它所在的方法名，判断不了方法名是否包含 "pass", 只能省去这个条件

### Regex
```regexp
\.\s*(replaceAll|replaceFirst|split|matches)\s*\(\s*"([.|])\s*"\s*,?([^)]*)
```

## RE: File.separator used for regular expression (RE_CANT_USE_FILE_SEPARATOR_AS_REGULAR_EXPRESSION)
The code here uses `File.separator` where a regular expression is required. This will fail on Windows platforms, where 
the `File.separator` is a backslash, which is interpreted in a regular expression as an escape character. 

Among other options, you can just use `File.separatorChar=='\\' ? "\\\\" : File.separator` instead of `File.separator`.

### Examples
```java
// https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugsTestCases/src/java/bugPatterns/RE_CANT_USE_FILE_SEPARATOR_AS_REGULAR_EXPRESSION.java#L9
any1.replaceAll(File.separator, any2);
Pattern.compile(File.separator, Pattern.DOTALL);
Pattern.compile(File.separator, Pattern.CASE_INSENSITIVE);
```

### Spotbugs' Implementation
[link](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/BadSyntaxForRegularExpression.java#L89)

#### 检查的方法
- `java/util/regex/Pattern`
    - `static Pattern	compile(String regex, int flags)`
    - `static Pattern	compile(String regex)`
    - `static boolean	matches(String regex, CharSequence input)`
- `java/lang/String`
    - `String replaceAll(String regex, String replacement)`
    - `String replaceFirst(String regex, String replacement)`
    - `String[]	split(String regex)`
    - `String[]	split(String regex, int limit)`
    - `boolean	matches(String regex)`
    
#### 判断条件
```java
OpcodeStack.Item it = stack.getStackItem(stackDepth);
if (it.getSpecialKind() == OpcodeStack.Item.FILE_SEPARATOR_STRING && (flags & Pattern.LITERAL) == 0) {
    bugReporter.reportBug(new BugInstance(this, "RE_CANT_USE_FILE_SEPARATOR_AS_REGULAR_EXPRESSION", HIGH_PRIORITY)
            .addClassAndMethod(this).addCalledMethod(this).addSourceLine(this));
    return;
}
```

> - `Pattern.DOTALL` Enables dotall mode. In dotall mode, the expression `.` matches any character, including a line terminator. By default this expression does not match line terminators. Dotall mode can also be enabled via the embedded flag expression `(?s)`. (The s is a mnemonic for "single-line" mode, which is what this is called in Perl.) 
> - `Pattern.LITERAL` Enables literal parsing of the pattern. When this flag is specified then the input string that specifies the pattern is treated as a sequence of literal characters. Metacharacters or escape sequences in the input sequence will be given no special meaning. The flags CASE_INSENSITIVE and UNICODE_CASE retain their impact on matching when used in conjunction with this flag. The other flags become superfluous. There is no embedded flag character for enabling literal parsing.

判断条件为第一个参数为 `File.separator`，且第二个参数不包含 `Pattern.LITERAL`， 它会使输入序列中的元字符或转义序列将没有特殊含义。
只有 `static Pattern	compile(String regex, int flags)` 需要判断 `Pattern.LITERAL`.

### 