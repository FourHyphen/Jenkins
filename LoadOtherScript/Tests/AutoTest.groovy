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
                        currentResult = execute_test_suite(WORKSPACE)
                    }
                }
            }
        }
    }
}

def test_init(def workspace_path) {
    // def result = powershell returnStdout: true, script: "<powershell command>"
    powershell "ls ${workspace_path}"
}

def execute_test_suite(def workspace_path) {
    test_MainJobA = load "${workspace_path}/LoadOtherScript/Tests/test_MainJobA.groovy"

    def result_test_MainJobA = test_MainJobA.test_suite()

    if (result_test_MainJobA) {
        return 'SUCCESS'
    } else {
        return 'FAILURE'
    }
}
