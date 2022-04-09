// 前提: Jenkins サーバーの文字コードが SJIS である
// UTF8 に変更する場合、BOM なしにすること(BOM ありだとスクリプトの最初の行が BOM バイト付きで処理され、しかも load でエラーしないので厄介)

def load_script_edited_for_testing(String test_script_path, String workspace_path, String unique_id) {
    // テスト用に pipeline ブロックを除いたスクリプトファイルを作成
    String script_edited_for_testing_path = "${workspace_path}/${unique_id}_MainJobA.groovy"
    create_script_edited_for_testing(test_script_path, script_edited_for_testing_path)

    // テスト用のスクリプトを load
    return load_script(script_edited_for_testing_path)
}

def create_script_edited_for_testing(String original_path, String create_path) {
    // テスト用に pipeline ブロックなし＆ return this ありのスクリプト本文を作成し、保存する
    println("create_script_edited_for_testing()")

    String text = read_file(original_path)
    String contents = exclude_pipeline_block(text)
    contents = add_return_this(contents)
    write_file(create_path, contents)

    println("create: ${create_path}")
}

def read_file(String file_path) {
    // いちいち Scripts not permitted to use に対応するのが面倒なのでスクリプト処理
    // return new File(file_path).getText()
    try {
        return read_file_linux(file_path)
    } catch (Exception e){
        return read_file_windows(file_path)
    }
}

def read_file_linux(String file_path) {
    return sh(returnStdout: true, script: "cat ${file_path}")
}

def read_file_windows(String file_path) {
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

def add_return_this(String contents) {
    // return this が存在しない場合、末尾に return this を追加する
    def ret = contents

    // ==~ 演算子は文字列の全てが正規表現にマッチする場合に初めて true になるので =~ で代替
    if (!(contents =~ /(?m)^return +this\r?\n/)) {
        ret += "\nreturn this\n"
    }

    return ret
}

def write_file(String file_path, String contents) {
    // いちいち Scripts not permitted to use に対応するのが面倒なのでスクリプト処理
    // new File(file_path).setText(contents)
    try {
        write_file_linux(file_path, contents)
    } catch (Exception e) {
        write_file_windows(file_path, contents)
    }
}

def write_file_linux(String file_path, String contents) {
    String sh_command = create_sh_command_write_file(file_path, contents)
    sh(script: sh_command)
}

def create_sh_command_write_file(String file_path, String contents) {
    String tmp_name = "tmp.groovy"
    String sh_command = """
    echo "{$contents}" > ${tmp_name}
    iconv -t SJIS ${tmp_name} > ${file_path}
    rm ${tmp_name}
    """
}

def write_file_windows(String file_path, String contents) {
    String ps_command = create_ps_command_write_file(file_path, contents)
    powershell(script: ps_command)
}

def create_ps_command_write_file(String file_path, String contents) {
    return """
        \$splited = \"${contents}\".Replace("\r", "").Split("\n")

        # StreamWriter 構築
        \$enc = [System.Text.Encoding]::GetEncoding("SJIS")
        \$sw = [System.IO.StreamWriter]::new(\"${file_path}\", \$false, \$enc)

        # 1 行毎に記載することで powershell 用のエスケープを回避
        foreach (\$line in \$splited)
        {
            \$sw.WriteLine(\$line)
        }

        \$sw.Close()
    """
}

def load_script(String load_script_path) {
    def script = load(load_script_path)
    println("loaded")
    return script
}

def are_equals(def expected, def actual) {
    if (expected == actual) {
        return true
    }

    println("check NG...  expected: ${expected} / actual: ${actual}")
    return false
}

def print_result(Boolean result, String method_name) {
    String res = result ? "OK" : "NG"
    println("${method_name}...${res}")
}

return this
