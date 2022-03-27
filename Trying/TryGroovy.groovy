import groovy.transform.CompileStatic
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

DO_STAGE = [
    'DO_STAGE_ENV':false,
    'DO_STAGE_ADD':false,
    'DO_STAGE_STRING':false,
    'DO_STAGE_ENUM':false,
    'DO_STAGE_LIST':false,
    'DO_STAGE_DICT':false,
    'DO_STAGE_IF':false,
    'DO_STAGE_CLOSURE':false,
    'DO_STAGE_FOR':false,
    'DO_STAGE_MAP':false,
    'DO_STAGE_REFLECTION':false,
    'DO_STAGE_ANNOTATION':false,
    'DO_STAGE_DATE':false,
    'DO_STAGE_REGEX':true,
    'DO_STAGE_OTHER':false,
    'DUMMY':false    // コピペが楽になるように
]

pipeline {
    agent any

    stages {
        // expression: 中で true 返したときだけ実行
        stage('Env') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_ENV'] } } }
            steps {
                // 変数定義等、あらゆることをするには script ブロックが必要
                script {
                    // stage 名は env に存在しない
                    //  -> 取得例) https://swet.dena.com/entry/2021/01/18/200000
                    // BUILD_DISPLAY_NAME=#56
                    // BUILD_ID=56
                    // BUILD_NUMBER=56
                    // BUILD_TAG=jenkins-TryGroovy-56
                    // BUILD_URL=http://localhost:8080/job/TryGroovy/56/
                    // CI=true
                    // CLASSPATH=
                    // HUDSON_HOME=C:\ProgramData\Jenkins\.jenkins
                    // HUDSON_SERVER_COOKIE=689f8526eb3f0e8e
                    // HUDSON_URL=http://localhost:8080/
                    // JENKINS_HOME=C:\ProgramData\Jenkins\.jenkins
                    // JENKINS_SERVER_COOKIE=689f8526eb3f0e8e
                    // JENKINS_URL=http://localhost:8080/
                    // JOB_BASE_NAME=TryGroovy
                    // JOB_DISPLAY_URL=http://localhost:8080/job/TryGroovy/display/redirect
                    // JOB_NAME=TryGroovy
                    // JOB_URL=http://localhost:8080/job/TryGroovy/
                    // RUN_ARTIFACTS_DISPLAY_URL=http://localhost:8080/job/TryGroovy/56/display/redirect?page=artifacts
                    // RUN_CHANGES_DISPLAY_URL=http://localhost:8080/job/TryGroovy/56/display/redirect?page=changes
                    // RUN_DISPLAY_URL=http://localhost:8080/job/TryGroovy/56/display/redirect
                    // RUN_TESTS_DISPLAY_URL=http://localhost:8080/job/TryGroovy/56/display/redirect?page=tests
                    env.getEnvironment().each {
                        out_console(it.toString())
                    }
                }
            }
        }

        stage('Add') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_ADD'] } } }
            steps { script { out_console(add(1, 2).toString()) } }
        }

        stage('String') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_STRING'] } } }
            steps { script { try_string() } }
        }

        stage('Enum') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_ENUM'] } } }
            steps { script { try_enum() } }
        }

        stage('List') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_LIST'] } } }
            steps { script { try_list() } }
        }

        stage('Dict') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_DICT'] } } }
            steps { script { try_dict() } }
        }

        stage('If') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_IF'] } } }
            steps {
                // timestamper ver. 1.17
                // 1.18 移行なら timestamps { } を使える
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {  try_if() }
                }
            }
        }

        stage('Closure') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_CLOSURE'] } } }
            steps { script { try_closure() } }
        }

        stage('For') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_FOR'] } } }
            steps { script { try_for() } }
        }

        stage('Map') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_MAP'] } } }
            steps { script { try_map() } }
        }

        stage('Reflection') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_REFLECTION'] } } }
            steps { script { try_reflection() } }
        }

        stage('Annotation') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_ANNOTATION'] } } }
            steps { script { try_annotation() } }
        }

        stage('Date') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_DATE'] } } }
            steps { script { try_date() } }
        }

        stage('Regex') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_REGEX'] } } }
            steps { script { try_regex() } }
        }

        stage('Other') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_OTHER'] } } }
            steps { script { try_other() } }
        }
    }
}

