def test_suite(String workspace_path, String unique_id) {
    // テスト用に pipeline ブロックを除いたスクリプトファイルを作成
    // (pipeline ブロック残したままだと java.lang.IllegalStateException: Only one pipeline { ... } block can be executed in a single run.)
    String test_script_path = "${workspace_path}/${unique_id}_MainJobA.groovy"
    create_script_without_pipeline_block("${workspace_path}/LoadOtherScript/MainJobA.groovy", test_script_path)

    // テスト用のスクリプトを load
    def script_MainJobA = load_script(test_script_path)

    return true
}

def create_script_without_pipeline_block(String original_path, String create_path) {
    // pipeline ブロックなしのスクリプト本文を作成し、保存する
    println("create_script_without_pipeline_block()")

    String text = read_file(original_path)
    String contents = exclude_pipeline_block(text)
    write_file(create_path, contents)

    println("create: ${create_path}")
}

def read_file(String file_path) {
    // いちいち Scripts not permitted to use に対応するのが面倒なのでスクリプト処理
    // return new File(file_path).getText()
    return powershell(returnStdout: true, script: "Get-Content ${file_path}")
}

def exclude_pipeline_block(String text) {
    // (?m) -> 複数行マッチモード(^ が改行文字直後の行頭にマッチする)
    // (?s) -> DotAll モード(. が改行文字にもマッチする)
    // 行頭の "pipeline {" から、"}" のみの行まで控え目マッチ(CRLF改行対応として改行文字を "\r?\n" で表現)
    def matching = /(?m)(?s)^pipeline *\{.*?\r?\n\}\r?\n/
    def excluded = (text =~ matching)?.replaceAll("")
    println(excluded)
    return excluded
}

def write_file(String file_path, String contents, String encoding="utf8") {
    // いちいち Scripts not permitted to use に対応するのが面倒なのでスクリプト処理
    // new File(file_path).setText(contents)
    String here_document = @"${contents}"@
    powershell(script: "Write-Output ${here_document} | Set-Content -Encoding ${encoding} ${file_path}")
}

def load_script(String load_script_path) {
    def script = load(load_script_path)
    println("loaded")
    return script
}

return this
