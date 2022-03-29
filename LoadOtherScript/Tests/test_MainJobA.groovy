def test_suite(def workspace_path, def unique_id) {
    // テスト用に pipeline ブロックを除いたスクリプトファイルを作成
    def test_script_path = "${workspace_path}/${unique_id}_MainJobA.groovy"
    create_script_without_pipeline_block("${workspace_path}/LoadOtherScript/MainJobA.groovy", test_script_path)

    // テスト用のスクリプトを load
    script_MainJobA = load_script(test_script_path)

    return true
}

def create_script_without_pipeline_block(def original_path, def create_path) {
    println("create_script_without_pipeline_block()")
    println("create: ${create_path}")
}

def load_script(def load_script_path) {
    def script = load load_script_path
    println("loaded")
    return script
}

return this
