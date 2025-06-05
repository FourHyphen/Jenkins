import groovy.transform.CompileStatic
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter
import org.codehaus.groovy.runtime.StackTraceUtils

DO_STAGE = [
    'DO_STAGE_ENV': false,
    'DO_STAGE_ADD': false,
    'DO_STAGE_STRING': false,
    'DO_STAGE_ENUM': false,
    'DO_STAGE_LIST': false,
    'DO_STAGE_DICT': false,
    'DO_STAGE_IF': false,
    'DO_STAGE_CLOSURE': false,
    'DO_STAGE_FOR': false,
    'DO_STAGE_MAP': false,
    'DO_STAGE_REFLECTION': false,
    'DO_STAGE_ANNOTATION': false,
    'DO_STAGE_DATE': true,
    'DO_STAGE_REGEX': false,
    'DO_STAGE_STACK_TRACE': false,
    'DO_STAGE_PIPELINE_SYNTAX': false,
    'DO_STAGE_REFERENCES': true,
    'DO_STAGE_OTHER': true,
    'DUMMY': false    // コピペが楽になるように
]

pipeline {
    agent any

    // 参考: https://www.jenkins.io/doc/book/pipeline/syntax/
    options { timestamps() }
    parameters {
        // text -> string の複数行
        string(name: 'PERSON', defaultValue: 'Mr Jenkins', description: 'Who should I say hello to?')
        text(name: 'BIOGRAPHY', defaultValue: '', description: 'Enter some information about the person')
        booleanParam(name: 'TOGGLE', defaultValue: true, description: 'Toggle this value')
        choice(name: 'CHOICE', choices: ['One', 'Two', 'Three'], description: 'Pick something')
        password(name: 'PASSWORD', defaultValue: 'SECRET', description: 'Enter a password')
    }

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

        stage('Stack Trace') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_STACK_TRACE'] } } }
            steps { script { try_stack_trace() } }
        }

        stage('Pipeline Syntax') {
            // 参考: https://www.jenkins.io/doc/book/pipeline/syntax/
            when { allOf { expression { return DO_STAGE['DO_STAGE_PIPELINE_SYNTAX'] } } }
            // retry(3) -> 2 回の失敗までリトライ、3 回目の失敗で終了
            //     options { retry(3) }
            //     steps { script { error("stage Option: options retry check") } }

            // timeout() -> タイムアウト条件を満たしたらジョブが ABORTED になる
            // Timeout set to expire in 3 sec
            // Cancelling nested steps due to timeout
            //     options { timeout(time: 3, unit: 'SECONDS') }
            //     steps { script { sleep(10) } }

            // tools -> 自動的にインストールされるもの
            // tools { maven 'apache-maven-3.0.1'  }

            // triggers -> cron トリガーも仕込める
            // triggers { cron('H */4 * * 1-5') }

            // input -> ユーザー入力を待つ
            // input {
            //     message "Should we continue?"
            //     ok "Yes, we should."
            //     submitter "alice,bob"
            //     parameters {
            //         string(name: 'PERSON', defaultValue: 'Mr Jenkins', description: 'Who should I say hello to?')
            //     }
            // }

            // parallel の各 stage は上記の when の実行条件を無視する？
            // parallel {
            //     // failFast true    // 1 つのステージで失敗したら残りを失敗とする設定だが以下エラーとなった
            //     // org.codehaus.groovy.control.MultipleCompilationErrorsException: startup failed
            //     stage ("Parallel A") {
            //         // failFast true でない場合、他ステージが失敗してもこれは最後まで実行された
            //         steps { script { sleep(10) } }
            //     }
            //     stage ("Parallel B") {
            //         steps { script { error("Parallel B Error") } }
            //     }
            // }

            steps { script { println("dummy") } }    // 実行するものが何もないとエラーするので記載
        }

        stage('References') {
            when { allOf { expression { return DO_STAGE['DO_STAGE_REFERENCES'] } } }
            steps { script { references() } }
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
    out_console(list3.toString())    // [ABC, 10, DEF, 20, GHI, 30, 40, 50]

    // リストの引き算が可能
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
    list6 = list5.findAll { it % 2 == 0 }    // [0, 2, 4, 6, 8, 10]
    value = list5.findAll { it % 2 == 0}
                 .inject { sum, it -> sum + it }    // 30 = 0 + 2 + 4 + 6 + 8 + 10

    // inject 例) max 取得
    max = list5.inject { now_max, it -> now_max < it ? it : now_max }    // 10
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
    // int を使おうとすると WorkflowScript: 355: primitive type parameters not allowed here となった
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
int try_annotation() {
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

    // groovy の date 関数は Jenkins では使えない模様
    // println(date(2019, 1, 31))    // hudson.remoting.ProxyException: groovy.lang.MissingMethodException: No signature of method:
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

def try_stack_trace() {
    // String str = "str"
    // out_console((str instanceof String).toString())    // true

    StackTraceElement[] ste = new Throwable().getStackTrace()
    println("ste[0] -----------------------------------------------")
    println(ste[0].getClassName())      // クラス名を取得          WorkflowScript
    println(ste[0].getMethodName())     // メソッド名を取得        try_other
    println(ste[0].getFileName())       // ファイル名を取得        WorkflowScript
    println(ste[0].getLineNumber())     // 行番号を取得            463
    println(ste[0].isNativeMethod())    // nativeメソッドか判定    false
    println(ste[0])                     // スタックトレースの情報を整形して表示
    println("ste[0] -----------------------------------------------")

    println("ste[1] -----------------------------------------------")
    println(ste[1].getMethodName())     // メソッド名を取得        run
    println(ste[1].getLineNumber())     // 行番号を取得            138 = この関数を呼び出した行数
    println("ste[1] -----------------------------------------------")

    // 現在の関数名
    // import org.codehaus.groovy.runtime.StackTraceUtils
    def current = StackTraceUtils.sanitize(new Throwable()).getStackTrace()[0]
    println(current.methodName)    // try_other

    show_method_name()
}

def show_method_name() {
    // 今の関数を取得
    def current =  StackTraceUtils.sanitize(new Throwable()).getStackTrace()[0]
    println("getStackTrace()[0].methodName: ${current.methodName}")    // get_method_name_question

    // この関数を呼び出した関数を取得
    def before =  StackTraceUtils.sanitize(new Throwable()).getStackTrace()[1]
    println("getStackTrace()[1].methodName: ${before.methodName}")    // try_other
}

void references() {
    println("Jenkins ------------------------------------------------------")
    println("自動テスト: https://github.com/jenkinsci/JenkinsPipelineUnit")
    println("Pipeline Syntax: https://www.jenkins.io/doc/book/pipeline/syntax/")
    println("groovy -------------------------------------------------------")
    println("https://docs.oracle.com/cd/E83857_01/paas/app-builder-cloud/visual-builder-groovy/groovy-basics.html")
}

void try_other() {
    println("try_other()")
    // nvl() -> 使えないっぽい
    // String test = null
    // println(nvl(test, "val 'test' is null."))    // java.lang.NoSuchMethodError: No such DSL method 'nvl'
    // import java.lang.Object しても Strings がないと言われた
    // println(Strings.nvl(test, "val 'test' is null."))


}
