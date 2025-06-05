// Jenkins デフォルト import
// import jenkins.*
// import jenkins.model.*
// import hudson.*
// import hudson.model.*

import groovy.json.*

// cps 変換のためにシリアライズ化が必要
class InputJson implements Serializable {
    String name = null
    int age

    // セッタの定義
    // ここで error すれば実質的に read only にできる
    def setName(String name) {
        // クラス外での import では CPS 変換時に Unknown type: IMPORT となった
        // import jenkins.*

        // この書き方では自クラスを見に行って未定義エラーとなる。error() メソッドはどこの空間にあるか？
        // error('"name" property is read-only')

        throw new Exception('"name" property is read-only')
    }

    def InputJson(String name, int age){
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

        println('in toJsonString(): return: ')
        println(json)
        return json
    }
}

InputJson create_input_json(String name, int age){
    return new InputJson(name, age)
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
