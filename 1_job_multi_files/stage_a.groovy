// Jenkins デフォルト import
// import jenkins.*
// import jenkins.model.*
// import hudson.*
// import hudson.model.*

import groovy.json.*

// println は何も工夫しないと標準出力に表示されるが、Jenkins は専用の print ストリームを使用するらしい
//  -> 何も工夫しないとただ println を実行してもジョブコンソールログに何も出てこない
// println での出力先を変更するのに以下方法は No such property: out for class: groovy.lang.Binding となった
// import hudson.model.*
// System.out = getBinding().out

// cps 変換のためにシリアライズ化が必要
class InputJson implements Serializable {
    def script = null    // 呼び出し元 Jenkins ジョブ環境
    String name = null
    int age

    // セッタの定義
    // ここで error すれば実質的に read only にできる
    def setName(String name) {
        // クラス外での import では CPS 変換時に Unknown type: IMPORT となった
        // import jenkins.*

        // 以下でも OK, java.lang.Exception: "name" property is read-only となる
        // throw new Exception('"name" property is read-only')

        // この書き方では自クラスを見に行って未定義エラーとなる
        // error('"name" property is read-only')

        // これで OK
        // hudson.AbortException: this error is called by error(). "name" property is read-only
        script.error('this error is called by error(). "name" property is read-only')
    }

    def InputJson(def script, String name, int age){
        this.script = script
        this.name = name
        this.age = age
    }

    def toJson() {
        // クラス外での import groovy.json.* は効いてる
        return new JsonSlurperClassic().parseText(toJsonString())
    }

    String toJsonString() {
        String json = """{
    "name": "${this.name}",
    "age": ${this.age}
}"""

        // echo だと自クラスを見に行って未定義エラーとなる
        // echo('in toJsonString(): return: ')

        // これでジョブコンソールログに出力された
        script.println('in toJsonString(): return: ')
        script.println(json)
        return json
    }
}

InputJson create_input_json(def script, String name, int age){
    return new InputJson(script, name, age)
}

def stage_a(InputJson input_json) {
    println("stage_a.groovy: stage_a()")
    println(input_json.name)
    println(input_json.age)

    println("input_json.toJsonString(): ")
    println(input_json.toJsonString())

    println("input_json.toJson(): ")
    println(input_json.toJson())
}

return this
