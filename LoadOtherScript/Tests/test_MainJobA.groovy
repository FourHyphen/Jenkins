def test_suite(String workspace_path, String unique_id) {
    // テスト用に pipeline ブロックを除いたスクリプトファイルを作成
    // (pipeline ブロック残したままだと java.lang.IllegalStateException: Only one pipeline { ... } block can be executed in a single run.)
    String test_script_path = "${workspace_path}/${unique_id}_MainJobA.groovy"
    create_script_without_pipeline_block("${workspace_path}/LoadOtherScript/MainJobA.groovy", test_script_path)

    // テスト用のスクリプトを load
    def script_MainJobA = load_script(test_script_path)

    println("g_value1: ${script_MainJobA.g_value1}")
    script_MainJobA.pre_process()
    println("g_value1: ${script_MainJobA.g_value1}")

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

def write_file(String file_path, String contents, String encoding="utf-8") {
    // いちいち Scripts not permitted to use に対応するのが面倒なのでスクリプト処理
    // new File(file_path).setText(contents)
    String ps_command = create_ps_command_write_file(file_path, contents, encoding)
    powershell(script: ps_command)
}

def create_ps_command_write_file(String file_path, String contents, String encoding) {
    return """
        \$splited = \"${contents}\".Replace("\r", "").Split("\n")
        \$enc = \$null
        if ("${encoding}".ToLower() -eq "utf-8") {
            # bom なし固定
            \$enc = [System.Text.UTF8Encoding]::new(\$false)
        } else {
            \$enc = [System.Text.Encoding]::GetEncoding("${encoding}")
        }
        \$sw = [System.IO.StreamWriter]::new(\"${file_path}\", \$false, \$enc)

        foreach (\$line in \$splited)
        {
            \$sw.WriteLine(\$line)
        }
        \$sw.WriteLine("return this")
        \$sw.Close()
    """
}

def load_script(String load_script_path) {
    def script = load(load_script_path)
    println("loaded")
    return script
}

return this
