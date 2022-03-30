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
                        currentResult = execute_test_suite(WORKSPACE, "${now}_${BUILD_ID}")
                    }
                }
            }
        }
    }
}

def test_init(String workspace_path) {
    // def result = powershell returnStdout: true, script: "<powershell command>"
    powershell("ls ${workspace_path}")
}

def execute_test_suite(String workspace_path, String unique_id) {
    def test_MainJobA = load("${workspace_path}/LoadOtherScript/Tests/test_MainJobA.groovy")

    def result_test_MainJobA = test_MainJobA.test_suite(workspace_path, unique_id)

    if (result_test_MainJobA) {
        return 'SUCCESS'
    } else {
        return 'FAILURE'
    }
}
