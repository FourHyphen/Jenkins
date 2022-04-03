// 前提: Jenkins サーバーに以下システム環境変数を設定し、文字コードを UTF-8 にする
// JAVA_TOOL_OPTIONS: -Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8

def test_suite(String workspace_path, String unique_id) {
    // テスト用に pipeline ブロックを除いたスクリプトファイルを作成
    // 注意点: BOM なしにすること(BOM ありだとスクリプトの最初の行が BOM バイト付きで処理され、しかも load でエラーしないので厄介)
    String test_script_path = "${workspace_path}/${unique_id}_MainJobA.groovy"
    create_script_without_pipeline_block("${workspace_path}/LoadOtherScript/MainJobA.groovy", test_script_path)

    // テスト用のスクリプトを load
    def script_MainJobA = load_script(test_script_path)

    println("g_value1: ${script_MainJobA.g_value1}")    // "g_value1: "
    script_MainJobA.pre_process()
    println("g_value1: ${script_MainJobA.g_value1}")    // "g_value1: processed"

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

def read_file(String file_path, String encoding="UTF8") {
    // いちいち Scripts not permitted to use に対応するのが面倒なのでスクリプト処理
    // return new File(file_path).getText()
    return powershell(returnStdout: true, script: "Get-Content -Encoding ${encoding} ${file_path}")
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
    def matching = /(?m)^return +this(\t| )*\r?\n/
    String script_not_contains_return_this = (!(contents ==~ matching)).toString()

    return """
        \$splited = \"${contents}\".Replace("\r", "").Split("\n")

        # StreamWriter 構築
        \$enc = \$null
        if ("${encoding}".ToLower() -eq "utf-8") {
            # bom なし固定
            \$enc = [System.Text.UTF8Encoding]::new(\$false)
        } else {
            \$enc = [System.Text.Encoding]::GetEncoding("${encoding}")
        }
        \$sw = [System.IO.StreamWriter]::new(\"${file_path}\", \$false, \$enc)

        # 1 行毎に記載することで powershell 用のエスケープを回避
        foreach (\$line in \$splited)
        {
            \$sw.WriteLine(\$line)
        }

        # スクリプトが load 非対応の場合、return this を強制付与
        if (\$${script_not_contains_return_this})
            \$sw.WriteLine("return this")
        }
        \$sw.Close()
    """
}

def load_script(String load_script_path) {
    def script = load(load_script_path)
    println("loaded")
    return script
}

return this
