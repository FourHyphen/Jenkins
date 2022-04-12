import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

pipeline {
    agent any

    stages {
        stage('TestInit') {
            steps {
                // timestamper ver. 1.17
                // 1.18 以降なら timestamps { } を使える
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        test_init(WORKSPACE)
                    }
                }
            }
        }

        stage('Execute') {
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        def date = LocalDateTime.now()
                        def now = date.format(DateTimeFormatter.ofPattern('yyyyMMdd_HHmmss'))
                        if (!execute_test_suite(TEST_BRANCH_OR_COMMIT, WORKSPACE, "${now}_${BUILD_ID}")) {
                            error("test failed")
                        }
                    }
                }
            }
        }
    }

    post {
        // 失敗したときは環境確認のためにワークスペースをそのまま残す
        success {
            deleteDir()
        }
    }
}

def test_init(String workspace_path) {
    // def result = powershell returnStdout: true, script: "<powershell command>"
    powershell("ls ${workspace_path}")
}

def execute_test_suite(String branch_or_commit, String workspace_path, String unique_id) {
    def test_MainJobA = load("${workspace_path}/LoadOtherScript/Tests/test_MainJobA.groovy")
    def common = load("${workspace_path}/LoadOtherScript/Tests/common.groovy")

    def result_test_MainJobA = test_MainJobA.test_suite(branch_or_commit, workspace_path, unique_id, common)

    if (result_test_MainJobA) {
        return true
    } else {
        return false
    }
}
