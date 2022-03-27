pipeline {
    agent any

    stages {
        stage('TestInit') {
            steps {
                // timestamper ver. 1.17
                // 1.18 以降なら timestamps { } を使える
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        test_init()
                    }
                }
            }
        }

        stage('Execute') {
            steps {
                wrap([$class: 'TimestamperBuildWrapper']) {
                    script {
                        currentResult = execute_test_suite()
                    }
                }
            }
        }
    }
}

def test_init() {
    // 
}

def execute_test_suite() {

    return 'SUCCESS'
}