def out_console(String str) {
    echo "${str}"
}

def add(int a, int b) {
    return (a + b)
}

def try_string() {
    def str1 = '0123456789'
    def str2 = 'ABCDEFG'

    out_console(str1 + " " + str2)    // 連結
    out_console(str2.toUpperCase() + " " + str2.toLowerCase())
    out_console(str1.replace('012', 'JJJ'))
    out_console(str1.substring(2, 5))    // '234'
    // out_console(str1[2:5])    // 非対応

    out_console(str1.length().toString())

    // '1_000' 表記非対応だった
    out_console(Integer.parseInt('1000').toString())

    for (c in str1) {
        out_console(c)    // 1 文字ずつになった
    }

    def splited = 'AAA BBB CCC'.split(' ')
    out_console(splited[0])
    out_console(splited[1])
    out_console(splited[2])
    // out_console(splited[3])    // java.lang.ArrayIndexOutOfBoundsException
    out_console(splited.join(' / '))    // 'AAA / BBB / CCC'
}

enum Rank {
    BRONZE,
    SILVER,
    GOLD
}

// Java ならできるらしい、Groovy ではそもそも定義の時点でエラーしてる？
// enum RankWithNum {
//     BRONZE(5),
//     SILVER(6),
//     GOLD(7)
// }

def try_enum() {
    Rank b = Rank.BRONZE
    out_console(b.toString())    // 'BRONZE'
    out_console(get_class_name(b))    // 'Rank'
    // out_console((Rank.SILVER).toInteger().toString())        // Rank に toInteger() はないエラー？
    // out_console(Integer.parseInt("2").toString())            // 変換可能
    // out_console(Integer.parseInt(Rank.SILVER).toString())    // 変換不可
}

def try_list() {
    def list1 = ["ABC", 10, 'DEF', 20]
    for (elem in list1) {
        out_console(elem.toString())
    }

    // append
    out_console(list1[3] + " / " + list1[-1])    // '20 / 20'
    list1.add('GHI')
    out_console(list1[4] + " / " + list1[-1])    // 'GHI / GHI'

    out_console(list1.indexOf('DEF').toString())    // 2

    def list2 = [30, 40, 50]
    def list3 = list1 + list2        // リスト連結しても当然元のは変わらない
    out_console(list1.toString())
    out_console(list2.toString())
    out_console(list3.toString())

    def list4 = list3 - ['ABC', 40]
    out_console(list4.toString())    // '[10, DEF, 20, GHI, 30, 50]'

    // こんな書き方もあった
    list4.each {
        elem -> out_console(elem.toString())
    }

    // メソッド参照: [Java] 定義済みメソッドを引数なしで呼び出すこと
    // list4.each {
    //     out_console    // WorkflowScript クラスを探しに行った
    // }

    // https://koji-k.github.io/groovy-tutorial/collection/list.html#collect
    list5 = (0..10).toList()    // [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    out_console(list5.toString())
    list6 = list5.findAll { it % 2 == 0 }    // [0, 2, 4, 6, 8, 10]
    out_console(list6.toString())
    value = list5.findAll { it % 2 == 0}
                 .inject { sum, it -> sum + it }    // 30 = 0 + 2 + 4 + 6 + 8 + 10
    out_console(value.toString())

    // inject 例) max 取得
    max = list5.inject { now_max, it -> now_max < it ? it : now_max }
    out_console(max.toString())    // 10
}

