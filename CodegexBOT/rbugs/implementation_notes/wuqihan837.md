## STCAL: Static DateFormat（STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE）
[简要描述](https://spotbugs.readthedocs.io/en/stable/bugDescriptions.html#stcal-static-dateformat-stcal-static-simple-date-format-instance):
As the JavaDoc states, DateFormats are inherently unsafe for multithreaded use. 
### Regex
```regexp
(\w*\s*)static\s+(?:final){0,1}\s*(DateFormat|SimpleDateFormat|Calendar|GregorianCalendar)\s+(\w*)
```
### Examples
```java
static final SimpleDateFormat d;
static java.text.DateFormat d; 
static DateFormat d = null;
static SimpleDateFormat d = new SimpleDateFormat();
```
### 实现思路
1. [spotbugs 实现思路](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/StaticCalendarDetector.java#L196): 
```java
/**
 * Checks if the visited field is of type {@link java.util.Calendar} or
 * {@link java.text.DateFormat} or a subclass of either one. If so and the
 * field is static and non-private it is suspicious and will be reported.
 */
```
2. 我的实现思路： 
	- 由于我们不方便获取变量类型信息，我们可以直接匹配 Field 的声明语句是否类似于 `public static DateFormat d`
	- 正则表达式会提取权限修饰符、类名和变量名，如果是 `private` field 则跳过，否则判断类名是 DateFormat 还是 Calendar
	- 根据 Javadoc , [DateFormat](https://docs.oracle.com/javase/8/docs/api/java/text/DateFormat.html) 的 Direct Known Subclasses 只有 `SimpleDateFormat` 类，故只匹配这两种类型，先不考虑自定义的 DateFormat 的子类; 同样，[Calendar](https://docs.oracle.com/javase/8/docs/api/java/util/Calendar.html) 的 Direct Known Subclasses 只有 `GregorianCalendar`.
## STCAL: Static Calendar field (STCAL_STATIC_CALENDAR_INSTANCE)
### Regex
```regexp
(\w*\s*)static\s*(?:final)?\s+(DateFormat|SimpleDateFormat|Calendar|GregorianCalendar)\s+(\w*)\s*[;=]
```
### Examples
### 实现思路
见 STCAL_STATIC_SIMPLE_DATE_FORMAT_INSTANCE

## Se: The readResolve method must not be declared as a static method (SE_READ_RESOLVE_IS_STATIC)
简要描述：为使readResolve方法得到序列化机制的识别，不能作为一个静态方法来声明。

### Regex
```regexp
((?:static|final|\s)*)\s+([^\s]+)\s+readResolve\s*\(\s*\)\s+throws\s+ObjectStreamException
```
### Examples
```java
private static Object readResolve() throws ObjectStreamException 
static Object readResolve() throws ObjectStreamException
public Object readResolve() throws ObjectStreamException
public static final Object readResolve() throws ObjectStreamException
```
### 实现思路
[Spotbugs](https://github.com/spotbugs/spotbugs/blob/07bf864b83083c467e29f1b2de58a2cf5aa5c0d6/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/SerializableIdiom.java)
中的思路是先检测方法名是否为readResolve 且当前 class 是 serializable，如果是，则检查返回值类型是否是 `java.lang.Object` 类型，然后才
检测是否有static修饰词，如果有，则触发该pattern。

我的实现思路为：

1. 我们无法获取 class 是否是 serializable，故将默认 priority 从 high 降为 normal，且假设程序员只在 serializable class 中重写 readResolve 方法

2. 由于 `final` 和 `static` 出现顺序可变，故用提取 `((?:static|final|\s)*)` 后，对该字符串进行 split， 判断 static 是否在其中



## Se: Method must be private in order for serialization to work
简要描述：serialization: object -> byte stream 
相关方法：
private void writeObject(ObjectOutputStream oos) throws Exception
private void readObject(ObjectInputStream ois) throws Exception
这两个方法必须是private的, 否则会被 silently ignored by the serialization/deserialization API
### Regex
```regexp
(private)?\s*void\s*(?:writeObject|readObject)\((?:ObjectOutputStream|ObjectInputStream)\s*(?:oos|ois)\s*\)\s*throws\s*Exception
```
### Examples
```java
public void writeObject(ObjectOutputStream oos) throws Exception
public void readObject(ObjectInputStream ois) throws Exception
private void readObject(ObjectInputStream ois) throws Exception
private void writeObject(ObjectOutputStream oos) throws Exception
```
### Spotbugs 实现
[link](https://github.com/spotbugs/spotbugs/blob/a6f9acb2932b54f5b70ea8bc206afb552321a222/spotbugs/src/main/java/edu/umd/cs/findbugs/detect/SerializableIdiom.java#L486)

```java
        } else if ("readObject".equals(getMethodName()) && "(Ljava/io/ObjectInputStream;)V".equals(getMethodSig())
                && isSerializable) {
            sawReadObject = true;
            if (!obj.isPrivate()) {
                bugReporter.reportBug(new BugInstance(this, "SE_METHOD_MUST_BE_PRIVATE", isExternalizable ? NORMAL_PRIORITY : HIGH_PRIORITY)
                        .addClassAndMethod(this));
            }

        } else if ("readObjectNoData".equals(getMethodName()) && "()V".equals(getMethodSig()) && isSerializable) {

            if (!obj.isPrivate()) {
                bugReporter.reportBug(new BugInstance(this, "SE_METHOD_MUST_BE_PRIVATE", isExternalizable ? NORMAL_PRIORITY : HIGH_PRIORITY)
                        .addClassAndMethod(this));
            }

        } else if ("writeObject".equals(getMethodName()) && "(Ljava/io/ObjectOutputStream;)V".equals(getMethodSig())
                && isSerializable) {
            sawWriteObject = true;
            if (!obj.isPrivate()) {
                bugReporter.reportBug(new BugInstance(this, "SE_METHOD_MUST_BE_PRIVATE", isExternalizable ? NORMAL_PRIORITY : HIGH_PRIORITY)
                        .addClassAndMethod(this));
            }
        }
```

涉及到的方法的官方定义
```java
 private void writeObject(java.io.ObjectOutputStream out) throws IOException  // throws Exception 也可以，否则会 build failed
 private void readObject(java.io.ObjectInputStream in) throws IOException, ClassNotFoundException;
 private void readObjectNoData() throws ObjectStreamException;
```

1. `isSerializable`
2. `isExternalizable`

```java
// Does this class directly implement Serializable?
    String[] interface_names = obj.getInterfaceNames();
    for (String interface_name : interface_names) {
        if ("java.io.Externalizable".equals(interface_name)) {
            directlyImplementsExternalizable = true;
            isExternalizable = true;
        } else if ("java.io.Serializable".equals(interface_name)) {
            implementsSerializableDirectly = true;
            isSerializable = true;
            break;}}

    // Does this class indirectly implement Serializable?  这个我们做不到
    if (!isSerializable) {
        if (Subtypes2.instanceOf(obj, "java.io.Externalizable")) { isExternalizable = true; }
        if (Subtypes2.instanceOf(obj, "java.io.Serializable")) { isSerializable = true; }}
```


### 实现思路
1. 检查方法名是否为 `readObject`，返回值类型是否为 `void`，且参数列表是否只有一个 `ObjectInputStream` 类型的参数. 由于三个方法的参数类型都不一样，所以我们用正则提取方法名和参数列表的内容，再一一对应判断。
2. TODO: 增加 local search 和 global search 来辅助判断该 class 是否直接实现了 Serializable 接口 (无法判断是否是间接实现)
3. 检查是否是 private



