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

    def text = new File(original_path).text
    def contents = exclude_pipeline_block(text)

    println("create: ${create_path}")
}

def exclude_pipeline_block(def text) {
    // (?s) -> . が \n にもマッチする(DotAll モード)
    // (?m) -> 複数行マッチモード(^ が \n 直後の行頭にマッチする)
    // 行頭の pipeline { から、\n}\n つまり } のみの行まで控え目マッチ
    def matching = /(?sm)^pipeline *{.*?\n}\n/
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