void try_dict() {
    // こんなんでも OK だった
    def dict1 = [
        3:100,
        'BBB':'aaaaa',
        50:[70, 90]
    ]

    out_console(dict1.toString())    // '[3:100, BBB:aaaaa, 50:[70, 90]]'
    out_console(get_class_name(dict1))    // 'class java.util.LinkedHashMap'

    out_console(dict1.containsKey(3).toString())                // true
    out_console(dict1.containsKey('Not exist').toString())      // false
    out_console(dict1.containsValue('aaaaa').toString())        // true
    out_console(dict1.containsValue('Not exist').toString())    // false

    for (item in dict1) {
        out_console(get_class_name(item))    // class java.util.LinkedHashMap$Entry

        // key & value 取得は以下どっちでも OK
        out_console(item.key.toString() + " : " + item.value.toString())
        out_console(item.getKey().toString() + " : " + item.getValue().toString())
    }

    // これも OK
    dict1.each {
        item -> out_console(item.key.toString() + ' / ' + item.value.toString())
    }

    // これも OK、これがよさそう
    dict1.each {
        key, value -> out_console(key.toString() + ' /// ' + value.toString())
    }

    // java はこれで回せるらしいが、少なくとも Jenkins では NG だった
    // dict1.forEach(
    //     (key, value) -> out_console(key.toString() + ' ##### ' + value.toString())
    // )

    // この書き方は不可
    // for (key, value in dict1) {
    //     out_console(key.toString() + ' ##### ' + value.toString())
    // }
}

def get_class_name(def var) {
    return var.getClass().toString()
}

def get_class_and_package_name(def var) {
    return var.getClass().getCanonicalName()
}

def try_if() {
    def value = 'aaa'

    // if (value == 'a') {
    //     value2 = value
    // } else {
    //     value2 = 'else'
    // }
    value2 = value == 'a' ?: 'else'
    out_console(value2)

    // https://koji-k.github.io/groovy-tutorial/null-safe/index.html
    // Nullable / Null safe
    String str = null;
    out_console(str?.toString() ?: "str is null")    // str is null が出てきた

    str = "test"
    out_console(str?.toString() ?: "str is null")    // test が出てきた
}

def try_closure() {
    def list1 = (0..5).toList()    // toList() がないと range ？になる
    // out_console(get_class_name(list1))

    // クロージャの定義は Fluent Python のと同じ
    // -> 関数内部で参照される非グローバル変数に状態を保持できる lambda
    // (Python のは FluentPython/chapter7_decorator_closer.py 参照)

    // closure は同じ領域で宣言しないと参照できない？
    // (↓をグローバル領域に書いても参照できなかった)
    Closure doubled = { it * 2 }
    // 以下 2 つが同じ処理 <-> .collect { doubled } は Closure そのものが要素になった
    out_console(list1.collect(doubled).toString())
    out_console(list1.collect { doubled(it) }.toString())

    // クロージャの合成 -> 狙い通りにできない...
    // Closure out = { out_console(it.toString()) }
    // Closure doubled_out = doubled >> out
    // // list1.each { out(it) }    // これはできてる
    // // list1.each { doubled_out(it) }    // これはできない
    // list2 = list1.collect(doubled_out)    // これもできない？
    // out_console(get_class_name(list2))
    // out_console(list2.toString())    // list2 は doubled 適用後でできてる

    // Closure add_three = { it + 3 }
    // Closure doubled_add_three = doubled >> add_three
    // list3 = doubled_add_three(list1)
    // out_console(list3.toString())    // [0, 1, 2, 3, 4, 5, 0, 1, 2, 3, 4, 5]
}

def try_for() {
    // def list1 = (5..10).toList()

    // Java: 拡張 for 文 -> Groovy は in しか使えない
    // for (num : list1) {
    //     out_console(num.toString())
    // }
}

def try_map() {
    Map<String, Integer> map = new HashMap<>()
    map['one'] = 1    // Java はわからんが Groovy なら通る
    map['two'] = 2

    // out_console(map.toString())
    out_console(map.keySet().toString())
    out_console(map.values().toString())
    out_console(map.size().toString())
    map.each {
        key, value -> out_console("key: ${key} / value: ${value}")
    }
}

def try_reflection() {

}

@CompileStatic
// @TypeChecked
Integer try_annotation() {
    // TypeChecked 効いてない、実行時エラーになった
    // out_console(not_exist.toString())
    // TypeChecked 効いてない、エラーしなかった
    // return "string"

    // CompileStatic 効いてない
    // out_console(not_exist.toString())
    // return "string"
}

def try_date() {
    // 現在時刻
    def date = LocalDateTime.now()
    println(date.format(DateTimeFormatter.ofPattern('yyyy/MM/dd HH:mm:ss.SSS')))

    // 文字列の日付変換
    String str = '2022/03/19 12:34:56'
    date = LocalDateTime.parse(str, DateTimeFormatter.ofPattern('yyyy/MM/dd HH:mm:ss'))
    println(date.toString())

    // 日付の演算
    println(date.plusDays(10).toString())
}

