def test_suite(String workspace_path, String unique_id, def common) {
    // common -> common.groovy の load 結果
    // テスト用のスクリプトを load
    def jenkinsfile = common.load_script_edited_for_testing("${workspace_path}/LoadOtherScript/MainJobA.groovy", workspace_path, unique_id)

    def result_test_pre_process = test_pre_process(jenkinsfile, common)
    def result_test_clone_fake = test_clone_fake(jenkinsfile, common)

    if (result_test_pre_process && result_test_clone_fake) {
        return true
    } else {
        return false
    }
}

def test_pre_process(def jenkinsfile, def common) {
    // 実行
    jenkinsfile.pre_process()

    // 事後条件
    def result = true
    // Jenkins ではこの呼び方は NG だった
    // if (!common.are_equals(expected: "processed", actual: jenkinsfile.g_value1)) {
    if (!common.are_equals("processed", jenkinsfile.g_value1)) {
        result = false
    }

    common.print_result(result, "test_pre_process")
    return result
}

def test_clone_fake(def jenkinsfile, def common) {
    def result = true

    jenkinsfile.clone_fake("value")
    def log = common.get_current_log(20)
    println(log.getClass().toString())
    println(log)
    if (!common.is_contains(log, '''$"`'|%.:+=!?<>&@''')) {
        result = false
    }

    common.print_result(result, "test_clone_fake")
    return result
}

return this
