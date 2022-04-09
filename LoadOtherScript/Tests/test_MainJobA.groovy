def test_suite(String workspace_path, String unique_id, def common) {
    // common -> common.groovy の load 結果
    // テスト用のスクリプトを load
    def jenkinsfile = common.load_script_edited_for_testing("${workspace_path}/LoadOtherScript/MainJobA.groovy", workspace_path, unique_id)

    def result_test_pre_process = test_pre_process(jenkinsfile, common)

    if (result_test_pre_process) {
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
    if (!common.are_equals(expected: "processed", actual: jenkinsfile.g_value1)) {
        result = false
    }

    common.print_result(result, common.get_method_name())
    return result
}

return this