def try_regex() {
    def text = 'aaa0 bbb ccccc bbbaaa aaa1'
    def matching = (text =~ /\baaa[0-9]\b/)    // 戻り値: class java.util.regex.Matcher
    // class java.util.regex.Matcher
    //     public java.util.regex.Matcher     java.util.regex.Matcher.appendReplacement(java.lang.StringBuffer,java.lang.String)
    //     public java.lang.StringBuffer      java.util.regex.Matcher.appendTail(java.lang.StringBuffer)
    //     public int                         java.util.regex.Matcher.end()
    //     public int                         java.util.regex.Matcher.end(int)
    //     public int                         java.util.regex.Matcher.end(java.lang.String)
    //     public boolean                     java.util.regex.Matcher.find()
    //     public boolean                     java.util.regex.Matcher.find(int)
    //     public java.lang.String            java.util.regex.Matcher.group()
    //     public java.lang.String            java.util.regex.Matcher.group(int)
    //     public java.lang.String            java.util.regex.Matcher.group(java.lang.String)
    //     public int                         java.util.regex.Matcher.groupCount()
    //     public boolean                     java.util.regex.Matcher.hasAnchoringBounds()
    //     public boolean                     java.util.regex.Matcher.hasTransparentBounds()
    //     public boolean                     java.util.regex.Matcher.hitEnd()
    //     public boolean                     java.util.regex.Matcher.lookingAt()
    //     public boolean                     java.util.regex.Matcher.matches()
    //     public java.util.regex.Pattern     java.util.regex.Matcher.pattern()
    //     public static java.lang.String     java.util.regex.Matcher.quoteReplacement(java.lang.String)
    //     public java.util.regex.Matcher     java.util.regex.Matcher.region(int,int)
    //     public int                         java.util.regex.Matcher.regionEnd()
    //     public int                         java.util.regex.Matcher.regionStart()
    //     public java.lang.String            java.util.regex.Matcher.replaceAll(java.lang.String)
    //     public java.lang.String            java.util.regex.Matcher.replaceFirst(java.lang.String)
    //     public boolean                     java.util.regex.Matcher.requireEnd()
    //     public java.util.regex.Matcher     java.util.regex.Matcher.reset()
    //     public java.util.regex.Matcher     java.util.regex.Matcher.reset(java.lang.CharSequence)
    //     public int                         java.util.regex.Matcher.start()
    //     public int                         java.util.regex.Matcher.start(int)
    //     public int                         java.util.regex.Matcher.start(java.lang.String)
    //     public java.util.regex.MatchResult java.util.regex.Matcher.toMatchResult()
    //     public java.lang.String            java.util.regex.Matcher.toString()
    //     public java.util.regex.Matcher     java.util.regex.Matcher.useAnchoringBounds(boolean)
    //     public java.util.regex.Matcher     java.util.regex.Matcher.usePattern(java.util.regex.Pattern)
    //     public java.util.regex.Matcher     java.util.regex.Matcher.useTransparentBounds(boolean)

    matching?.toMatchResult()?.each {
        // it -> class java.lang.String
        println(it.toString())    // aaa0 と aaa1 が出力された
    }

    // 何も気にしない場合、^ は文字列の最初にマッチする(\n直後にはマッチしない)
    text = 'private static string STR = "str"\n'
    text += 'public int Number'
    // フラグ
    // (?s) -> . が \n にもマッチする(DotAll モード)
    // (?m) -> 複数行マッチモード(^ が \n 直後の行頭にマッチする)
    matching = /(?m)^(?:private|public)(?: +static +)? +(\w+) +\w+(?: *= *(["\w]+))?/
    (text =~ matching)?.toMatchResult()?.each {
        // it -> class java.util.ArrayList
        // 1回目: [private static string STR = "str", string, "str"]
        // 2回目: [public int Number, int, null]
        println(it.toString())
    }
}

def try_other() {
    String str = "str"
    out_console((str instanceof String).toString())    // true
}
