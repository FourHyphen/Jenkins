def test_suite(String workspace_path, String unique_id, def common) {
    // common -> common.groovy の load 結果
    // テスト用のスクリプトを load
    def jenkinsfile = common.load_script_edited_for_testing("${workspace_path}/LoadOtherScript/MainJobA.groovy", workspace_path, unique_id)

    println("g_value1: ${jenkinsfile.g_value1}")    // "g_value1: "
    jenkinsfile.pre_process()
    println("g_value1: ${jenkinsfile.g_value1}")    // "g_value1: processed"

    return true
}

return this
