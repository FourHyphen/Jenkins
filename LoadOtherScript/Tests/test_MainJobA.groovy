def test_suite(def workspace_path, def unique_id) {
    // テスト用に pipeline ブロックを除いたスクリプトファイルを作成
    // (pipeline ブロック残したままだと java.lang.IllegalStateException: Only one pipeline { ... } block can be executed in a single run.)
    def test_script_path = "${workspace_path}/${unique_id}_MainJobA.groovy"
    create_script_without_pipeline_block("${workspace_path}/LoadOtherScript/MainJobA.groovy", test_script_path)

    // テスト用のスクリプトを load
    script_MainJobA = load_script(test_script_path)

    return true
}

def create_script_without_pipeline_block(def original_path, def create_path) {
    println("create_script_without_pipeline_block()")

    // pipeline ブロックなしのスクリプト本文を作成
    def text = new File(original_path).getText()
    def contents = exclude_pipeline_block(text)

    // pipeline ブロックなしのスクリプトファイルを保存
    new File(create_path).setText(contents)
    println("create: ${create_path}")
}

def exclude_pipeline_block(def text) {
    // (?m) -> 複数行マッチモード(^ が改行文字直後の行頭にマッチする)
    // (?s) -> DotAll モード(. が改行文字にもマッチする)
    // 行頭の "pipeline {" から、"}" のみの行まで控え目マッチ(CRLF改行対応として改行文字を "\r?\n" で表現)
    def matching = /(?m)(?s)^pipeline *\{.*?\r?\n\}\r?\n/
    def excluded = (text =~ matching)?.replaceAll("")
    println(excluded)
    return excluded
}

def load_script(def load_script_path) {
    def script = load load_script_path
    println("loaded")
    return script
}

return this
